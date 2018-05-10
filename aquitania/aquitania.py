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

09/05/2018 - I've added Aquitania to github, on its final repository. I am currently working on a ArgumentParser and I
will make it pip installable soon.

10/05/2018 - Changed name from GeneralManager to Aquitania.
"""
import cProfile
import datetime
import importlib
import re

from aquitania.brains.brains_manager import BrainsManager
from aquitania.brains.models.random_forest import RandomForestClf
from aquitania.data_processing.util import generate_folder, clean_indicator_data, clean_ai_data
from aquitania.data_source.broker.broker_selection import select_broker
from aquitania.execution.live_management.live_environment import LiveEnvironment
from aquitania.indicator.management.indicator_manager import *
from aquitania.liquidation.build_exit import BuildExit
from aquitania.resources.no_deamon_pool import MyPool
import _pickle
import aquitania.resources.references as ref
import argparse

# TODO create architecture to make indicator managers talk with themselves. Use cross-security output, correlations, etc
from aquitania.strategies.example_strategy import ExampleStrategy


class Aquitania:
    """
    This class starts the indicators and load them with data:
        1. Download all necessary historic data.
        2. Load the historic data
        3. Run a simulation through the historic data
        4. Create exit points (according to rules set by humans on a Strategy class)
        5. Create an AI strategy
        6. Run a Live Feed and trade the AI Strategy on Real Time
    """

    def __init__(self, broker='test', storage='pandas_hdf5', list_of_asset_ids=ref.cur_ordered_by_spread,
                 strategy_=ExampleStrategy(), is_clean=False, start_dt=datetime.datetime(1971, 2, 1)):
        """
        Initializes GeneralManager, which is a class that has methods to download all Candles (historic and live) and
        run them through indicators, as well as to create exit points and an AI strategy.

        :param broker: (str) Broker Name (ex.: 'test, 'oanda', 'fxcm')
        :param storage: (str) Database Name (ex.: 'pandas_hdf5')
        :param list_of_asset_ids: (list of str) Asset ids to be processed
        :param strategy_: Strategy to be used
        :param is_clean: if True will reset all historical data
        :param start_dt: start date for historical simulations
        """

        # Instantiate broker_instance
        self._broker_instance = select_broker(broker, storage)
        self._list_of_asset_ids = list_of_asset_ids
        self._live_feed_status = True
        self._strategy = strategy_
        self._start_date = start_dt

        # Generates data folders if they are non-existent
        for folder in ref.data_folders:
            generate_folder(folder)

        # Cleans data in case it was set to reset stored simulations data
        if is_clean:
            self.clean_data()

    def clean_data(self):
        """
        Clean simulation Data.
        """
        # Cleans data relative to indicators
        clean_indicator_data()

        # Cleans data relative to AI
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

    def run(self, is_complete=True, is_live=True):
        """
        Execute the following steps:
        1. Run multiple process, one for each IndicatorManager, on all the historic data.
        2. Creates exit points for a given strategy if 'is_complete' is True
        3. Creates an automated AI strategy if 'is_complete' is True
        4. Executes strategy on Live Data if 'is_live' is True
        """

        # Instantiates list of IndicatorManagers
        list_of_indicator_managers = self.load_all_indicator_managers()

        if is_complete:
            # Execute exit points creation
            self.run_liquidation()

            # Execute creation of automated AI strategy
            self.run_brains()

        # Run only if it is not a test, and executes the strategy on Live Data
        if is_live:
            le = LiveEnvironment(self._broker_instance, self._strategy, list_of_indicator_managers, True)
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
            be = BuildExit(self._broker_instance, asset_id, signal, 14400)

            # Consolidate Exists Routine (it gets all possible exits and finds the earliest one)
            be.consolidate_exits()

    def run_brains(self):
        """
        Generates an automated AI strategy and evaluates this strategy.
        """

        # Initializes time counter
        time_a = time.time()

        # Initializes object that manages AI Strategy creation
        bm = BrainsManager(self._broker_instance, self._list_of_asset_ids, self._strategy)

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

    :return: ArgParser with following options:
        optional arguments:
          -h, --help           show this help message and exit
          -b, --backtest       Backtest mode
          -bo, --backtestonly  Backtest only mode
          -e, --exits          Build Exits only mode
          -i, --ai             Artificial Intelligence only mode
          -ei, --exitsai       Build Exits and Artificial Intelligence only
          -d, --debug          Debug mode (Single Process)
          -a, --assets         Number of assets
          -s, --source         Data Source name
          -db, --database      DataBase name
          -c, --clean          Deletes all stored data
          -sd, --startdate     The Start Date - format YYYY-MM-DD
          -ed, --enddate       The End Date - format YYYY-MM-DD
          -t, --trade          Trading strategy to be used
    :rtype: argparse.Namespace
    """
    # Creates parser
    parser = argparse.ArgumentParser(description='Running Aquitania')

    # Creates group to select mode that Aquitania will run
    mode = parser.add_mutually_exclusive_group()

    # Mode Selection options
    mode.add_argument('-b', '--backtest', action='store_true', help='Backtest mode')
    mode.add_argument('-bo', '--backtestonly', action='store_true', help='Backtest only mode')
    mode.add_argument('-e', '--exits', action='store_true', help='Build Exits only mode')
    mode.add_argument('-i', '--ai', action='store_true', help='Artificial Intelligence only mode')
    mode.add_argument('-ei', '--exitsai', action='store_true', help='Build Exits and Artificial Intelligence only')
    mode.add_argument('-d', '--debug', action='store_true', help='Debug mode (Single Process)')
    mode.add_argument('-cp', '--cprofile', action='store_true', help='CProfile Code (Evaluate Performance)')

    # Selects number of assets
    parser.add_argument('-a', '--assets', type=int, metavar='', help='Number of assets')

    # Selects DataSource name
    parser.add_argument('-s', '--source', type=str, metavar='', help='Data Source name')

    # Selects DataBase name
    parser.add_argument('-db', '--database', type=str, metavar='', help='DataBase name')

    # Selects if all stored data from simulations should be reseted
    parser.add_argument('-c', '--clean', action='store_true', help='Deletes all stored data')

    # Selects start and end dates
    parser.add_argument("-sd", "--startdate", type=valid_date, metavar='', help="The Start Date - format YYYY-MM-DD")
    parser.add_argument("-ed", "--enddate", type=valid_date, metavar='', help="The End Date - format YYYY-MM-DD")

    # Selects trading strategy
    parser.add_argument('-t', '--trade', type=str, metavar='', help='Trading strategy to be used (CamelCase)')

    # Returns argument parser
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


def select_execution_mode(gm, args):
    """
    Executes the GeneralManager accordingly to what was set in the ArgumentParser.

    :param gm: (GeneralManager) instantiated GeneralManager object
    :param args: (ArgumentParser) instantiated ArgumentParser
    """
    # Backtest mode (runs exits and brains)
    if args.backtest:
        gm.run(True, False)

    # Backtest mode (does NOT run exits and brains)
    elif args.backtestonly:
        gm.run(False, False)

    # Exits only mode
    elif args.exits:
        gm.run_liquidation()

    # Brains only mode
    elif args.ai:
        gm.run_brains()

    # Exits and brains only mode
    elif args.exitsai:
        gm.run_liquidation()
        gm.run_brains()

    # Debug mode (single process and it doesn't run exits and brains)
    elif args.debug:
        gm.debug_single_process()

    # Performance evaluator mode (single process and it doesn't run exits and brains)
    elif args.cprofile:
        cProfile.run('gm.debug_single_process()')

    # Live Environment mode, it runs all the backtests, generate exits and an artificial intelligence strategy.
    else:
        gm.run(True, True)


def get_strategy(strategy_name):
    """
    Class name is camel case.
    Filename is all lower and words are separated by underline('_')
    :param strategy_name:
    :return:
    """
    # Converts Strategy name to file name
    filename = camel_to_underline(strategy_name)

    # Imports and instantiates strategy
    return getattr(importlib.import_module('strategies.{}'.format(filename)), strategy_name)()


def camel_to_underline(name):
    """
    Converts CamelCase to underline. As for example CamelCase --> camel_case.

    :param name: (str) Name to be converted
    :return: Converted name in lower caps and underline
    :rtype: str
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


# General Manager - Runs simulations and live feeds from here
if __name__ == '__main__':
    # Gets ArgumentParser settings
    args = arg_parser()

    # Gets broker instance arguments
    broker_ = args.source if args.source is not None else 'oanda'
    storage_ = args.database if args.database is not None else 'pandas_hdf5'

    # Initializes Strategy
    strategy = get_strategy(args.trade if args.database is not None else 'ExampleStrategy')

    # Gets number of assets
    n_assets = args.assets if args.assets is not None else 1

    # Generates list of assets
    asset_list = ref.cur_ordered_by_spread[0:n_assets]

    # Sets backtesting start date
    start_date = args.startdate if args.startdate is not None else datetime.datetime(1971, 4, 1)

    # Set if this will be a new backtest, or if it should use data/states from previous simulations
    clean_data = args.clean

    # Initialize General Manager
    gm = Aquitania(broker_, storage_, asset_list, strategy, clean_data, start_date)

    # Selects execution mode accordingly to the ArgumentParser
    select_execution_mode(gm, args)
