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

import numpy as np
import pandas as pd

dict_tbltimestamp_to_minutes = {"g01": 1, "g05": 5, "g15": 15, "g60": 60}

tsCodeToTableColumn_list = ["g01", "g05", "g15", "g60"]

currencies_dict = {"AUD_CAD": 0, "AUD_CHF": 1, "AUD_HKD": 2, "AUD_JPY": 3, "AUD_NZD": 4, "AUD_SGD": 5, "AUD_USD": 6,
                   "CAD_CHF": 7, "CAD_HKD": 8, "CAD_JPY": 9, "CAD_SGD": 10, "CHF_HKD": 11, "CHF_JPY": 12, "CHF_ZAR": 13,
                   "EUR_AUD": 14, "EUR_CAD": 15, "EUR_CHF": 16, "EUR_CZK": 17, "EUR_DKK": 18, "EUR_GBP": 19,
                   "EUR_HKD": 20, "EUR_HUF": 21, "EUR_JPY": 22, "EUR_NOK": 23, "EUR_NZD": 24, "EUR_PLN": 25,
                   "EUR_SEK": 26, "EUR_SGD": 27, "EUR_TRY": 28, "EUR_USD": 29, "EUR_ZAR": 30, "GBP_AUD": 31,
                   "GBP_CAD": 32, "GBP_CHF": 33, "GBP_HKD": 34, "GBP_JPY": 35, "GBP_NZD": 36, "GBP_PLN": 37,
                   "GBP_SGD": 38, "GBP_USD": 39, "GBP_ZAR": 40, "HKD_JPY": 41, "NZD_CAD": 42, "NZD_CHF": 43,
                   "NZD_HKD": 44, "NZD_JPY": 45, "NZD_SGD": 46, "NZD_USD": 47, "SGD_CHF": 48, "SGD_HKD": 49,
                   "SGD_JPY": 50, "TRY_JPY": 51, "USD_CAD": 52, "USD_CHF": 53, "USD_CNH": 54, "USD_CZK": 55,
                   "USD_DKK": 56, "USD_HKD": 57, "USD_HUF": 58, "USD_INR": 59, "USD_JPY": 60, "USD_MXN": 61,
                   "USD_NOK": 62, "USD_PLN": 63, "USD_SAR": 64, "USD_SEK": 65, "USD_SGD": 66, "USD_THB": 67,
                   "USD_TRY": 68, "USD_ZAR": 69, "ZAR_JPY": 70}

currencies_list = ["AUD_CAD", "AUD_CHF", "AUD_HKD", "AUD_JPY", "AUD_NZD", "AUD_SGD", "AUD_USD", "CAD_CHF", "CAD_HKD",
                   "CAD_JPY", "CAD_SGD", "CHF_HKD", "CHF_JPY", "CHF_ZAR", "EUR_AUD", "EUR_CAD", "EUR_CHF", "EUR_CZK",
                   "EUR_DKK", "EUR_GBP", "EUR_HKD", "EUR_HUF", "EUR_JPY", "EUR_NOK", "EUR_NZD", "EUR_PLN", "EUR_SEK",
                   "EUR_SGD", "EUR_TRY", "EUR_USD", "EUR_ZAR", "GBP_AUD", "GBP_CAD", "GBP_CHF", "GBP_HKD", "GBP_JPY",
                   "GBP_NZD", "GBP_PLN", "GBP_SGD", "GBP_USD", "GBP_ZAR", "HKD_JPY", "NZD_CAD", "NZD_CHF", "NZD_HKD",
                   "NZD_JPY", "NZD_SGD", "NZD_USD", "SGD_CHF", "SGD_HKD", "SGD_JPY", "TRY_JPY", "USD_CAD", "USD_CHF",
                   "USD_CNH", "USD_CZK", "USD_DKK", "USD_HKD", "USD_HUF", "USD_INR", "USD_JPY", "USD_MXN", "USD_NOK",
                   "USD_PLN", "USD_SAR", "USD_SEK", "USD_SGD", "USD_THB", "USD_TRY", "USD_ZAR", "ZAR_JPY"]

cur_ordered_by_spread = ['EUR_USD', 'USD_JPY', 'GBP_USD', 'USD_CAD', 'EUR_JPY', 'GBP_JPY', 'EUR_CAD', 'AUD_USD',
                         'EUR_AUD', 'AUD_JPY', 'EUR_HKD', 'HKD_JPY', 'CAD_JPY', 'GBP_HKD', 'EUR_GBP', 'USD_CHF',
                         'GBP_AUD', 'CAD_HKD', 'GBP_CAD', 'NZD_USD', 'AUD_HKD', 'GBP_NZD', 'EUR_NZD', 'USD_DKK',
                         'AUD_CAD', 'NZD_JPY', 'NZD_HKD', 'GBP_CHF', 'USD_CNH', 'CHF_HKD', 'EUR_CHF', 'NZD_CAD',
                         'CHF_JPY', 'CAD_CHF', 'USD_MXN', 'USD_SGD', 'AUD_NZD', 'AUD_CHF', 'GBP_SGD', 'NZD_CHF',
                         'CAD_SGD', 'SGD_JPY', 'USD_SEK', 'USD_NOK', 'EUR_SGD', 'NZD_SGD', 'EUR_NOK', 'AUD_SGD',
                         'SGD_HKD', 'SGD_CHF', 'USD_ZAR', 'USD_TRY', 'GBP_ZAR', 'EUR_SEK', 'EUR_ZAR', 'CHF_ZAR',
                         'USD_CZK', 'USD_PLN', 'EUR_TRY', 'TRY_JPY', 'USD_HKD', 'GBP_PLN', 'USD_HUF', 'ZAR_JPY',
                         'EUR_PLN', 'EUR_HUF', 'EUR_CZK', 'USD_INR', 'EUR_DKK', 'USD_THB', 'USD_SAR']

all_instruments_list = ['WHEAT_USD', 'AUD_CHF', 'XAG_SGD', 'EUR_GBP', 'CHF_ZAR', 'US2000_USD', 'XAU_USD', 'USB02Y_USD',
                        'USD_SEK', 'GBP_SGD', 'CORN_USD', 'EUR_CAD', 'HK33_HKD', 'USD_SAR', 'GBP_CAD', 'XAU_GBP',
                        'ZAR_JPY', 'USD_TRY', 'GBP_JPY', 'USB05Y_USD', 'USD_ZAR', 'NATGAS_USD', 'CAD_HKD', 'USD_INR',
                        'AUD_JPY', 'CN50_USD', 'XAG_AUD', 'TWIX_USD', 'EUR_CZK', 'AUD_SGD', 'XAU_JPY', 'NZD_CAD',
                        'SGD_CHF', 'US30_USD', 'USD_HKD', 'USD_CHF', 'EUR_HKD', 'UK10YB_GBP', 'XAG_EUR', 'USD_CZK',
                        'NZD_HKD', 'SOYBN_USD', 'USD_DKK', 'AUD_HKD', 'XAG_USD', 'XAU_XAG', 'SPX500_USD', 'EU50_EUR',
                        'XAG_CHF', 'USD_NOK', 'XAU_EUR', 'EUR_PLN', 'SGD_JPY', 'GBP_NZD', 'XAU_SGD', 'XAU_CAD',
                        'NZD_CHF', 'XAG_NZD', 'EUR_JPY', 'EUR_USD', 'CAD_JPY', 'NZD_SGD', 'NL25_EUR', 'EUR_HUF',
                        'HKD_JPY', 'USD_HUF', 'XAG_GBP', 'SG30_SGD', 'XAG_HKD', 'SUGAR_USD', 'USD_CAD', 'BCO_USD',
                        'XCU_USD', 'DE30_EUR', 'NAS100_USD', 'EUR_ZAR', 'NZD_JPY', 'AUD_CAD', 'EUR_NOK', 'NZD_USD',
                        'XAU_HKD', 'GBP_ZAR', 'CHF_JPY', 'UK100_GBP', 'XAU_AUD', 'CAD_CHF', 'CAD_SGD', 'EUR_SGD',
                        'XAG_CAD', 'USB30Y_USD', 'XAU_CHF', 'DE10YB_EUR', 'WTICO_USD', 'EUR_TRY', 'USD_JPY', 'CHF_HKD',
                        'AU200_AUD', 'SGD_HKD', 'XAU_NZD', 'USD_PLN', 'GBP_AUD', 'GBP_HKD', 'EUR_CHF', 'EUR_SEK',
                        'USD_SGD', 'XPD_USD', 'GBP_PLN', 'EUR_NZD', 'XPT_USD', 'AUD_USD', 'XAG_JPY', 'USB10Y_USD',
                        'IN50_USD', 'GBP_USD', 'USD_MXN', 'JP225_USD', 'USD_CNH', 'TRY_JPY', 'GBP_CHF', 'USD_THB',
                        'FR40_EUR', 'EUR_DKK', 'AUD_NZD', 'EUR_AUD']

currency_list = ['AUD', 'CAD', 'CHF', 'CNH', 'CZK', 'DKK', 'EUR', 'GBP', 'HKD', 'HUF', 'INR', 'JPY', 'MXN', 'NOK',
                 'NZD', 'PLN', 'SAR', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']

ohlc_dict = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}

data_folders = ['data/ai', 'data/model_manager', 'data/indicator', 'data/order_manager', 'data/state', 'data/liquidation']

ts_to_letter = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']


def tsCodeToTableColumn(ts):
    return tsCodeToTableColumn_list[ts]


downsample_ts_range = ['1Min', '5Min', '15Min', '60Min', 'D', 'W-SUN', 'MS']

timestampreverse_dict = {'1Min': 0, '5Min': 1, '15Min': 2, '60Min': 3, 'D': 4, 'W-SUN': 5, 'MS': 6}


def downsample_pandas_df(df, to_ts):
    if isinstance(to_ts, int):
        to_ts = timestampreverse_dict[to_ts]

    df['volume'] = df['volume'].astype(np.int32)

    if to_ts == '1Min':
        return df

    df = df.groupby(pd.Grouper(freq=to_ts, level=0, label='left')).agg(ohlc_dict)
    df = df.dropna(how='any')
    df['volume'] = df['volume'].astype(np.int32)
    return df


def get_start_date(broker_instance, currency):
    if isinstance(currency, int):
        currency = currencies_list[currency]
    df = broker_instance.load_data(currency)
    return df.index[0]


def build_timestamps(df):
    list_of_dfs = [df]
    for ts in downsample_ts_range[1:]:
        list_of_dfs.append(downsample_pandas_df(df, ts))
    return list_of_dfs
