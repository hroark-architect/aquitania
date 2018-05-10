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
import os
import pandas as pd

from aquitania.data_processing.util import generate_folder


class OracleManager:
    """
    The OracleManager is a class to run_model the Oracle.

    It will get the Oracle predictions and take actions from it, such as make trades, record trades in a database.
    """
    def __init__(self, oracle, order_manager):
        self.oracle = oracle
        self.order_manager = order_manager

    def consult_oracle(self, df_input):
        raw_input = pd.DataFrame([df_input])
        ai_input = self.oracle.transformer.transform_x(raw_input)
        self.make_trade(raw_input, ai_input)

    def make_trade(self, raw_input, ai_input):
        # TODO work on inverted trade routines
        make_trade, invert_trade, size, proba, ratio = self.oracle.predict(ai_input)

        if make_trade:
            df = self.new_order(raw_input, size, invert_trade)
            df.index = raw_input.index
            raw_input = pd.concat([raw_input, df], axis=1)
            raw_input[['proba_bracket', 'ratio_bracket', 'bracket_size']] = pd.DataFrame([[proba, ratio, size]])
            record_trade(raw_input)

    def new_order(self, output, size, invert_trade):
        idx = output.index[0]
        finsec = output.loc[idx, 'asset']
        profit = output.loc[idx, self.oracle.signal.profit]
        stop = output.loc[idx, self.oracle.signal.stop]
        entry = output.loc[idx, self.oracle.signal.entry]

        if invert_trade:
            is_buy = stop > 0
        else:
            is_buy = stop < 0

        return self.order_manager.new_order(finsec, is_buy, size, stop, profit, entry)


def record_trade(df):
    generate_folder('data/trade_record/')
    if not os.path.exists('data/trade_record/live_trades.csv'):
        df.to_csv('data/trade_record/live_trades.csv')
    else:
        with open('data/trade_record/live_trades.csv', 'a') as f:
            df.to_csv(f, header=False)
