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

29/05/2018 - Created a feather storage system.
"""
import os

import aquitania.resources.references as references
import pandas as pd
import numpy as np

from aquitania.data_processing.util import generate_folder
from aquitania.data_source.storage.abstract_storage_system import AbstractStorageSystem


class PandasFeather(AbstractStorageSystem):
    def __init__(self, broker_name):
        """
        Initializes pandas HDF5 storage system.

        'controls.h5' - Stores what was the last candle to be saved into the database
        'data.h5' - Data itself

        :param broker_name: (str) Broker name (Ex.: oanda, fxcm...)
        """
        super().__init__(broker_name=broker_name, extension='.feather')

    def get_stored_data(self, asset):
        """
        Gets stored data for specific asset.

        :param asset: (str) Asset name

        :return: Candles for specified asset
        :rtype: pandas DataFrame
        """
        # Generates candles and asset name if folder don't exist
        generate_folder('{}/{}'.format(self.candles_folder, asset))

        # Gets DataFrame from disk
        return pd.read_feather(self.get_candles_filename(asset)).set_index('datetime')

    def save_over_data(self, asset, df):
        """
        Overwrites current file on disk. Used on 'controls.h5', not on the main 'data.h5' file.
        :param asset: (str) Asset Name
        :param df: (pandas DataFrame) DataFrame to be store into disk
        """
        # Opens Feather file
        df.reset_index().to_feather(self.get_candles_filename(asset))

    def add_data_storage(self, asset, df):
        """
        Saves DataFrame into disk accordingly to asset name.

        :param asset: (str or int) Asset Name
        :param df: (pandas DataFrame) DataFrame to be store into disk
        """
        # Transforms asset (int) into (str) if input was in (int)
        # TODO improve type handling somewhere else in the code to be able to remove this line
        if not isinstance(asset, str):
            asset = references.currencies_list[asset]

        # Save Candles data into disk
        df.reset_index().to_feather(self.get_candles_filename(asset))

        # Update controls with new data
        self.reset_controls(asset, df.index[-1])

    def reset_controls(self, asset, end_date):
        """
        Deletes data store in 'control.h5', and create a new file only with a different 'end_date' according to new
        input.

        :param asset: (str) Asset Name
        :param end_date: (DateTime) Last Candle saved into disk
        """
        df = pd.read_feather(self.get_candles_controls_filename(asset))
        df['end_date'] = end_date
        df.to_feather(self.get_candles_controls_filename(asset))

    def save_controls(self, asset, df):
        """
        Appends controls DataFrame into 'controls.h5'

        :param asset: Asset Name
        :param df: controls DataFrame
        """
        # Generates candles and asset name if folder don't exist
        generate_folder('{}/{}'.format(self.candles_folder, asset))

        # Save controls DataFrame into disk
        df.to_feather(self.get_candles_controls_filename(asset))

    def read_controls(self, asset):
        """
        Read control.h5 file and returns DataFrame that is stored inside it.

        :param asset: (str) Asset Name
        """
        return pd.read_feather(self.get_candles_controls_filename(asset))

    def save_indicators(self, df, asset, ts):
        """
        Save indicators into disk according to asset name and ts.

        :param df: (pandas DataFrame) Save DataFrame into disk
        :param asset: (str) Asset Name
        :param ts: (int) Timestamp id
        """
        # Filename (with folder included)
        filename = self.get_indicator_filename(asset, ts)

        df.reset_index().to_feather(filename)
