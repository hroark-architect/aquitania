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

03/05/2018 - Added to project. Playing around with technical indicators.
"""
from aquitania.indicator.abstract.indicator_output_abc import AbstractIndicatorOutput
from collections import *
from statistics import *


class EMA(AbstractIndicatorOutput):
    def __init__(self, obs_id, period, rate_of_decay):
        super().__init__(obs_id, ['alta'], False, (2,))
        self.ma = deque(maxlen=period)
        self.period = period
        self.rate_of_decay = rate_of_decay
        self.divider = sum([1 * ((1 - rate_of_decay) ** i) for i in range(period)])

    def indicator_logic(self, candle):
        # Initialize variables
        ema = 2  # 'ema' = 2 is clever way to generate 'a favor' e 'contra'

        # Append close to moving average
        self.ma.append(candle.close[self.up])

        # Check if there are enough candles to calculate moving average
        if len(self.ma) == self.period:
            # Calculates sum of weighted closes
            sum_ = sum([close * ((1 - self.rate_of_decay) ** i) for i, close in enumerate(reversed(self.ma))])

            # Gets average of weighted closes
            avg = sum_ / self.divider

            # Tells if current close is above moving average
            ema = 1 if candle.close[self.up] > avg else 0

        # Returns values
        return ema
