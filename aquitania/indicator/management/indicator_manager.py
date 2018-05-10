########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||| #
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||| #
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||| #
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||| #
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||| #
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
########################################################################################################################

"""
.. moduleauthor:: H Roark

The indicator managers holds all the indicator lists for all timestamps and then builds the loaders based on this.

The loaders will be handed to the Feeder.

Intended to be a simple-ish class that grew into: Feeder, IndicatorLoader, and IndicatorDataManager.

21/04/2018 - A very interesting thing to do is to improve architecture to enable the indicators to use each others
output in a fashion that will enable them to leverage cross-instrument analysis. The main issue is that we use a lot of
multiprocessing to run multiple financial instruments, so this will require to work with multiprocessing variable
sharing variables. I had a lot of trouble implementing this before, but a Queue of tuples might work here.
"""
import time
import os

from aquitania.data_processing.util import add_asset_columns_to_df
from aquitania.data_source.feeder import Feeder
from aquitania.data_source.historic_data_manager import HistoricDataManager
from aquitania.indicator.management.indicator_loader import IndicatorLoader
from aquitania.resources.candle import Candle
import aquitania.resources.references as ref
import aquitania.resources.datetimefx as dtfx
import _pickle
import pandas as pd


class IndicatorManager:
    """
    One of the pillars of the Aquitania project, this class is the architect of how a single process in Aquitania should
    work. Each Financial Security (asset) should run contained in a IndicatorManager object.
s   """

    def __init__(self, broker_instance, asset, strategy, start_date):
        """
        Initializes IndicatorManager.

        :param broker_instance: (DataSource) Object derived from AbstractDataSource
        :param asset: (str) Currency that will shape the IndicatorManager
        """
        # Instantiates necessary variables
        self.broker_instance = broker_instance
        self.asset = asset
        self.start_date = start_date
        self.strategy = strategy
        self.output = None

        # Instantiate Loaders
        self.list_of_loaders = self.build_loaders()

        # Instantiates HistoricDataManager
        self.hdm = HistoricDataManager(broker_instance, asset, True)

        # Instantiate Feeder
        self.feeder = Feeder(self.list_of_loaders, asset)

    def update_load_run_data(self):
        """
        This method updates, then loads all the historic data and then run all the indicators through it.

        It is great for generating historic databases of indicators output.
        """
        print('{}Starting to update database for {}.'.format(dtfx.now(), self.asset))

        # Updates historic database (downloads new candles from remote server)
        self.hdm.update_historic_database(q3=None)
        print('{}Database updated. Starting simulations for {}.'.format(dtfx.now(), self.asset))

        # Execute indicators in downloaded database (can select initial date)
        self.load_run_data()
        print('{}Simulations completed for {}.'.format(dtfx.now(), self.asset))

    def load_run_data(self):
        """
        This method loads all the historic data and then run all the indicators through it.
        """

        # TODO implement a select here (will work on HDF5, but might not work on other storage methods)
        df = self.hdm.load_data()

        # Guarantees that 'self.start_date' is instantiated.
        if self.start_date is None:
            self.start_date = df.index[0]

        # TODO implement end_date slice as well
        # Gets Usable DataFrame
        df = df[self.start_date:]

        # Executes DataFrame in batches to be able to save the current state of the IndicatorManager
        for dt in self.feeder.exec_df(df[self.start_date:]):
            print('{}Saving a batch into disk on {}. Last Candle analyzed: {}.'.format(dtfx.now(), self.asset, dt))
            self.start_date = dtfx.next_candle_datetime(dt, 1)  # Order is important here
            self.save()

    def live_feed(self):
        """
        Feeds live Candles to the Feeder which will in turn feed all indicators.

        Transforms a list of Candles into individual Candles to be fed.
        """
        # Gets list of tuples containing Candle values
        candles = self.hdm.get_live_data()

        # Checks if blank Candle values
        if candles is not None:
            # Runs candle processing routine
            self.live_candle_processing(candles)

        # Routine for empty candles object
        else:
            # Sleeps for a while just not to use 100% of CPU
            time.sleep(0.1)

    def live_candle_processing(self, candles):
        """
        Does live processing of candles. It will get a list of tuples and instantiate Candle objects from it.

        :param candles: (list of tuples) Input Candles to be processed (not instantiated yet)
        """
        # Evaluate all incoming Candles
        for candle in candles:
            # Defines asset as string
            asset = ref.currencies_list[candle[1]]

            # Converts processed candle to Candle object
            candle = Candle(0, asset, candle[0], candle[3], candle[4], candle[5], candle[6], candle[7], True)

            # Feeds Candle object to Indicators
            self.feeder.feed(candle)

            # Prints information of live fed Candle
            print(candle)

        # Generates output
        self.output = self.generate_live_output()

    def generate_live_output(self):
        """
        Returns indicators output in form of a pandas DataFrame.

        :return: DataFrame containing indicator output
        :rtype: pandas DataFrame
        """
        # TODO centralize this elsewhere in the codebase, this method is duplicate (probably on AnalyticsLoader)
        # Instantiates new DataFrame
        df = None

        # Get output from all_loaders
        for loader in self.list_of_loaders:
            temp_df = loader.generate_df()

            # Routine for when there is in fact output
            if temp_df is not None:

                # Routine to concatenate timestamps output
                if df is None:
                    df = temp_df
                else:
                    df = pd.concat([df, temp_df], axis=1)

        # Routine to generate columns based on Financial Security
        if df is not None:
            df = add_asset_columns_to_df(df, self.asset)

        return df

    def build_loaders(self):
        """
        This method builds all the loaders.

        One analytics_loader.py is basically all the indicators of a given time stamp that will be fed.

        There is no need to separate between 'is_open' and 'is_closed' indicators in is_load, this implementation was
        done on the 'Loader' class.
        """

        # Initializes Variables
        fi = self.asset
        il = self.strategy.indicator_list

        # TODO correct rest of code base to work well with variable timestamps (specially feeder.py)
        # Creates a list of instantiated IndicatorLoaders
        loader_list = [IndicatorLoader(il[ts], fi, ts, self.broker_instance) for ts in range(len(il))]

        # Returns IndicatorLoaders in a list
        return loader_list

    def save(self):
        """
        Save IndicatorManager into disk.

        This architecture once was much more complex, but only saving the IndicatorManager object into disk (and all its
        attributes that contains all IndicatorLoaders and by consequence all Indicators are sufficient to store
        Aquitania states.
        """
        # Sets file name
        filename = 'data/state/{}.pkl'.format(self.asset)

        # Removes file in case it exists
        if os.path.exists(filename):
            os.remove(filename)

        # Writes state to disk
        # TODO there are better implementations than _pickle (cPickle), messagePack and others. Might check this later.
        with open(filename, 'wb') as f:
            _pickle.dump(self, f)
