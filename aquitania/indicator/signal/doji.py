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
from aquitania.indicator.signal.abstract_signal import AbstractSignal


class Doji(AbstractSignal):
    """
    Technical Analysis Doji Candle Pattern.
    """

    def __init__(self, obs_id):
        # Instantiates Variables
        columns = ['ok', 'profit', 'stop', 'entry']
        is_open = False
        last_output = (False, 0.0, 0.0, 0.0)

        # Initializes AbstractSignal
        super().__init__(obs_id, columns, is_open, last_output)

    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.
        """
        profit, loss, entry = 0.0, 0.0, 0.0

        self.up = candle.upper_shadow(up=True) < candle.lower_shadow(up=True)

        # Check if it is a Doji
        is_ok = candle.is_doji(self.up)

        if is_ok:
            # Generate Exit points
            loss = candle.low[self.up]
            profit = candle.num_profit(candle.close[self.up] - loss, self.up)
            entry = candle.close[self.up]

        return is_ok, profit, loss, entry
