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
import numpy as np
import os

from aquitania.data_processing.util import generate_folder
from aquitania.data_source.storage.sanity_check import basic_sanitizer


class AbstractStorageSystem:
    __metaclass__ = abc.ABCMeta

    def __init__(self, broker_name, extension):
        self.candles_folder = '{}/{}'.format('repository', broker_name)
        self.indicator_output_folder = '{}/{}'.format('data/indicator', broker_name)
        self.extension = extension

    def add_data(self, df):
        """
        Appends Candle data to HDF5 repository.

        :param df: (pandas DataFrame) Candle data to be appended.
        DataFrame columns are: ['open, 'high', 'low', 'close', 'volume'] with DateTime index.
        """
        # Gets asset name
        asset = df.loc[df.index[-1], 'fi']

        # Creates new DataFrame (Uses .copy() to avoid pandas setCopyWarning...)
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()

        # Converts volume to int32
        df.loc[:, 'volume'] = df.loc[:, 'volume'].astype(np.int32)

        # Saves into HDF5
        self.add_data_storage(asset, df)

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

    def is_candles(self, asset):
        return os.path.isfile(self.get_candles_filename(asset))

    def is_controls(self, asset):
        """
        Check if control files exists.

        :param asset: Asset Name

        :return: True if there is a controls file for given asset name
        :rtype: bool
        """
        return os.path.isfile(self.get_candles_controls_filename(asset))

    def get_dict_of_file_columns(self, asset):
        """
        Creates a dictionary with keys as timestamp and values as column names.

        :param asset: (str) Asset Name

        :return: dictionary with keys as timestamp and values as column names
        :rtype: dict of sets
        """
        # Sets indicator output folder
        folder = self.indicator_output_folder
        generate_folder(folder)

        # Creates dict
        columns = {}

        # Gets list of assets
        for directory in os.listdir(folder):

            # Checks if there asset is on the list of all assets
            if asset in directory:

                # Creates path for desired asset
                currency_dir = '{}/{}'.format(folder, directory)

                # Iterates through list of files for given asset
                for the_file in os.listdir(currency_dir):
                    # Gets filepath for given file
                    filepath = '{}/{}'.format(currency_dir, the_file)

                    # Get column name for given file
                    columns[the_file] = self.get_columns(filepath)

        # Returns dictionary with keys as timestamp and values as column names
        return columns

    @abc.abstractmethod
    def add_data_storage(self, asset, df):
        pass

    @abc.abstractmethod
    def get_stored_data(self, currency):
        pass

    @abc.abstractmethod
    def get_stored_data_in_chunks(self, currency, chunksize):
        pass

    @abc.abstractmethod
    def save_over_data(self, currency, df):
        pass

    @abc.abstractmethod
    def save_indicators(self, df, currency, ts):
        pass

    @abc.abstractmethod
    def get_columns(self, filepath):
        pass
