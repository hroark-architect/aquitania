########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||||#
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||||#
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||||#
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||||#
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||||#
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||||#
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
########################################################################################################################

"""
.. moduleauthor:: H Roark

This abstract base class was done to facilitate generating output-able indicators.

It was conceived on 27/11/2017.

17/04/2018 - It once was divided into 2 classes Open and Closed Output, now it is back to one very simple class.
31/05/2018 - Forced implementation of 'last_output' for closed observers.
"""

import abc
from aquitania.indicator.abstract.indicator_abc import AbstractIndicator


class AbstractIndicatorOutput(AbstractIndicator):
    """
    This class was made to force requirements for indicator that will produce outputs.

    All those indicators need to:
        1. Have an 'id'
        2. Have a 'columns' output
        3. Have a classification of 'is_open' or not (accepts open candles or not)

    That is important to feed indicators and also to generate output to be analyzed.

    This is a base class and should not be used directly.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, obs_id, columns, is_open=True, last_output=None):
        """
        Sets values for attributes specific to output-able indicators.

        :param obs_id: String that contains an identifiable name for indicator (ex.: cont_ext_g01)
        :param columns: String that enables identification of each of the output parameters, usually will be some
                        combination of 'id' with a name that identifies the output parameter (ex.: cont_ext_g01_is_alta)
        :param is_open: Boolean value that defines whether works with open candles as well
        """
        # Set attributes
        self.id = obs_id
        self.columns = ['{}_{}'.format(obs_id, column) for column in columns]
        self.is_open = is_open

        # Instantiates abstract indicator
        super().__init__()

        # Routine verification for last output on closed observers, will force implementation
        self.set_last_output(columns, is_open, last_output)

    def set_last_output(self, columns, is_open, last_output):
        """
        Routine to set 'self.last_output' on close observers.

        It serves to force implementation, as it was hard to remember exactly how to set this up.

        :param columns: (list of str) List of column names
        :param is_open: (bool) True if open, False if closed
        :param last_output: (tuple of values) Tuple that contains the initial state for indicator output
        """
        # Only works for closed observers
        if not is_open:
            # Check if output is in correct data structure for indicator output (tuple)
            if not isinstance(last_output, tuple):
                raise ValueError('Please instantiate last_output as tuple.')

            # Check if the output has the same length as the number of columns
            elif len(last_output) != len(columns):
                raise ValueError('Please correct the length of last_output or columns, should be the same')

            # If last_output is in correct format, save it as an attribute
            else:
                self.last_output = last_output

    def set_output(self, result):
        """
        Append to 'output_list' and set 'last_output'.

        :param result: Output from '.indicator_logic()'
        """
        self.last_output = result
        self.output_list.append(result)

    def fillna(self):
        """
        FillNA method, specific to output indicators.

        Copies last output to list.
        """
        self.output_list.append(self.last_output)
