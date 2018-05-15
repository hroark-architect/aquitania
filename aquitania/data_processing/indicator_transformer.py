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

Studying Transformers through 'Hands-On Machine Learning...' on 29/01/2018.
"""
import bisect

import numpy as np
import pandas as pd
import aquitania.resources.references as ref

from aquitania.data_processing.indicator_pipeline import IndicatorPipeLine
from aquitania.liquidation.spreads import ratio_with_spreads
from aquitania.resources.asset import AssetInfo


class IndicatorTransformer:
    def __init__(self, broker_instance, signal, currencies_list, n_ratio_bins=10, n_proba_bins=10):
        self.broker_instance = broker_instance
        self.signal = signal
        self.profit = signal.profit
        self.stop = signal.stop
        self.n_ratio_bins = n_ratio_bins
        self.ratio_bins, self.iratio_bins = None, None
        self.n_proba_bins = n_proba_bins
        self.proba_bins = None
        self.asset_info = AssetInfo(broker_instance, currencies_list)

    def transform(self, X, y):
        # Remove lines where it was not traded for real or not exited
        X = self.transform_x(X)
        not_traded = np.where(y['exit_saldo'] == 0, False, True)
        X = X[not_traded]
        y_pips = y[not_traded]['exit_saldo']
        y_date = y[not_traded]['exit_date']

        pipe = IndicatorPipeLine()
        X = pipe.fit_transform(X)

        # Create a proper result set
        y = pd.Series(np.where(y_pips > 0, True, False), name='results', index=X.index)
        currency_str = X['asset'].replace({v: k for v, k in enumerate(ref.currencies_list)})
        currency_str.name = 'currency_str'

        # TODO think about shuffling data as some learning algorithms may use order to overfit
        pd.concat([currency_str, X, y_date, y, y_pips], axis=1).to_csv('concat_df.csv')

        return X, y

    def transform_x(self, X):
        # Set signal column as True for buy as False for sell
        X['signal'] = X[self.profit] > 0

        # Remove datetime values from X
        X = X.select_dtypes(exclude=np.datetime64)

        # Generates entry column in case it doesn't exist
        if 'entry' not in X.columns:
            X['entry'] = X[self.signal.entry]

        # Adds Ratio Calculations
        X = self.add_ratio(X)

        # Removes columns related to exit points
        X = remove_exit_columns(X)

        return X

    def add_ratio(self, df):
        # TODO what to do when working with multiple possible exit points and entry points?
        # Create ratios
        df[['ratio', 'ratio_inverted']] = df.apply(self.ratio_w_spread, axis=1, args=(self.profit, self.stop))

        # Generate Bins in case it is building the backtest base
        self.ratio_bin_generation(df)

        # Ratios Bins Routine
        df['ratio'] = pd.cut(df['ratio'], bins=self.ratio_bins).cat.codes
        df['ratio_inverted'] = pd.cut(df['ratio_inverted'], bins=self.iratio_bins).cat.codes

        return df

    def ratio_w_spread(self, df_line, profit_id, stop_id):
        cur_obj = self.asset_info.dict[ref.currencies_list[df_line['asset']]]
        return pd.Series(ratio_with_spreads(df_line[profit_id], df_line[stop_id], df_line['entry'], cur_obj))

    def ratio_bin_generation(self, df):
        while self.ratio_bins is None:
            try:  # If there is a very big category with non-profitable trades it will throw an error of duplicate bins
                self.ratio_bins = generate_bins(df, 'ratio', self.n_ratio_bins)
                self.iratio_bins = generate_bins(df, 'ratio_inverted', self.n_ratio_bins)
            except:
                self.n_ratio_bins -= 1

    def transform_proba(self, df):
        # Generate Bins in case it is building the backtest base
        self.proba_bin_generation(df)
        df['prediction_proba'] = pd.cut(df['raw_predict'], bins=self.proba_bins).cat.codes

        return df

    def proba_bin_generation(self, df):
        while self.proba_bins is None:
            try:  # If there is a very big category with non-profitable trades it will throw an error of duplicate bins
                self.proba_bins = generate_bins(df, 'raw_predict', self.n_proba_bins)
            except:
                self.n_proba_bins -= 1

    def get_proba_bin(self, value):
        return get_bin_value(self.proba_bins, value)


def get_bin_value(bins, value):
    pos = bisect.bisect(bins, value) - 1
    return max(pos, 0)


def generate_bins(df, column_name, number_of_bins):
    _, bins = pd.qcut(df[column_name], number_of_bins, retbins=True, labels=False)
    bins[0], bins[-1] = -float(np.inf), float(np.inf)
    return bins


def remove_exit_columns(X):
    drop_columns = []
    for column in X.columns:
        if 'stop' in column or 'profit' in column or 'entry' in column or 'virada' in column or 'train' in column:
            drop_columns.append(column)
    X.drop(columns=drop_columns, inplace=True)
    return X
