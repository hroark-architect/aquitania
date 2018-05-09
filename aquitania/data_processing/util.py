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

File to hold utility functions related to data processing.
"""

import os
import shutil
import aquitania.resources.references as ref
import pandas as pd


def clean_indicator_data():
    """
    Delete all files in folders related to indicator output.
    """
    delete_contents('data/indicator')
    delete_contents('data/state')
    delete_contents('data/order_manager')


def clean_ai_data():
    """
    Delete all files in folders related to AI output.
    """
    delete_contents('data/liquidation')
    delete_contents('data/ai')
    delete_contents('data/model_manager')


def delete_contents(folder):
    """
    Delete all files inside an specific folder.
    :param folder: Folder path
    """
    # Create folder if it doesn't exist
    generate_folder(folder)

    # File deletion routine
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            # Delete files inside folder
            if os.path.isfile(file_path):
                os.unlink(file_path)

            # Delete directories inside folder
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


def generate_folder(folder):
    if not os.path.isdir(folder):
        os.makedirs(folder)


def get_stored_ai(finsec, signal):
    df_path = 'data/ai/' + finsec + '_' + signal
    if os.path.exists(df_path):
        return pd.read_hdf(df_path)
    else:
        return False


def add_to_dataframe(df, temp_df, axis):
    if df is not None:
        return pd.concat([df, temp_df], axis=axis)
    else:
        return temp_df


def save_df(df, df_path):
    """
    Save observations DataFrame to pandas.

    :param df: DataFrame to be stored in HDF5
    :param df_path: Name of file to be Stored
    """
    # Saves observations to disk
    with pd.HDFStore(df_path) as hdf:
        hdf.append(key='indicators', value=df, format='table', data_columns=True)


def add_asset_columns_to_df(df, finsec):
    df['asset'] = ref.currencies_dict[finsec]
    df['eval_currency'] = ref.currency_list.index(finsec.split('_')[0])
    df['base_currency'] = ref.currency_list.index(finsec.split('_')[1])
    return df
