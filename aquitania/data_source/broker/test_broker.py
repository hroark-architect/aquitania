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

Repository of code related to broker test module.

20/04/2018 - Created TestBroker class already utilizing the AbstractDataSource architecture.
"""
from six.moves import urllib

from data_source.broker.abstract_data_source import AbstractDataSource


class TestBroker(AbstractDataSource):
    """
    This class creates objects that establishes connections with Oanda API.

    Attributes - implemented by AbstractDataSource:
    broker_name (str) = Broker (Ex.: 'oanda')
    ds_name (str) = Data Storage Type (Ex.: 'pandas_hdf5')
    ds (AbstractStorageSystem) - Custom object to deal with data storage

    Attributes - broker specific:
    account_ID (str): Oanda's account ID
    token (str): Oanda's API token
    api (API): Oanda's API object
    """

    def __init__(self, broker_name, data_storage_type):
        # Sets .ds 'str' calling super DataSource class
        self.url = 'https://raw.githubusercontent.com/hroark-architect/data/master/'
        super().__init__(broker_name, data_storage_type)

    def candle_downloader(self, start_date, finsec, q1):
        """
        Important to notice that this method doesn't really update candles with new information, it only downloads a
        file that is pretty much never updated. This only serves for test purposes.

        :param start_date:  Irrelevant
        :param finsec: Desired Financial Security (Ex.: EUR_USD)
        :param q1: Irrelevant
        """
        # Checks if there is a test file already
        if not self.ds.is_candles(finsec):

            # Initialize Variables to get downloaded data from server
            url = '{}{}.h5'.format(self.url, finsec)
            filepath = self.ds.get_candles_filename(finsec)

            try:
                # Downloads data from server
                urllib.request.urlretrieve(url, filepath)
            except:
                # Gives back a generic error, might be a connection issue as well, improve this on the future
                raise ValueError('Didn\'t get file from server, selected financial security may not there.')

    def get_historic_data_status(self, finsec):
        pass
