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
"""
import bisect
import multiprocessing
import pandas as pd
import numpy as np
import os
from aquitania.data_processing.analytics_loader import build_liquidation_dfs
from cpython.datetime cimport datetime

cpdef build_exits(broker_instance, str asset, signal, int max_candles, bint is_dentro=False, bint is_virada=False):
    """
    Calculates exit DateTime for a list of Exit Points. It will be used in later module that evaluates winning or
    losing positions.

    :param broker_instance: (DataSource) Input broker instance
    :param asset: (str) Input asset
    :param signal: (AbstractSignal) Input signal
    :param max_candles: (int) Number of max G01 candles to look in the future to liquidate trade
    :param is_dentro: (bool) True if when positioned, don't look for new positions in the same side
    :param is_virada: (bool) True if when positioned, if there is a trade in the same side, you switch positions
    """

    # Initializes variables
    entry = signal.entry
    exit_points = {signal.stop, signal.profit}
    exits = None
    import time
    time_a = time.time()

    df, candles_df = build_dfs(broker_instance, asset, exit_points, entry)
    print('build_dfs: ', time.time() - time_a)

    time_b = time.time()
    exits = process_exit_points(df, exit_points, candles_df, max_candles, is_virada)
    print('process exit points: ', time.time() - time_b)

    # Sets filename
    filename = 'data/liquidation/' + asset + '_' + entry

    # Save liquidation to disk
    time_c = time.time()
    save_liquidation_to_disk(filename, exits)
    print('save liquidation to disk: ', time.time() - time_c)

    time_d = time.time()
    consolidate_exits(asset, entry, exits, is_dentro)
    print('consolidate exits: ', time.time() - time_d)

cdef build_dfs(broker_instance, asset, exit_points, entry):
    # Load DataFrames
    df = build_liquidation_dfs(broker_instance, asset, exit_points, entry)
    candles_df = broker_instance.load_data(asset)

    # Create Entry Point column
    candles_df['entry_point'] = candles_df['open'].shift(-1)

    # Build entry points and close values into exit DataFrame
    df = build_entry_points(df, candles_df)

    # Checks if df is empty and raise Warning if so.
    if df.shape[0] == 0:
        ValueError('There was a problem with the signal in your strategy, it didn\'t generate any ok=True.')

    # Clean Candles DF
    candles_df = candles_df[['open', 'high', 'low']]

    return df.sort_index(), candles_df

cdef process_exit_points(df, exit_points, candles_df, max_candles, is_virada):
    cdef object exits = None

    # Create exits for all exit points
    for exit_point in exit_points:
        # Run multiprocessing routine
        temp_exit = mp(df[['close', 'entry_point', exit_point]], exit_point, candles_df, max_candles)

        # Routine for df_alta
        temp_exit.columns = [exit_point + '_dt', exit_point + '_saldo']

        # Concat exits
        if exits is None:
            exits = temp_exit
        else:
            exits = pd.concat([exits, temp_exit], axis=1)
        del temp_exit

    # Routine if for every trade an opposite trade is automatically an entry
    if is_virada:
        virada_df = virada(df)
        exits = pd.concat([exits, virada_df], axis=1)

    # Quick fix to generate entry points for AI
    else:
        temp_df = df[['entry_point']]
        temp_df.columns = ['entry']
        exits = pd.concat([exits, temp_df], axis=1)

    return exits

cdef build_entry_points(df, candles_df):
    """
    The new feeder routine that was created to deal with the issue that there were outputted candles that were not
    in the right possible timing, which helped remove the .update_method() from indicator logic, need to have a fix
    because we will have output at TimeStamps that have never existing in 1 Minute candles.

    For this reason some kind of routine was needed to fetch those trades that were created in minutes that are not
    part of the original Database.

    :param df: (pandas DataFrame) Containing exit points.

    :return: DataFrame with exit points along with close and entry_point values
    :rtype: pandas DataFrame
    """

    # Generates inner join DataFrame
    df_inner = pd.concat([candles_df[['close', 'entry_point']], df], join='inner', axis=1)

    # Finds exit points for elements outside the inner join DataFrame
    for element in df.index.difference(df_inner.index):
        # Selects 1 month prior to the DataFrame, which is the highest period we use
        w = candles_df.loc[element - pd.offsets.Day(31):element + pd.offsets.Minute(1)].iloc[-1][
            ['close', 'entry_point']]

        # Changes index to be able to concat correctly
        w.name = element

        # Creates line to be added
        x = pd.concat([df.loc[element], w])

        # Add line to DataFrame
        df_inner.loc[element] = x

    # Returns ordered DataFrame
    return df_inner.sort_index()

cdef mp(df, exit_point, candles_df_pd, max_candles):
    cdef tuple candles_index = tuple(candles_df_pd.index)
    cdef tuple candles_df = tuple(tuple(x) for x in candles_df_pd.itertuples())

    cpu = multiprocessing.cpu_count()
    dividers = [int(df.shape[0] / cpu * i) for i in range(1, cpu)]

    df_list = np.split(df, dividers, axis=0)

    index_start = [bisect.bisect_left(candles_index, df.index[0])] + [
        bisect.bisect_left(candles_index, df.index[divider]) for divider in dividers]
    index_end = [bisect.bisect_left(candles_index, df.index[divider - 1]) for divider in dividers] + [
        bisect.bisect_left(candles_index, df.index[-1])]

    df_list = [(tuple(tuple(x) for x in d.itertuples()), exit_point, candles_index[index_start[i]:index_end[i]],
                candles_df[index_start[i]:index_end[i] + max_candles], max_candles) for i, d in enumerate(df_list)]

    pool = multiprocessing.Pool()
    results = pool.map(dataframe_apply, df_list)
    pool.close()
    pool.join()

    # Filter to remove df with zero rows
    results = [df for df in results if df.shape[0] > 0]

    x = pd.concat(results)[[0, 1]]
    return x

cpdef dataframe_apply(dlist):
    df, ep_str, candles_index, candles_df, max_candles = dlist[0], dlist[1], dlist[2], dlist[3], dlist[4]

    cdef list raw_df = []
    cdef list index = []
    cdef datetime dt
    cdef double close
    cdef double entry_point
    cdef double exit_point

    for dt, close, entry_point, exit_point in df:
        pos = bisect.bisect_left(candles_index, dt)
        x = candles_df[pos:max_candles]
        raw_df.append(create_exits(dt, close, entry_point, exit_point, ep_str, x))
        index.append(dt)

    return pd.DataFrame(raw_df, index=index)

def create_exits(datetime dt, double close, double entry_point, double exitp, str exit_str, tuple remaining):
    """
    Calculate exit datetime for each possible exit point.

    :param df_line: Input df_line

    :return: pd.Series([Hora da Saida, Saldo])
    """

    if exitp < 0:
        exitp = exitp * -1

    # Evaluate if it is stop or not
    is_stop = 'stop' in exit_str

    # Evaluate if alta ou baixa
    is_high = close < exitp

    # Checks if it is not the last value
    if len(remaining) < 2:
        # Need to return series as this outputs a DataFrame when used in a DF.apply()
        return [np.datetime64('NaT'), 0.0]

    # Iter through DataFrame to find exit

    cdef datetime index
    cdef double open
    cdef double high
    cdef double low

    index, open, high, low = remaining[0]

    # Routine if high
    if is_high:
        if high >= exitp:
            if index == dt:
                if open >= exitp:
                    return [np.datetime64('NaT'), -1.0]

    # Routine if low
    else:
        if low <= exitp:
            if index == dt:
                if open <= exitp:
                    return [np.datetime64('NaT'), -1.0]

    # Iter through DataFrame to find exit
    for index, open, high, low in remaining[1:]:

        # Routine if high
        if is_high:
            if high >= exitp:
                exitp = max(open, exitp)
                saldo = exitp - entry_point

                if is_stop:
                    saldo = saldo * -1
                return [index, saldo]

        # Routine if low
        else:
            if low <= exitp:
                exitp = min(open, exitp)
                saldo = entry_point - exitp

                if is_stop:
                    saldo = saldo * -1
                return [index, saldo]

    # If no values found returns blank
    return [np.datetime64('NaT'), 0.0]

def consolidate_exits(asset, entry, exits, is_dentro):
    """
    Run exit consolidation routine and saves it to disk.
    """
    # Sort DataFrame
    exits.sort_index(inplace=True)

    # Instantiates DataFrame
    df = exits.apply(juntate_exits, axis=1, args=(is_dentro,))
    df.columns = ['exit_reference', 'exit_date', 'exit_saldo']

    # Sets filename
    filename = 'data/liquidation/' + asset + '_' + entry + '_CONSOLIDATE'

    # Save liquidation to disk
    save_liquidation_to_disk(filename, df)

def juntate_exits(df_line, is_dentro):
    """
    Gets a DataFrame line and evaluate what exit will it be.

    :param df_line: Input DF Line
    :return: Output DF Line containing:
        1. 'exit_reference' - String
        2. 'exit_date' - DateTime
        3. 'exit_saldo' - Float
    :rtype: pandas Series
    """
    # TODO evaluate last_trade logic
    last_trade = None

    # Dentro Routine
    if is_dentro and last_trade is not None and last_trade > df_line.name:
        return pd.Series(['', np.datetime64('NaT'), 0])

    # Creates DataFrame to be able to use select_dtypes function
    df = pd.DataFrame([df_line])

    if check_if_invalid_entry(df):
        return pd.Series(['', np.datetime64('NaT'), 0])

    # Select only dates
    include_dict = {'include': np.datetime64}  # Needed to bypass something in cython
    df = df.select_dtypes(**include_dict)

    # Select minimum dates
    selected_column = df.idxmin(axis=1).values[0]

    # If dates returns empty return empty
    if isinstance(selected_column, np.float64):
        return pd.Series(['', np.datetime64('NaT'), 0])

    # Get saldo column name
    selected_saldo = selected_column.replace('dt', 'saldo')

    last_trade = df_line[selected_column]

    # Generates output
    return pd.Series([selected_column, df_line[selected_column], df_line[selected_saldo]])

def check_if_invalid_entry(df_line):
    if not df_line.isin([-1]).values.any():
        return False
    else:
        selected_columns = df_line.columns[df_line.isin([-1]).values[0]]
        for column in selected_columns:
            selected_dt = column.replace('saldo', 'dt')
            if pd.isnull(df_line[selected_dt].values):
                return True
    return False

def save_liquidation_to_disk(filename, df):
    """
    Saves liquidation to disk in HDF5 format.

    :param filename: Selects filename to be saved
    :param df: DataFrame to be saved
    """
    # Remove liquidation File if exists
    if os.path.isfile(filename):
        os.unlink(filename)

    # Save liquidations to disk
    with pd.HDFStore(filename) as hdf:
        hdf.append(key='liquidation', value=df, format='table', data_columns=True)

def virada(df):
    # TODO virada is dependent on column order. improve this.
    output = []
    for index_a, close_a, ep_a, profit_a, stop_a in df.itertuples():
        for index_b, close_b, ep_b, profit_b, stop_b in df[index_a:].itertuples():
            if stop_a > 0:
                if stop_b < 0:
                    output.append([index_b, ep_b - ep_a, ep_a])
                    break
            else:
                if stop_b > 0:
                    output.append([index_b, ep_a - ep_b, ep_a])
                    break
        else:
            output.append([np.datetime64('NaT'), 0.0, ep_a])

    return pd.DataFrame(output, index=df.index, columns=['virada_dt', 'virada_saldo', 'entry'])
