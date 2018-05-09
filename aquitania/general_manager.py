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

This file is the door to Aquitania, it is responsible to run all the necessary code and processes.

It was designed to support multiprocessing both on historic data and on live streams. The logic is basically that each
process is on asset. (This could be improved in the future to work with multi-asset analysis without a lot of effort).

12/04/2018 - I've opened the code to the core of Aquitania, and I have started refactoring the most basic classes to
make it understandable to others.
"""

import datetime

from brains.brains_manager import BrainsManager
from brains.models.random_forest import RandomForestClf
from data_processing.util import generate_folder, clean_indicator_data, clean_ai_data
from data_source.broker.broker_selection import select_broker
from execution.live_management.live_environment import LiveEnvironment
from indicator.management.indicator_manager import *
from liquidation.build_exit import BuildExit
from resources.no_deamon_pool import MyPool
from strategies.example import ExampleStrategy
import _pickle
import resources.references as ref
import argparse


# TODO create architecture to make indicator managers talk with themselves. Use cross-security output, correlations, etc
class GeneralManager:
    """
    This class starts the indicators and load them with data:
        1. Download all necessary historic data.
        2. Load the historic data
        3. Run a simulation through the historic data
        4. Create exit points (according to rules set by humans on a Strategy class)
        5. Create an AI strategy
        6. Run a Live Feed and trade the AI Strategy on Real Time
    """

    def __init__(self, broker, list_of_asset_ids, strategy_, test, start_dt):
        """
        Initializes GeneralManager, which is a class that has methods to download all Candles (historic and live) and
        run them through indicators, as well as to create exit points and an AI strategy.

        :param broker: Object of type 'broker_instance' from 'data_source' module
        :param list_of_asset_ids: (list of str) Asset ids to be processed
        :param strategy_: Strategy to be used
        :param test: if True will only ran backtest and reset all historical data
        :param start_dt: start date for historical simulations
        """

        # Initialize variables
        self._broker_instance = broker
        self._list_of_asset_ids = list_of_asset_ids
        self._live_feed_status = True
        self._strategy = strategy_
        self._is_test = test
        self._start_date = start_dt

        # Generates data folders if they are non-existent
        for folder in ref.data_folders:
            generate_folder(folder)

        # Cleans data in case it is test
        if self._is_test:
            clean_indicator_data()
            clean_ai_data()

    def load_all_indicator_managers(self):
        """
        Multiprocessing method to create a list with all indicator managers (one for each asset) already instantiated
        and that ran across all historic data.

        :return: List of Instantiated IndicatorManagers that ran across all historic data
        :rtype: List of IndicatorManagers
        """

        # Starts multiprocessing to load historic data and run indicators through historic data
        asset_pool = MyPool()
        indicator = asset_pool.map(self.load_indicator_manager, self._list_of_asset_ids)
        asset_pool.close()
        asset_pool.join()
        return indicator

    def load_indicator_manager(self, asset):
        """
        Instantiates IndicatorManager for each asset and loads then with data and generates the necessary
        indicators.

        This was made to be used in a parallel fashion. Each asset is a process.

        :param asset: String that identifies which asset will be processed

        :return: IndicatorManager object with loaded candles and indicators
        :rtype: IndicatorManager
        """

        # Print asset
        print('Running simulation on:', asset)

        # Instantiates IndicatorManager
        indicator_manager = self.instantiates_indicator_manager(asset)

        # Starts time counter
        time_a = time.time()

        # Load historic data and feed it to the indicators
        indicator_manager.update_load_run_data()

        # Calculates elapsed time
        print('Elapsed time to run simulation on ', asset + ':', time.time() - time_a)

        return indicator_manager

    def instantiates_indicator_manager(self, asset_id):
        """
        Instantiates IndicatorManager, searches for a previous saved state to load.

        :param asset_id: Security that IndicatorManager will be instantiated on.
        :return: New or loaded (if available) IndicatorManager
        """

        # Initialize state folder (where IndicatorManager state is saved).
        folder = 'data/state/'

        # Creates folder if it doesn't exist
        generate_folder(folder)

        # Loads IndicatorManager saved state if there is any
        for the_file in os.listdir(folder):
            if asset_id + '.pkl' in the_file:
                with open(folder + asset_id + '.pkl', 'rb') as f:
                    indicator_manager = _pickle.load(f)
                    indicator_manager.hdm.is_san_n_store = True
                    return indicator_manager

        # Instantiates a new IndicatorManager in case it didn't return the function previously
        return IndicatorManager(self._broker_instance, asset_id, self._strategy, self._start_date)

    def run(self):
        """
        Execute the following steps:
        1. Run multiple process, one for each IndicatorManager, on all the historic data.
        2. Creates exit points for a given strategy.
        3. Creates an automated AI strategy
        4. Executes strategy on Live Data if 'self.is_test' is False
        """

        # Instantiates list of IndicatorManagers
        list_of_indicator_managers = self.load_all_indicator_managers()

        # Execute exit points creation
        self.run_liquidation()

        # Execute creation of automated AI strategy
        self.run_brains()

        # Run only if it is not a test, and executes the strategy on Live Data
        if not self._is_test:
            le = LiveEnvironment(broker_instance, self._strategy, list_of_indicator_managers, True)
            le.process_manager()

    def run_liquidation(self):
        """
        Creates exit points as defined in the Strategy at 'self._strategy'.

        Saves exits on 'data/exits'
        """

        for asset_id in self._list_of_asset_ids:
            # Build Exit for a specific asset
            print('Creating exits for security:', asset_id)

            # Gets signal from strategy
            # TODO implement multiple signals and multiple exit points
            signal = self._strategy.signal

            # Generate all possible exits according to possible Exit points
            be = BuildExit(broker_instance, asset_id, signal, 14400)

            # Consolidate Exists Routine (it gets all possible exits and finds the earliest one)
            be.consolidate_exits()

    def run_brains(self):
        """
        Generates an automated AI strategy and evaluates this strategy.
        """

        # Initializes time counter
        time_a = time.time()

        # Initializes object that manages AI Strategy creation
        bm = BrainsManager(broker_instance, self._list_of_asset_ids, self._strategy)

        # Initializes list of AI models that will be used (in case of ensemble)
        strategy_models = RandomForestClf

        # Creates AI Strategy
        bm.run_model(strategy_models)

        # Prints time it took to generate and evaluate Strategy
        print('\n\n----------------------------------------------------------------')
        print('AI Strategy generation took: {} seconds'.format(time.time() - time_a))
        print('----------------------------------------------------------------')

    def debug_single_process(self):
        """
        Don't try to debug a multiprocessing application. It is a big mistake that I've made a few times, there are a
        lot of very weird bugs on those things.

        This method ran the application on a single process and ensures that debug will be very easy and bug free,
        always debug here or using a similar method.
        """
        for asset in self._list_of_asset_ids:
            self.load_indicator_manager(asset)


def arg_parser():
    """
    Generates the arg parser for the main file.

    :return:
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Running Aquitania')

    parser.add_argument('-l', '--live', action='store_true', help='Live Environment mode')
    parser.add_argument('-b', '--backtest', action='store_true', help='Backtest mode')
    parser.add_argument('-bo', '--backtestonly', action='store_true', help='Backtest only mode')
    parser.add_argument('-e', '--exits', action='store_true', help='Build Exits only mode')
    parser.add_argument('-i', '--ai', action='store_true', help='Artificial Intelligence only mode')
    parser.add_argument('-ei', '--exitsai', action='store_true', help='Build Exits and Artificial Intelligence only')

    parser.add_argument('-a', '--assets', type=int, metavar='', help='Number of assets')
    parser.add_argument('-s', '--source', type=str, metavar='', help='Data Source name')
    parser.add_argument('-c', '--clean', action='store_true', help='Deletes all stored data')
    parser.add_argument('-d', '--database', type=str, metavar='', help='Storage name')

    parser.add_argument("-sd", "--startdate", type=valid_date, help="The Start Date - format YYYY-MM-DD")
    parser.add_argument("-ed", "--enddate", type=valid_date, help="The Start Date - format YYYY-MM-DD")

    parser.add_argument('-t', '--trade', type=str, metavar='', help='Trading strategy to be used')

    return parser.parse_args()


def valid_date(s):
    """
    This is a method to check a valid date for the argparse.

    :param s: (str) String that comprises date in format YYYY-MM-DD

    :return: Input date in datetime.datetime format
    :rtype: datetime.datetime
    """
    # Tries converting the date
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")

    # If it fails, raise error
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


# General Manager - Runs simulations and live feeds from here
if __name__ == '__main__':
    # Gets ArgumentParser settings
    args = arg_parser()

    # TODO currently for Aquitania to work perfectly, the computer TimeZone needs to be UTC = 0 | NEED TO FIX THIS
    # Instantiate broker_instance
    broker = args.source if args.source is not None else 'test'
    storage = args.database if args.database is not None else 'pandas_hdf5'

    broker_instance = select_broker(broker, storage)

    # Initializes Strategy
    # TODO make working version of strategy in argparse (needs some kind of selector between all possible strategies)
    strategy = ExampleStrategy()

    # Gets number of assets
    n_assets = args.assets if args.assets is not None else 1

    # Generates list of assets
    asset_list = ref.cur_ordered_by_spread[0:n_assets]

    exits = args.exits
    ai = args.ai

    # Sets backtesting start date
    start_date = args.startdate if args.startdate is not None else datetime.datetime(1971, 4, 1)
    end_date = args.enddate

    # Set if this will be a new backtest, or if it should use data/states from previous simulations
    clean_data = args.clean

    # Initialize General Manager
    gm = GeneralManager(broker_instance, asset_list, strategy, clean_data, start_date)
    gm.run()

    # Run Only Liquidation Routine (comment out gm.run())
    # gm.run_liquidation()

    # Run Only AI Routine (comment out gm.run())
    # gm.run_brains()

    # Debug Routine
    # gm.debug_single_process()

    # Debug Performance Routine - This will print the time each method takes to run
    # cProfile.run('gm.run_sp()')
