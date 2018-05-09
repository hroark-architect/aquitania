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

import math as m
import numpy as np


def kelly_criterion(win_loss_ratio, win_probability):
    """
    Calculates optimal bet sizing according to the Kelly Criterion.

    :param win_probability: Probability to win a bet.
    :param win_loss_ratio: Reward in relation to loss size (1.5 means that the wins are 150% the size of the losses).

    :return: Kelly Criterion Optimal Bet Size
    :rtype: Float
    """
    # if self.win_loss_ratio == 0:
    # return 0

    if win_loss_ratio == 0:
        return 0.0

    kelly = expected_value(win_loss_ratio, win_probability) / win_loss_ratio

    if kelly < 0:
        return 0.0

    return kelly


def adjusted_kelly_criterion(win_loss_ratio, win_probability):
    """
    This is the adjusted Kelly Criterion as in Thorp's book that most people on finance markets use when they are
    not that sure that the probabilities are in fact exact.

    Serves to calculate optimal bet sizing accounting for possible error and biases in probability estimates.

    :return: Half of the Kelly Criterion Optimal Bet Size
    :rtype: Float
    """

    return kelly_criterion(win_loss_ratio, win_probability) / 2


def expected_value(win_loss_ratio, win_probability):
    """
    Calculates expected value of a bet.

    :return: Returns expected value.
    :rtype: Float
    """
    return win_loss_ratio * win_probability - (1 - win_probability)


def multiple_expected_values(list_of_wl_ratio, list_of_win_trades, list_of_count):
    total, value = 0, 0.0

    for wl_ratio, win_count, count in zip(list_of_wl_ratio, list_of_win_trades, list_of_count):
        win_proba = win_count / count
        value += expected_value(wl_ratio, win_proba) * count
        total += count

    return value / total


def calculate_rate_of_return(bet_sizing, win_loss_ratio, win_probability):
    """
    Calculate rate of return of bets, as stated in:

    http://www.elem.com/~btilly/kelly-criterion/#rate_example

    This method is really interesting because it account for drawdown influence in the profitability of the
    strategy.

    Calculates bet sizing according to Kelly Criterion.

    :param bet_sizing: (float) Bet sizing - Minimum value is 0, Maximum is 1

    :return: Returns the expected rate of return
    :rtype: Float
    """

    lose_amount = bet_sizing

    # Kelly criterion throws negative values if you have a losing situation

    if lose_amount == 1:
        return 1

    win_amount = lose_amount * win_loss_ratio

    lose_log = m.log(1 - lose_amount, m.e)
    win_log = m.log(1 + win_amount, m.e)

    rr = m.exp((1 - win_probability) * lose_log + win_probability * win_log) - 1

    return rr

