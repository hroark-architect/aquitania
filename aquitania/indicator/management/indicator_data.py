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

"""
import aquitania.resources.references as ref


class IndicatorDataManager:
    """
    Module that manages exporting and importing output from observers.
    """

    def __init__(self, currency, broker_instance):
        """
        Initializes ObserverDataManager for given currency.

        :param currency: Input currency
        """
        self._currency = currency
        self._broker_instance = broker_instance

    def save_output(self, df, ts):
        """
        Save indicators output DataFrame to disk.

        :param df: DataFrame to be stored in HDF5
        :param ts: TimeStamp of output to be saved
        """

        # When empty DataFrame is generated, it is converted to None, that should not be saved
        if df is None:
            return

        ts = ref.ts_to_letter[ts]

        # Saves observations to disk
        self._broker_instance.save_indicators(df, self._currency, ts)
