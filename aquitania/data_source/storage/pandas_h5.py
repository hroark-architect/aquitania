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

12/04/2018 - Created a pandas storage system.
"""
import os

import aquitania.resources.references as references
import pandas as pd
import numpy as np

from aquitania.data_processing.util import generate_folder
from aquitania.data_source.storage.abstract_storage_system import AbstractStorageSystem


class PandasHDF5(AbstractStorageSystem):
    def __init__(self, broker_name):
        """
        Initializes pandas HDF5 storage system.

        'controls.h5' - Stores what was the last candle to be saved into the database
        'data.h5' - Data itself

        :param broker_name: (str) Broker name (Ex.: oanda, fxcm...)
        """
        super().__init__(broker_name=broker_name, extension='.h5')

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
        self.add_to_hdf5(asset, df)

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
        with pd.HDFStore(self.get_candles_filename(asset)) as hdf:
            df = hdf.get(key='G01')
            return df

    def save_over_data(self, asset, df):
        """
        Overwrites current file on disk. Used on 'controls.h5', not on the main 'data.h5' file.
        :param asset: (str) Asset Name
        :param df: (pandas DataFrame) DataFrame to be store into disk
        """
        # Opens HDF5 file
        with pd.HDFStore(self.get_candles_filename(asset)) as hdf:
            # Remove current files
            hdf.remove(key='G01')

            # Save new files into disk
            hdf.append(key='G01', value=df, format='table', data_columns=True, dropna='any')

    def add_to_hdf5(self, asset, df):
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
        with pd.HDFStore(self.get_candles_filename(asset)) as hdf:
            hdf.append(key='G01', value=df, format='table', data_columns=True, dropna='any')

        # Update controls with new data
        self.reset_controls(asset, df.index[-1])

    def reset_controls(self, asset, end_date):
        """
        Deletes data store in 'control.h5', and create a new file only with a different 'end_date' according to new
        input.

        :param asset: (str) Asset Name
        :param end_date: (DateTime) Last Candle saved into disk
        """
        # Open HDF5 file
        with pd.HDFStore(self.get_candles_controls_filename(asset)) as hdf:
            # Gets temporary DataFrame to be edited
            end_df = hdf.get(key='controls')

            # Removes hdf5 table from disk
            hdf.remove(key='controls')

            # Changes 'end_date' parameter
            end_df['end_date'] = end_date

            # Saves 'controls.hdf5' back into disk
            hdf.append(key='controls', value=end_df, format='table', data_columns=True, dropna='any')

    def save_controls(self, asset, df):
        """
        Appends controls DataFrame into 'controls.h5'

        :param asset: Asset Name
        :param df: controls DataFrame
        """
        # Generates candles and asset name if folder don't exist
        generate_folder('{}/{}'.format(self.candles_folder, asset))

        # Save controls DataFrame into disk
        with pd.HDFStore(self.get_candles_controls_filename(asset)) as hdf:
            hdf.put(key='controls', value=df, format='table')

    def is_candles(self, finsec):
        return os.path.isfile(self.get_candles_filename(finsec))

    def is_controls(self, asset):
        """
        Check if control files exists.

        :param asset: Asset Name

        :return: True if there is a controls file for given asset name
        :rtype: bool
        """
        return os.path.isfile(self.get_candles_controls_filename(asset))

    def read_controls(self, asset):
        """
        Read control.h5 file and returns DataFrame that is stored inside it.

        :param asset: (str) Asset Name
        """
        return pd.read_hdf(self.get_candles_controls_filename(asset))

    def save_indicators(self, df, asset, ts):
        """
        Save indicators into disk according to asset name and ts.

        :param df: (pandas DataFrame) Save DataFrame into disk
        :param asset: (str) Asset Name
        :param ts: (int) Timestamp id
        """
        # Filename (with folder included)
        filename = self.get_indicator_filename(asset, ts)

        # Saves indicators into disk
        with pd.HDFStore(filename) as hdf:
            hdf.append(key='indicators', value=df, format='table', data_columns=True)

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
                    with pd.HDFStore(filepath) as hdf:
                        columns[the_file] = set(hdf.select('indicators', start=0, stop=0).columns.values)

        # Returns dictionary with keys as timestamp and values as column names
        return columns
