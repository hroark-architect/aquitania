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

This is one of the first and most basic classes.

It serves as structure for all indicators.

On 28/11/2017 I refactored this class to remove getters and setters. Notice that there are still two setters on this
code but they do other things besides simply attributing a value to a variable.

17/04/2018 - Making quite a big refactor in Aquitania to make it public. Removed most methods this class once had, it
just has the bare essential. Elegant design. Deleting some old children such as indicator open output and closed output.
"""

import abc
import numpy as np


class AbstractIndicator:
    """
    This is the AbstractIndicator class. It is used as an abstract base class for every indicator (not always directly).

    This is a base class and should not be used directly.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        """
        Sets basic starting values for every indicator.
        """
        # Initializes variables
        self.up = True
        self.last_candle = None
        self.last_output = np.nan
        self.output_list = []

    def feed(self, candle):
        """
        Executes indicator through 'self.indicator_logic()' and stores values on 'self.output_list'.

        :param candle: input candle
        """
        self.set_output(self.indicator_logic(candle))

    def set_output(self, result):
        """
        Append to 'output_list' and set 'last_output'.

        :param result: Output from indicator_logic
        """
        self.last_output = result

    @abc.abstractmethod
    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.

        To be implemented.
        """
        pass
