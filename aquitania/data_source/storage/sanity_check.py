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

Library consisting of functions to check candles quality. 

There is still a lot of work to be done. These functions are able to identify anomalies with the data.
There aren't functions to correct those anomalies or to look for other data sources.
"""

import pandas as pd

# TODO refactor this method, maybe create a beautiful jupyter notebook from it. Most of this is legacy...

def low_daily_frequency(df):
    """
    Checks for weekdays that have less than 600 candles 'G01' OR
    Checks for sundays that have less than 60 candles 'G01'
    
    :df dataframe consisting of g01 candles
    :return dataframe containing days that have a low frequency of g01 candles
    :rtype dataframe
    """
    df = df.new_year
    df = df.dropna(how='any')

    xmas = (df.index.month == 12) & (df.index.day == 25)
    new_year = (df.index.month == 1) & (df.index.day == 1)

    sunday_condition = ((df.index.weekday != 6) & (df['volume'] < 600)) & ~(xmas | new_year)
    not_sunday_condition = ((df.index.weekday == 6) & (df['volume'] < 60)) & ~(xmas | new_year)

    df = df.loc[sunday_condition | not_sunday_condition]
    return df


def check_gaps(df):
    """
    Checks for gaps wider than x pips.
    Doesn't take sunday gaps into consideration.
    
    :x reference amount of pips to measure the gap size that will be selected
    :df dataframe consisting of any kind of candles
    :return dataframe containing candles that opened with a gap of x in relation to previous candle
    :rtype dataframe
    """
    df['oldIndex'] = df.index
    df['oldIndex'] = df['oldIndex'].shift(1)
    df['oldClose'] = df['close'].shift(1)
    df['gap'] = (df['open'] - df['oldClose']) * [10000]
    df = df.loc[(df['gap'] > 10) & (df.index.year > 2004) & (df.index.weekday != 6)]
    return df


def x_hour_gaps(x, df):
    xmas = (df.index.month == 12) & (df.index.day == 25)
    new_year = (df.index.month == 1) & (df.index.day == 1)
    xmas_a = (df.index.month == 12) & (df.index.day == 26)
    new_year_a = (df.index.month == 1) & (df.index.day == 2)

    df['oldIndex'] = df.index
    df['oldIndex'] = df['oldIndex'].shift(1)
    df['timeGap'] = (df.index - df['oldIndex']).astype('timedelta64[h]')
    return df.loc[(df.index.weekday != 6) & (df['timeGap'] >= x) & ~(xmas | new_year | xmas_a | new_year_a)]


def x_pct_osc(x, df):
    df['osc'] = (df['high'] - df['low'])
    df['oscPct'] = df['osc'] / df['high'] * 100
    df = df.loc[(df['oscPct'] > x)]
    return df


def clean_bad_old_candles(df):
    aux_df = df.groupby(pd.Grouper(freq='D', level=0, label='left')).agg({'volume': 'count'})
    aux_df = aux_df.loc[(aux_df['volume']) > 30]
    start_date = aux_df.index[0]
    df = df.loc[start_date:]
    return df


def remove_duplicates(df):
    df = df[~df.index.duplicated(keep='first')]
    return df


def basic_sanitizer(df):
    df = remove_duplicates(df)
    df = df.dropna(how='any')
    df.sort_index(inplace=True)
    df = clean_bad_old_candles(df)
    return df
