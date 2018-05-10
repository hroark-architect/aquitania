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
import abc


class AbstractSignal(AbstractIndicatorOutput):
    """
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, obs_id, columns, is_open, last_output):
        """
        Sets values for attributes specific to output-able indicators.

        :param obs_id: String that contains an identifiable name for indicator (ex.: cont_ext_g01)
        :param columns: String that enables identification of each of the output parameters, usually will be some
                        combination of 'id' with a name that identifies the output parameter (ex.: cont_ext_g01_is_alta)
        :param is_open: Boolean value that defines whether works with open candles as well
        """
        # Checks if all mandatory column names for signals are there, and generates a column dict
        points = column_verification(obs_id, columns)

        # Creates a new dictionary, with the correct string names
        self.ok, self.profit, self.stop, self.entry = points['ok'], points['profit'], points['stop'], points['entry']

        # Instantiates AbstractIndicatorOutput
        super().__init__(obs_id, columns, is_open, last_output)


def column_verification(obs_id, columns):
    column_dict = {}
    for column in columns:
        for element in ['ok', 'profit', 'stop', 'entry']:
            if element in column:
                column_dict[column] = '{}_{}'.format(obs_id, column)
                break
        else:
            raise ValueError('All signals need 4 mandatory columns: ok, profit, stop, entry')

    return column_dict
