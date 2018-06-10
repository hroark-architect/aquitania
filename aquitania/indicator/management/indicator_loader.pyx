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

import pandas as pd
import aquitania.resources.references as ref
from aquitania.resources.candle cimport Candle

cdef class IndicatorLoader:
    """
    An IndicatorLoader object holds all indicators for a specific Financial Security
    """

    def __init__(self, list indicator_list, int asset, int timestamp, object broker_instance):
        """
        Initializes IndicatorLoader for specific asset and timestamp.

        :param indicator_list: Indicators to be evaluated
        :param asset: Financial Security that will be evaluated
        :param timestamp: Timestamp of the IndicatorLoader
        """

        # Initialize variables
        self.indicator_list = indicator_list
        self._asset = asset
        self._timestamp = timestamp
        self._broker_instance = broker_instance
        self._datetimes = []
        self._candle_complete = []

    cpdef void feed(self, Candle candle):
        """
        Feeds open candle into open indicators and fillna() to closed indicators.

        :param candle: Input Candle
        """
        # Feeds Candle to all indicators
        for indicator in self.indicator_list:

            # Routine for open indicator and closed indicators when candle is complete
            if indicator.is_open or candle.complete:
                indicator.feed(candle)

    cdef void store_candle(self, Candle candle):
        """
        Store Candle routine

        :param candle: Candle to be stored
        """

        self._datetimes.append(candle.datetime)
        self._candle_complete.append(candle.complete)

    cpdef void save_output(self):
        """
        Combines the output of all the indicators in a single pandas DataFrame.

        """
        df = self.generate_df()

        # When empty DataFrame is generated, it is converted to None, that should not be saved
        if df is None:
            return

        ts = ref.ts_to_letter[self._timestamp]

        # Saves observations to disk
        self._broker_instance.save_indicators(df, ref.currencies_list[self._asset], ts)

    cdef object generate_df(self):
        # Initialize Variables
        df = None

        # Get candles index
        index = self._datetimes

        # Gets output from indicators
        for indicator in self.indicator_list:

            # Go to next element if columns are empty
            if not indicator.columns:
                indicator.output_list = []
                continue

            temp_df = pd.DataFrame(indicator.output_list, columns=indicator.columns)

            if df is None:
                df = temp_df
            else:
                df = pd.concat([df, temp_df], axis=1)

            # Clears list from memory
            indicator.output_list = []

        if df is None:
            self._datetimes = []
            self._candle_complete = []
            return df

        df['complete_{}'.format(ref.ts_to_letter[self._timestamp])] = self._candle_complete

        df.index = index

        self._datetimes = []
        self._candle_complete = []

        # Returns values
        return df
