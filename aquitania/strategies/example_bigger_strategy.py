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


class ExampleBiggerStrategy(Strategy):

    def __init__(self):
        super().__init__()

    def monthly_obs(self):
        """
        Gets all the observers of 'MS' timestamp.

        :return: List of Observers of 'MS' timestamp
        """
        volume = Volume('h_volume', 25)
        sma = BollingerBands('h_bb', 25)
        rsi = RSI('h_rsi', 25)

        return [volume, sma, rsi]

    def weekly_obs(self):
        """
        Gets all the observers of 'W-SUN' timestamp.

        :return: List of Observers of 'W-SUN' timestamp
        """

        volume = Volume('g_volume', 25)
        sma = BollingerBands('g_bb', 25)
        rsi = RSI('g_rsi', 25)

        return [volume, sma, rsi]

    def daily_obs(self):
        """
        Gets all the observers of 'D' timestamp.

        :return: List of Observers of 'D' timestamp
        """
        volume = Volume('f_volume', 25)
        sma = BollingerBands('f_bb', 25)
        rsi = RSI('f_rsi', 25)

        return [volume, sma, rsi]

    def g60_obs(self):
        """
        Gets all the observers of 'Min60' timestamp.

        :return: List of Observers of 'Min60' timestamp
        """

        volume = Volume('e_volume', 25)
        sma = BollingerBands('e_bb', 25)
        rsi = RSI('e_rsi', 25)

        return [volume, sma, rsi]

    def g30_obs(self):
        """
        Gets all the observers of 'Min30' timestamp.

        :return: List of Observers of 'Min30' timestamp
        """

        # Extremist indicator needs to be loaded before anything that uses count_ext

        volume = Volume('d_volume', 25)
        sma = BollingerBands('d_bb', 25)
        rsi = RSI('d_rsi', 25)

        return [volume, sma, rsi]

    def g15_obs(self):
        """
        Gets all the observers of 'Min15' timestamp.

        :return: List of Observers of 'Min15' timestamp
        """

        volume = Volume('c_volume', 25)
        sma = BollingerBands('c_bb', 25)
        rsi = RSI('c_rsi', 25)

        return [volume, sma, rsi]

    def g05_obs(self):
        """
        Gets all the observers of 'Min5' timestamp.

        :return: List of Observers of 'Min5' timestamp
        """

        volume = Volume('b_volume', 25)
        sma = BollingerBands('b_bb', 25)
        rsi = RSI('b_rsi', 25)

        return [volume, sma, rsi]

    def g01_obs(self):
        """
        Gets all the observers of 'Min1' timestamp.

        :return: List of Observers of 'Min1' timestamp
        """

        volume = Volume('a_volume', 25)
        sma = BollingerBands('a_bb', 25)
        rsi = RSI('a_rsi', 25)
        self.signal = Doji('a_doji')

        return [volume, sma, rsi, self.signal]
