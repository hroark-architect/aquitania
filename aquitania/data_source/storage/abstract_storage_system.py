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

12/04/2018 - Created an abstract storage system.
"""

import abc

from aquitania.data_processing.util import generate_folder
from aquitania.data_source.storage.sanity_check import basic_sanitizer


class AbstractStorageSystem:
    __metaclass__ = abc.ABCMeta

    def __init__(self, broker_name, extension):
        self.candles_folder = '{}/{}'.format('repository', broker_name)
        self.indicator_output_folder = '{}/{}'.format('data/indicator', broker_name)
        self.extension = extension

    @abc.abstractmethod
    def add_data(self, df):
        pass

    @abc.abstractmethod
    def get_stored_data(self, currency):
        pass

    @abc.abstractmethod
    def save_over_data(self, currency, df):
        pass

    @abc.abstractmethod
    def save_indicators(self, df, currency, ts):
        pass

    def sanitize(self, currency):
        df = self.get_stored_data(currency)
        df = basic_sanitizer(df)
        self.save_over_data(currency, df)

    def get_indicator_filename(self, finsec, ts):
        generate_folder('{}/{}/'.format(self.indicator_output_folder, finsec))
        return '{}/{}/{}{}'.format(self.indicator_output_folder, finsec, ts, self.extension)

    def get_candles_filename(self, finsec):
        generate_folder('{}/{}/'.format(self.candles_folder, finsec))
        return '{}/{}/data{}'.format(self.candles_folder, finsec, self.extension)

    def get_candles_controls_filename(self, finsec):
        generate_folder('{}/{}/'.format(self.candles_folder, finsec))
        return '{}/{}/controls{}'.format(self.candles_folder, finsec, self.extension)
