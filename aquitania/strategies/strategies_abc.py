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

As of 11/05/2018, this class is only working as an Abstract Class, but it soon will be turned into a class with its own
behavior, just need to make a proper way to instantiate it with a dict of lists of Indicators or similar structure.
"""


# TODO make an indicator output/state for each strategy
class Strategy:

    # TODO make instantiation more powerful, pass a dict of indicators as input and make it work
    def __init__(self):
        """
        Instantiates a Strategy.

        self.signal is a mandatory attribute, and it guides the exit building block.
        """
        # TODO turn signal into a de facto list
        self.signal = []
        self.indicator_list = self.gen_indicator_list()

    def gen_indicator_list(self):
        """
        Each element in the main list is a given timestamp.
            Inside this element there is a list of observers for that given timestamp.

        :return: List of Lists of Observers
        :rtype: List of Lists of Observers
        """

        # Order seems retarded but it is important
        # TODO make it customizable as to what kind of candles to use
        monthly = self.monthly_obs()
        weekly = self.weekly_obs()
        daily = self.daily_obs()
        g60 = self.g60_obs()
        g30 = self.g30_obs()
        g15 = self.g15_obs()
        g05 = self.g05_obs()
        g01 = self.g01_obs()

        # Returns the built list
        return [g01, g05, g15, g30, g60, daily, weekly, monthly]

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

        return []

    def g60_obs(self):
        """
        Gets all the observers of 'Min60' timestamp.

        :return: List of Observers of 'Min60' timestamp
        """

        return []

    def g30_obs(self):
        """
        Gets all the observers of 'Min30' timestamp.

        :return: List of Observers of 'Min30' timestamp
        """

        return []

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

        return []

    def g01_obs(self):
        """
        Gets all the observers of 'Min1' timestamp.

        :return: List of Observers of 'Min1' timestamp
        """

        return []
