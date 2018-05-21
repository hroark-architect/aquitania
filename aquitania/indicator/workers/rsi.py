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
from collections import deque

from aquitania.indicator.abstract.indicator_output_abc import AbstractIndicatorOutput


class RSI(AbstractIndicatorOutput):
    """
     The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.
     RSI oscillates between zero and 100. Traditionally, and according to Wilder, RSI is considered overbought when 
     above 70 and oversold when below 30. 
    """

    def __init__(self, obs_id, period):
        """
        Initializes the Indicator, setting indicator named and number of candles to be observed.

        :param obs_id: (str) Indicator Name
        :param period: (int) Sets number of periods that will be evaluated
        """
        # Initiates variables to instantiate super()
        columns = ['']
        is_open = False
        last_output = (-1,)

        # Instantiates super().__init__
        super().__init__(obs_id, columns, is_open, last_output)

        # Instantiate attributes
        self.period = period
        self.high = deque(maxlen=period)
        self.low = deque(maxlen=period)
        self.last_close = None

    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.
        """
        # Initializes close diff
        close_diff = candle.close[1] - self.last_close if self.last_close is not None else 0

        # Saves diff to 'self.high' if green candle
        if close_diff > 0:
            self.high.append(close_diff)
        # Saves diff to 'self.low' if red candle
        elif close_diff < 0:
            self.low.append(abs(close_diff))

        # Checks if there are enough periods instantiated for both 'self.high' and 'self.low'
        if self.period == len(self.high) == len(self.low):
            # Calculates Relative Strength
            rs = sum(self.high) / sum(self.low)

            # Calculates Relative Strength Index
            rsi = 100 - (100 / (1 + rs))

        else:
            # Saves Values for invalid RSI
            rsi = -1

        # Sets last close for next loop
        self.last_close = candle.close[1]

        # Returns RSI in form of a 1 element tuple (mandatory for indicators)
        return (rsi,)
