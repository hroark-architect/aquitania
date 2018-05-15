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

12/04/2018 - Made a big refactor on this module, pretty much removing for good one of the first classes I ever created
which was called DataSource and made an improved and more efficient architecture, using DataSource as an abstract class
to force implementation of certain methods and etc.
"""

import abc
import datetime

from aquitania.data_source.storage.pandas_h5 import PandasHDF5


class AbstractDataSource:
    __metaclass__ = abc.ABCMeta

    def __init__(self, broker_name, data_storage_type, is_live=False):
        self.broker_name = broker_name
        self.ds_name = data_storage_type
        self.is_live = is_live
        self.ds = self.get_dss(data_storage_type)

    def get_dss(self, data_storage_type):
        data_storage_type = data_storage_type.lower()
        if data_storage_type == 'pandas_hdf5':
            return PandasHDF5(self.broker_name)
        else:
            raise NameError('Invalid Storage System Name')

    def get_historic_data_status(self, finsec):
        """
        Get historic data status.

        :param finsec: (str) Financial Security to select data

        :return: DataFrame containing start and end dates stored in the storage system
        :rtype: pandas DataFrame
        """
        if not self.ds.is_controls(finsec):
            self.new_historic_data_status(finsec)
        return self.ds.read_controls(finsec)['end_date'].values[0]

    def store(self, df):
        self.ds.add_data(df)

    def load_data(self, asset):
        """
        Loads data stored in disk for a specific Financial Security, this will fetch all candles.

        :param asset: (str) Select Financial Security
        :return: Stored data for selected Financial Security
        :rtype: pandas DataFrame
        """

        return self.ds.get_stored_data(asset)

    def sanitize(self, asset):
        """
        Sanitizes data according to DataStorage method.

        :param asset: (str) selected Financial Security
        """
        self.ds.sanitize(asset)

    def save_indicators(self, df, asset, ts):
        self.ds.save_indicators(df, asset, ts)

    def get_indicator_filename(self, asset, ts):
        return self.ds.get_indicator_filename(asset, ts)

    def get_dict_of_file_columns(self, asset):
        return self.ds.get_dict_of_file_columns(asset)

    def gen_asset_dict(self, asset):
        """
        Get Data Dictionary.

        Get Asset Attributes will get the specific info needed for a specific broker. This method will pull the info
        which is specific to each broker and then add some general methods on top of it.

        :param asset: (str) Asset Name

        :return: Data Dictionary for a given asset
        :rtype: dictionary
        """
        # Generates Data Dictionary
        data_dict = self.get_asset_attributes(asset)

        # Updates Data Dictionary with new fields

        data_dict['asset'] = asset
        data_dict['oscillation'], data_dict['volume'] = self.get_oscillation_and_volume(asset)
        data_dict['spread_by_osc'] = data_dict['spread'] / data_dict['oscillation']['D144']
        data_dict['update_on'] = datetime.datetime.now()
        data_dict['spread_by_osc'] = data_dict['last_bid'] / 10000

        # Returns Data Dictionary
        return data_dict

    def get_oscillation_and_volume(self, asset):
        df = self.load_data(asset)
        osc_avg_13, osc_avg_21, vol_13, vol_21 = calc_resample_osc(df, 'W', 13, 21)
        osc_avg_89, osc_avg_144, vol_89, vol_144 = calc_resample_osc(df, 'B', 89, 144)
        osc_dict = {'D144': osc_avg_144, 'D89': osc_avg_89, 'W21': osc_avg_21, 'W13': osc_avg_13}
        vol_dict = {'D144': vol_144, 'D89': vol_89, 'W21': vol_21, 'W13': vol_13}
        return osc_dict, vol_dict

    @abc.abstractmethod
    def get_asset_attributes(self, asset):
        pass

    @abc.abstractmethod
    def new_historic_data_status(self, asset):
        """
        Gets status of historic data download according to a specific data storage type.

        :return A DataFrame consisting of 5 columns (financial_instrument, g01, g05, g15, g60)
        :rtype pandas DataFrame
        """
        pass

    @abc.abstractmethod
    def candle_downloader(self, start_date, asset, q1):
        """
        Manages which data source to send the candle download request to.

        :param start_date: (datetime) Date which to start downloading Candles
        :param asset: (str) Asset Name to download candles
        :param q1 queue that is used inside the candle download functions
        """
        pass

    @abc.abstractmethod
    def connection_historic_data(self, params):
        """
        Chooses which broker to download historic data from.

        :param params: required params

        :return returns raw data from broker
        :rtype may vary according to broker
        """
        pass

    @abc.abstractmethod
    def data_processing_manager(self, raw_data):
        """
        Chooses method to process raw data according to which broker generated it.

        :param raw_data: (varies from broker to broker) Data that was downloaded from the broker

        :return: returns processed data
        :rtype: something that can easily transform into a pandas DataFrame
        """
        pass

    @abc.abstractmethod
    def stream(self, currencies_list, df_f_stream):
        """
        Initializes stream of Candles.

        This is kind of an infinite loop function. There is no controls implemented to stop and go.

        :param currencies_list: List of currencies to be Streamed
        :param df_f_stream: DataFrame created from Streaming
        """
        pass

    @abc.abstractmethod
    def get_spread_data(self, finsec):
        pass

    # TODO Evaluate methods that are not used directly after refactor and remove them from here

    @abc.abstractmethod
    def get_precision_digits(self, finsec):
        pass

    @abc.abstractmethod
    def get_account_balance(self):
        pass

    @abc.abstractmethod
    def get_account_nav(self):
        pass

    @abc.abstractmethod
    def get_list_of_instruments(self):
        pass

    @abc.abstractmethod
    def get_list_of_trades(self):
        pass

    @abc.abstractmethod
    def order(self, quote, precision_digits, bet_size, currency, profit, stop):
        pass

    @abc.abstractmethod
    def get_used_margin(self):
        pass

    @abc.abstractmethod
    def get_trade_params(self, asset):
        pass


def calc_resample_osc(df, resample, x1, x2):
    candles = df.resample(resample).agg({'high': 'max', 'low': 'min', 'volume': 'sum'})
    candles.columns = ['max', 'min', 'volume']
    candles['osc'] = candles['max'] - candles['min']

    osc_1 = candles['osc'][-x1:].mean()
    osc_2 = candles['osc'][-x2:].mean()

    vol_1 = candles['volume'][-x1:].mean()
    vol_2 = candles['volume'][-x2:].mean()

    return osc_1, osc_2, vol_1, vol_2
