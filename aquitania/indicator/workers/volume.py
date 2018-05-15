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

These was one of the first indicators ever to be evaluated. At some point I was getting too much overfitting in the AI
models, that I've decided to turn this indicator into a categorical one instead of a continuous one.
"""
from aquitania.indicator.abstract.indicator_output_abc import AbstractIndicatorOutput
from collections import *


class Volume(AbstractIndicatorOutput):
    """
    Volume is a categorical indicator to evaluate the volume. It has to categories, one for absolute volume to be able
    to compare between assets, and a relative volume to be able to make a intra-indicator comparison.

    Absolute volume is a measure of how many digits does the volume have, and relative volume is a ratio by the moving
    average of the volume.

    It is important to note that Volume implementation is dependent on how the broker generates volume data. For both
    Oanda and FXCM, which are the brokers used int 07th May 2018, Volumes are calculated through a tick quantity proxy.
    """

    def __init__(self, obs_id, period):
        """
        Instantiates Volume Indicator.

        :param obs_id: (str) Indicator Name
        :param period: (int) Number of periods to be observed
        """
        # Instantiates AbstractIndicatorOutput
        super().__init__(obs_id, ['abs_len', 'rel'], False, (0, -1))

        # Instantiates necessary variables
        self.mm = deque(maxlen=period)  # maxlen is a trick to adjust len automatically
        self.period = period

    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.
        """
        # Gets a proxy for absolute value, it only measures the order of magnitude (quantity of digits)
        abs_vol = int(candle.volume)

        # Instantiates a relative value for volume, -1 means it is not instantiated
        rel_vol = -1

        # Appends volume to deque
        self.mm.append(candle.volume)

        # If deque is of appropriate size, generates output
        if len(self.mm) == self.period:

            # Gets average
            avg = sum(self.mm) / self.period

            # Calculates relative volume in relation to average
            rel_vol = candle.volume / avg

        # Returns Absolute and Relative volume
        return abs_vol, rel_vol
