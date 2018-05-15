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
"""
import time

import datetime
import numpy as np
import os

from aquitania.execution.live_management.display import *
from aquitania.resources.asset import AssetInfo
from aquitania.execution.order_manager import OrderManager
from aquitania.execution.oracle_manager import OracleManager
import multiprocessing as mp
import _pickle as cPickle


class LiveEnvironment:

    def __init__(self, broker_instance, strategy, list_of_indicator_managers, is_live_observer_feed):
        if not broker_instance.is_live:
            raise NotImplementedError(
                'Selected data source is not implemented to work on a Live Environment. You need to change data sources'
                ', or only use current data source for backtesting.')
        self.broker_instance = broker_instance
        self.l_im = list_of_indicator_managers
        self.list_of_assets = [im.asset for im in self.l_im]
        self.is_live_observer_feed = is_live_observer_feed
        self.currencies_object = AssetInfo(broker_instance, self.list_of_assets)
        self.order_manager = OrderManager(self.broker_instance, self.currencies_object)
        self.strategy = strategy

        # Load Strategy
        oracle = load_oracle(strategy.__class__.__name__)
        self.oracle_manager = OracleManager(oracle, self.order_manager)

    def process_manager(self):
        q1 = mp.Queue()

        p = mp.Process(target=self.live_observer_feed, args=(q1,))
        w = mp.Process(target=self.brains, args=(q1,))
        z = mp.Process(target=self.display)

        # Start all the multiprocessing
        p.start()
        w.start()
        z.start()

        # Wait for the multiprocessing to finish and join all of them.
        p.join()
        w.join()
        z.join()

    def live_observer_feed(self, q1):
        minute = datetime.datetime.now().minute

        while True:
            if minute != datetime.datetime.now().minute:
                minute = datetime.datetime.now().minute
                for observer_manager in self.l_im:
                    observer_manager.live_feed()
                    df = observer_manager.output
                    if df is not None:
                        q1.put(df)
            else:
                time.sleep(1)

    def brains(self, q1):
        while True:
            if not q1.empty():
                df = q1.get()
                if df is not None:
                    if df.shape[0] > 0:
                        # RFC can't deal with Datetime as input to be analyzed
                        df = df.select_dtypes(exclude=np.datetime64)
                        # RFC can't deal with NA values
                        df.dropna(inplace=True, axis=1, how='any')
                        df.apply(self.oracle_manager.consult_oracle, axis=1)
            else:
                time.sleep(1)

    def display(self):
        """

        :return:
        """
        while True:
            # TODO make a big refactor on this and related methods/functions
            os.system('clear')
            disp_title()
            self.disp_live_strategy_performance()
            self.disp_broker_status()
            self.disp_exposure()
            time.sleep(60)

    def disp_live_strategy_performance(self):
        # TODO work on this
        centered_line('CURRENT STRATEGY LIVE PERFORMANCE')
        full_line()
        blank_line()
        indented_line('HISTORIC PERFORMANCE')
        indented_line('MONTHLY PERFORMANCE')
        indented_line('WEEKLY PERFORMANCE')
        blank_line()
        full_line()

    def disp_broker_status(self):
        centered_line('STATUS WITH BROKER {}'.format(self.broker_instance.broker_name.upper()))
        full_line()
        blank_line()
        indented_line('ASSETS BEING TRADED ({} TOTAL):'.format(len(self.list_of_assets)))
        double_indented_line(', '.join(self.list_of_assets))
        blank_line()
        indented_line('WORKING CONNECTION WITH {}:'.format(self.broker_instance.broker_name.upper()))
        indented_line('ACCOUNT BALANCE:        {0:.2f} USD'.format(self.broker_instance.get_account_balance()))
        indented_line('USED MARGIN:            {0:.2f} USD'.format(self.broker_instance.get_used_margin()))
        indented_line('MAX LEVERAGE:           {0:.0f}x'.format(self.broker_instance.account_leverage))
        blank_line()
        full_line()
        centered_line('OPEN_POSITIONS {}'.format(self.broker_instance.broker_name.upper()))
        full_line()
        blank_line()
        list_of_trades = self.broker_instance.get_list_of_trades()
        indented_line('TOTAL OF OPEN POSITIONS: {0:.0f} TRADES'.format(len(list_of_trades)))
        blank_line()
        for i, trade in enumerate(list_of_trades):
            display_individual_trade(i, trade)
        full_line()

    def disp_exposure(self):
        centered_line('EXPOSURE ON {}'.format(self.broker_instance.broker_name.upper()))
        full_line()


def display_individual_trade(i, trade):
    asset = trade['instrument']
    long_or_short = 'SHORT' if int(trade['initialUnits']) < 0 else 'LONG'
    dt = trade['openTime']
    price = trade['price']
    size = abs(int(trade['initialUnits']))
    pl = trade['unrealizedPL']
    mu = float(trade['marginUsed']) * 100

    indented_line('TRADE #{0:.0f}: {1} - {2}'.format(i, asset, long_or_short))
    double_indented_line('ENTRY TIME: {}/{}/{} - {}h{}'.format(dt[8:10], dt[5:7], dt[0:4], dt[11:13], dt[14:16]))
    double_indented_line('ENTRY PRICE: {}'.format(price))
    double_indented_line('ORDER SIZE: {} UNITS'.format(size))
    double_indented_line('CURRENT PL: {} USD'.format(pl))
    double_indented_line('MARGIN USED: {0:.2f} USD'.format(mu))
    blank_line()


def disp_title():
    d = datetime.datetime.now()
    dt_str = '{0:02.0f}/{1:02.0f}/{2:.0f} - {3:02.0f}h{4:02.0f}'.format(d.day, d.month, d.year, d.hour, d.minute)
    full_line()
    centered_line('LIVE ENVIRONMENT DISPLAY - {}'.format(dt_str))
    full_line()


def load_oracle(strategy_name):
    # Load Strategy
    with open('data/model_manager/{}.pkl'.format(strategy_name), 'rb') as f:
        return cPickle.load(f)
