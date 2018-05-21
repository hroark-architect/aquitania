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
from aquitania.indicator.abstract.indicator_output_abc import AbstractIndicatorOutput
from collections import *
from statistics import *


class BollingerBands(AbstractIndicatorOutput):
    """
    """

    def __init__(self, obs_id, period):
        super().__init__(obs_id, ['direction', 'upper_tied', 'lower_tied'], False, (2, -1, -1))
        self.ma = deque(maxlen=period)
        self.period = period

    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.
        * Middle Band = 20-day simple moving average (SMA)
        * Upper Band = 20-day SMA + (20-day standard deviation of price x 2)
        * Lower Band = 20-day SMA - (20-day standard deviation of price x 2)
        """
        # Initialize variables
        sma, upper, lower = 2, -1, -1  # 'sma' = 2 is clever way to generate 'a favor' e 'contra'

        # Append close to moving average
        self.ma.append(candle.close[self.up])

        # Check if there are enough candles to calculate moving average
        if len(self.ma) == self.period:

            # Initialize upper and lower values for when there is a valid moving average
            upper, lower = 0.0, 0.0

            # Calculates moving average
            avg = sum(self.ma) / self.period

            # Tells if current close is above moving average
            sma = 1 if candle.close[self.up] > avg else 0

            # Calculates standard deviation
            std = pstdev(self.ma)

            # Calculates difference between current candle and moving average
            diff = candle.close[self.up] - avg

            # Transform difference to standard deviations
            if diff > 0 and std != 0:
                # Value of above
                upper = diff / std
            elif diff < 0 and std != 0:
                # Value if below
                lower = -diff / std

        # Returns values
        return sma, upper, lower
