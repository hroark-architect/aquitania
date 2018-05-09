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

01/05/2018 - It was refactored to be placed inside Oracle.
"""

import pandas as pd
import bisect


class OracleCriteria:
    """
    This is the internal criteria the Oracle uses to decide whether one of his predictions should be a trade or not, and
    also how big of a bet we should make on this trade.
    """

    def __init__(self, transformer, bet_sizing_dict, i_bet_sizing_dict):
        """
        This initializes the Criteria object with the necessary requirements for it to do its job.

        It needs both bet sizing truth tables for normal and inverse values. And also it needs a transformer object to
        be able to convert probabilities and ratios into truth table interpretable values.

        :param transformer: (IndicatorTransformer) used when backtesting and creating the strategies
        :param bet_sizing_dict: (pandas DataFrame) truth table for bet sizing for normal trades
        :param i_bet_sizing_dict: (pandas DataFrame) truth table for bet sizing for inverted trades
        """
        self.transformer = transformer
        self.bet_sizing_dict = bet_sizing_dict
        self.i_bet_sizing_dict = i_bet_sizing_dict

    def met(self, proba, ratio, inverse_ratio):
        """
        Evaluates if a certain 'proba' and a certain 'ratio' have met the criteria of a particular truth table.

        If the criteria has been met, it will generate an output containing bet size and brackets information.

        :param proba: (int) Proba bracket
        :param ratio: (int) Ratio bracket
        :param inverse_ratio: (int) Inverse ratio bracket

        :return: tuple containing 5 elements:
            make_trade (bool): True if trade
            is_inverted (bool): True if trade needs to be inverted
            size (float): order size
            proba (int): bracket of probability
            used_ratio (int): bracket of ratio
        :rtype: tuple of 5 elements
        """
        # Calculates bet sizing for normal trades
        nbs = bet_sizing(self.bet_sizing_dict, proba, ratio)

        # Calculates bet sizing for inverted trades
        ibs = bet_sizing(self.i_bet_sizing_dict, proba, inverse_ratio)

        # Evaluates if the trade is normal or inverted
        if nbs >= ibs:

            # Sets variables for normal trade
            size, used_ratio, is_inverted = nbs, ratio, False

        else:
            # Sets variables for inverted trade
            size, used_ratio, is_inverted = ibs, inverse_ratio, True

        # Sets if there is a valid trade
        make_trade = True if size > 0 else False

        # Returns Oracle predictions about input conditions
        return make_trade, is_inverted, size, proba, used_ratio


def bet_sizing(bs_dict, proba, ratio):
    """
    Gets bet sizing given a bet sizing dictionary and prediction proba and ratio brackets.
    :param bs_dict: (pandas DataFrame) truth table for bet sizing 
    :param proba: (int) Proba bracket
    :param ratio: (int) Ratio bracket

    :return: Bet Sizing for given 'predict_proba' and 'ratio' bracket given a truth table
    :rtype: float
    """
    # Selects bet sizing given specific brackets
    return bs_dict.loc[proba, ratio]
