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

import random

import pandas as pd

from aquitania.brains.statistics.util import trade_sequence_returns


def monte_carlo_bets(proba_win, bet_sizing, ratio, sample_size, number_of_trials):
    # Instantiates the master list that will hold the output of each run
    master = []

    # Establishes the parameters for number of runs
    for x in range(0, number_of_trials):
        # Parameters for current run
        total_return = [1 if proba_win >= random.uniform(0, 1) else 0 for i in range(0, int(sample_size))]
        master.append(trade_sequence_returns(len(total_return), sum(total_return), bet_sizing, ratio))

    return pd.Series(master)
