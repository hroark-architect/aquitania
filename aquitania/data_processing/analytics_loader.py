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

This modules loads from disk the output from the indicators creates a single DataFrame for each currency that unifies
all the timestamps, OR a unified DataFrame for all currencies and timestamps, depending on what was requested.

Started refactoring this module on 26/04/2018. Currently thinking about dividing it into 2 different modules. Decided to
make it only one module but remove AnalyticsLoader class and leave only standalone methods.
"""
import os.path
import pandas as pd

from aquitania.data_processing.util import get_stored_ai, add_asset_columns_to_df, save_df, add_to_dataframe


def build_liquidation_dfs(broker_instance, asset, list_of_columns, signal):
    """
    This method builds a DataFrame with all possible entries that will be fed to the liquidation module in order to
    evaluate which are the optimal exit points.

    :param broker_instance: (DataSource) connection to broker / database
    :param asset: (str) Asset Name
    :param list_of_columns: (list of str) detailing column names
    :param signal: (str) signal name

    :return: DataFrame with all possible entries
    :rtype: pandas DataFrame
    """
    # Get column names
    columns_dict = get_dataframes_that_contain_columns(broker_instance, asset, list_of_columns)

    # Instantiate variables
    timestamp = signal[0]
    final_df = None
    complete = 'complete_{}'.format(timestamp)

    # Check if there is an indicator output file for given asset
    for filename in os.listdir(broker_instance.ds.indicator_output_folder):
        if asset in filename:
            break

    # If no file is found in the for loop, raises error
    else:
        raise IOError('No indicator that for selected currency: ' + asset)

    # Retrieves DataFrame that will be used to filter valid signal rows
    df = pd.read_hdf(broker_instance.get_indicator_filename(asset, timestamp))[[signal, complete]]

    # Gets all DataFrames according to key values (each key represents one timestamp)
    for key in columns_dict.keys():

        # Builds filepath str
        filepath = '{}/{}/{}'.format(broker_instance.ds.indicator_output_folder, asset, key)

        # Loads Indicators for given timestamp and asset
        temp_df = pd.read_hdf(filepath)[list(columns_dict[key])]

        # Instantiates first DataFrame to be joined
        if final_df is None:

            # Creates a filter column
            temp_df['filter'] = (df[complete] == 1) & (df[signal] != 0)

            # Makes a filter only to select rows where complete and signal are True
            final_df = temp_df.query('filter == 1')

            # Deletes filter column
            del final_df['filter']

        else:
            # Makes inner join with DataFrame that has filtered rows (output will be filtered as well)
            final_df = pd.concat([final_df, temp_df], join='inner', axis=1)

    # Returns filtered DataFrame
    return final_df


def get_dataframes_that_contain_columns(broker_instance, asset, set_of_columns):
    """
    Get DataFrames IDs for every column (str) in 'set_of_columns'.

    :param broker_instance: (DataSource) connection to broker / database
    :param asset: (str) Asset Name
    :param set_of_columns: (set of str) names of columns to be selected across multiple DataFrames

    :return: dictionary of lists where key is the name of the storage file and the relevant column it contains
    :rtype: dict of lists
    """
    # Get a DataFrame with all columns by key
    dict_of_columns = broker_instance.get_dict_of_file_columns(asset)

    # Instantiates new dict
    selected_keys = {}

    # For each possible key checks if it contains one of the columns in 'list_of_columns'
    for key in dict_of_columns.keys():

        # Find if there is an intersection between the selected columns and the actual columns in the file
        set_intersect = set_of_columns.intersection(dict_of_columns[key])

        # If there are columns that intersect, save it to output according to key in 'dict_of_columns'
        if len(set_intersect) > 0:
            selected_keys[key] = set_intersect

    # Returns a dict of sets that contain intersecting values
    return selected_keys


def build_ai_df(broker_instance, asset_list, signal):
    """
    Creates one DataFrame with all columns from all timestamps filtering rows for only the rows where signal is True.
    This creates a much less computationally expensive DataFrame.

    :param broker_instance: (DataSource) connection to broker / database
    :param asset_list: (list of str) list of Asset Names
    :param signal: (str) entry name

    :return: DataFrame with all assets and all columns
    :rtype: pandas DataFrame
    """
    # Initialize output variable
    final_df = None

    # Runs routine for each of the assets
    for asset in asset_list:
        # Gets stored AI if any
        cur_df = get_stored_ai(asset, signal)

        # TODO add verification to check if same size of the liquidation DataFrame
        if not isinstance(cur_df, pd.DataFrame):
            # Routine for when a new AI DataFrame needs to be created
            df_filter = get_signal_filter(broker_instance, asset, signal)

            # Get asset output (all timestamps combined into a single DataFrame)
            cur_df = get_asset_output(broker_instance, asset, df_filter, signal)

            # Add columns relative to asset classification to DataFrame
            cur_df = add_asset_columns_to_df(cur_df, asset)

            # Save AI DataFrame into disk
            save_df(cur_df, 'data/ai/' + asset + '_' + signal)

        # Combines individual asset output into a single DataFrame
        final_df = add_to_dataframe(final_df, cur_df, axis=0)

    # Returns Final DataFrame
    return final_df


def get_signal_filter(broker_instance, asset, signal):
    """
    Creates a filter to only select rows that have a signal on a DataFrame.

    :param broker_instance: (DataSource) connection to broker / database
    :param asset: (str) Asset Name
    :param signal: (str) entry name

    :return: Boolean values to determine which rows to select in a DataFrame
    :rtype: numpy Array
    """
    # Generates Timestamp Id - single digit number as (str)
    timestamp = signal[0]

    # Gets signal filter
    with pd.HDFStore(broker_instance.get_indicator_filename(asset, timestamp)) as hdf:
        df = hdf.select(key='indicators', columns=[signal, 'complete_' + timestamp])

    # Returns signal filter
    return df['complete_' + timestamp].astype(bool) & df[signal].astype(bool)


def get_asset_output(broker_instance, asset, df_filter, signal):
    """
    Gets a single huge DataFrame combining all timestamps for a given asset.

    :param broker_instance: (DataSource) connection to broker / database
    :param asset: (str) Asset Name
    :param df_filter: (numpy Array) Boolean values to determine which rows to select in a DataFrame

    :return: DataFrame combining all timestamps for a given asset
    :rtype: pandas DataFrame
    """
    # Initializes variables
    folder = broker_instance.ds.indicator_output_folder
    final_df = None
    list_dir = sorted(os.listdir(folder))

    # Search for directories
    for directory in list_dir:

        # Check if it is desired asset directory
        if asset in directory:

            # Gets folder name for current directory
            finsec_dir = '{}/{}/'.format(folder, asset)

            # Sorts file names to create DataFrame in a logical order of columns
            list_output = sorted(os.listdir(finsec_dir))

            # Runs file by file routine to append them into a single DataFrame
            for the_file in list_output:
                # Reads and filters DataFrame
                temp_df = pd.read_hdf(finsec_dir + the_file)[df_filter]

                # Combines timestamps into a single DataFrame
                final_df = add_to_dataframe(final_df, temp_df, axis=1)

    # Adds an entry column to the DataFrame (next 1Min candle open)
    final_df['entry'] = pd.read_hdf('data/liquidation/' + asset + '_' + signal)['entry']

    # Returns DataFrame with all timestamps
    return final_df
