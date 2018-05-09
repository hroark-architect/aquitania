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

Module added on 28/04/2018 to work with confidence intervals.
"""

from statsmodels.stats.proportion import proportion_confint


def lower_confidence_interval_99(n_success, n_trials):
    normal = proportion_confint(n_success, n_trials, 0.01)[0]
    beta = proportion_confint(n_success, n_trials, 0.01, 'beta')[0]
    return min(normal, beta)


def trade_sequence_returns(n_trades, win_trades, bet_sizing, ratio):
    balance = 1
    losing_trades = n_trades - win_trades
    balance *= (1 - bet_sizing) ** losing_trades
    balance *= (1 + (ratio * bet_sizing)) ** win_trades
    return balance


def ci_99_inverse_or_not(inverse, n_trades, n_win_trades):
    n_win_trades = n_win_trades_inverse_or_not(inverse, n_trades, n_win_trades)
    return lower_confidence_interval_99(n_win_trades, n_trades)


def n_win_trades_inverse_or_not(inverse, n_trades, n_win_trades):
    if inverse:
        return n_trades - n_win_trades
    else:
        return n_win_trades
