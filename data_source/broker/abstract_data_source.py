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

from data_source.storage.pandas_h5 import PandasHDF5


class AbstractDataSource:
    __metaclass__ = abc.ABCMeta

    def __init__(self, broker_name, data_storage_type):
        self.broker_name = broker_name
        self.ds_name = data_storage_type
        self.ds = self.get_dss(data_storage_type)

    def get_dss(self, data_storage_type):
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

    def load_data(self, finsec):
        """
        Loads data stored in disk for a specific Financial Security, this will fetch all candles.

        :param finsec: (str) Select Financial Security
        :return: Stored data for selected Financial Security
        :rtype: pandas DataFrame
        """

        return self.ds.get_stored_data(finsec)

    def sanitize(self, finsec):
        """
        Sanitizes data according to DataStorage method.
        :param finsec: (str) selected Financial Security
        """
        self.ds.sanitize(finsec)

    def save_indicators(self, df, finsec, ts):
        self.ds.save_indicators(df, finsec, ts)

    def get_indicator_filename(self, finsec, ts):
        return self.ds.get_indicator_filename(finsec, ts)

    def get_dict_of_file_columns(self, finsec):
        return self.ds.get_dict_of_file_columns(finsec)

    @abc.abstractmethod
    def new_historic_data_status(self, finsec):
        """
        Gets status of historic data download according to a specific data storage type.

        :return A DataFrame consisting of 5 columns (financial_instrument, g01, g05, g15, g60)
        :rtype pandas DataFrame
        """
        pass

    @abc.abstractmethod
    def candle_downloader(self, df_data_status, finsec, q1):
        """
        Manages which data source to send the candle download request to.

        :broker_instance instance of Broker class needed to download candles
        :dfDataStatus DataFrame that signals from which date to start downloading
        :q1 queue that is used inside the candle download functions
        """
        pass

    @abc.abstractmethod
    def connection_historic_data(self, params):
        """
        Chooses which broker to download historic data from.

        :params broker required params
        :return returns raw data from broker
        :rtype may vary according to broker
        """
        pass

    @abc.abstractmethod
    def data_processing_manager(self, raw_data):
        """
        Chooses method to process raw data according to which broker generated it.

        :raw_data raw data that was download from broker
        :return returns processed data
        :rtype list of lists
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

    @abc.abstractmethod
    def get_oscillation_and_volume(self, finsec):
        pass

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
