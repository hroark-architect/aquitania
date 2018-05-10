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
from aquitania.indicator.workers.rsi import RSI
from aquitania.indicator.workers.bollinger_bands import BollingerBands
from aquitania.indicator.signal.doji import Doji
from aquitania.strategies.strategies_abc import Strategy
from aquitania.indicator.workers.volume import Volume


class ExampleStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def monthly_obs(self):
        """
        Gets all the observers of 'MS' timestamp.

        :return: List of Observers of 'MS' timestamp
        """

        return []

    def weekly_obs(self):
        """
        Gets all the observers of 'W-SUN' timestamp.

        :return: List of Observers of 'W-SUN' timestamp
        """

        return []

    def daily_obs(self):
        """
        Gets all the observers of 'D' timestamp.

        :return: List of Observers of 'D' timestamp
        """
        sma = BollingerBands('f_bb', 25)

        return [sma]

    def g60_obs(self):
        """
        Gets all the observers of 'Min60' timestamp.

        :return: List of Observers of 'Min60' timestamp
        """

        volume = Volume('e_volume', 25)

        return [volume]

    def g30_obs(self):
        """
        Gets all the observers of 'Min30' timestamp.

        :return: List of Observers of 'Min30' timestamp
        """

        # Extremist indicator needs to be loaded before anything that uses count_ext

        self.signal = Doji('d_doji')

        return [self.signal]

    def g15_obs(self):
        """
        Gets all the observers of 'Min15' timestamp.

        :return: List of Observers of 'Min15' timestamp
        """

        return []

    def g05_obs(self):
        """
        Gets all the observers of 'Min5' timestamp.

        :return: List of Observers of 'Min5' timestamp
        """

        rsi = RSI('b_rsi', 25)

        return [rsi]

    def g01_obs(self):
        """
        Gets all the observers of 'Min1' timestamp.

        :return: List of Observers of 'Min1' timestamp
        """

        return []
