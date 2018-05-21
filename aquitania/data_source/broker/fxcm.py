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
.. moduleauthor:: Kavk

16/04/2018 - First file to created by an external contribution.
"""

import datetime
import pandas as pd
import numpy as np
import aquitania.resources.references as references

import fxcmpy

from aquitania.data_source.broker.abstract_data_source import AbstractDataSource
from aquitania.resources.datetimefx import next_candle_datetime


class FXCM(AbstractDataSource):
    """
    This class creates objects that establishes connections with FXCM API.

    Attributes:
    tokes (str): FXCM's API token
    """

    def __init__(self, broker_name, data_storage_type):
        # Read 'oanda_data.txt' file and creates a iterable of lines

        # Sets file paths
        self.folder_path = 'data/broker/'
        self.file_path = self.folder_path + 'fxcm_data.txt'

        # Loads attributes
        self.token, self.account_type = self.get_trading_data()

        # Sets .ds 'str' calling super DataSource class
        super().__init__(broker_name, data_storage_type, is_live=True)

        # Configures API access
        self.api = fxcmpy.fxcmpy(access_token=self.token, log_level='error', server=self.account_type)

    def get_trading_data(self):
        try:
            text_file = open(self.file_path, 'r')
            lines = text_file.readlines()
            token = lines[0][0:40]  # Remove spaces on the end of the line
            account_type = lines[1][0:4]  # Remove spaces on the end of the line

        except:
            print('\nCreate an account at www.fxcm.com\n')
            print('Insert your API token: (format: e462ba7617fc2a824ac440264dbfbfe1f095de64)')
            token = input()
            print('Insert your account type: (format: demo or real)')
            account_type = input()
            text_file = open(self.file_path, 'w')
            text_file.write(token + '\n' + account_type)

        text_file.close()

        return token, account_type

    def new_historic_data_status(self, asset):
        if not self.ds.is_controls(asset):
            # TODO Improve and create a method to get first candle from FXCM API database
            output = [asset, datetime.datetime(2010, 1, 1), datetime.datetime(2010, 1, 1)]

            df = pd.DataFrame([output])
            df.columns = ['currency', 'start_date', 'end_date']

            self.ds.save_controls(asset, df)

    def candle_downloader(self, start_date, asset, q1):
        """
        Download candles from FXCM server using multiprocessor module that is managed elsewhere.

        This function is specific to be using with the multiprocessor method that was build with HistoricDataManager.

        It will not work otherwise.

        :q1 queue that is used inside the candle download functions
        """
        # Iterates through timestamps and currencies

        if isinstance(start_date, pd._libs.tslib.Timestamp):
            proc_start_date = next_candle_datetime(start_date.to_pydatetime(), 1)
        elif isinstance(start_date, np.datetime64):
            proc_start_date = next_candle_datetime(datetime.datetime.utcfromtimestamp(start_date.tolist() / 1e9), 1)
        elif isinstance(start_date, datetime.datetime):
            proc_start_date = next_candle_datetime(start_date, 1)
        else:
            raise TypeError('FXCM start_date is of a wrong type. Try datetime.datetime or np.datetime64.')

        start = proc_start_date
        stop = start + datetime.timedelta(minutes=5000)

        while True:
            candles = self.api.get_candles(asset.replace('_', '/'), period='m1', start=start, stop=stop)
            candles['fi'] = references.currencies_dict[asset]
            q1.put(candles)
            if stop > datetime.datetime.today():
                break
            start = stop + datetime.timedelta(minutes=1)
            stop = start + datetime.timedelta(minutes=5000)

    def connection_historic_data(self, params):
        pass
        # df = self.api.get_candles('EUR/USD', period=params['ts'], start=params['start_date'], stop=stop)

    def data_processing_manager(self, raw_data):
        raw_data['tickqty'].replace(0, 1, inplace=True)

        raw_data = raw_data[['fi', 'bidopen', 'bidhigh', 'bidlow', 'bidclose', 'tickqty']]
        raw_data.columns = ['fi', 'open', 'high', 'low', 'close', 'volume']
        raw_data.index.names = ['datetime']

        print(raw_data.tail(1))
        return raw_data

    def get_spread_data(self, asset):
        pass

    def get_account_balance(self):
        pass

    def get_account_nav(self):
        pass

    def get_list_of_instruments(self):
        pass

    def get_list_of_trades(self):
        pass

    def order(self, quote, precision_digits, bet_size, currency, profit, stop):
        pass

    def get_used_margin(self):
        pass
