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

import numpy as np
import pandas as pd
from aquitania.indicator.management.indicator_data import *
import copy


class IndicatorLoader:
    """
    An IndicatorLoader object holds all indicators for a specific Financial Security
    """

    def __init__(self, indicator_list, finsec, timestamp, broker_instance):
        """
        Initializes IndicatorLoader for specific currency and timestamp.

        :param indicator_list: Indicators to be evaluated
        :param finsec: Financial Security that will be evaluated
        :param timestamp: Timestamp of the IndicatorLoader
        """

        # Initialize variables
        self._indicator_list = indicator_list
        self._currency = finsec
        self._timestamp = timestamp
        self._broker_instance = broker_instance
        self._datetimes = []
        self._last_candle_dt = None
        self._candle_complete = []

    def feed(self, candle):
        """
        Feeds open candle into open indicators and fillna() to closed indicators.

        :param candle: Input Candle
        """

        # Store Routine
        self.store_candle(candle)

        # Feeds Candle to all indicators
        for indicator in self._indicator_list:

            # Routine for open indicator and closed indicators when candle is complete
            if indicator.is_open or candle.complete:
                indicator.feed(candle)
            else:
                # Fillna closed indicators
                indicator.fillna()

    def fillna(self, candle):
        """
        Saves indicators in case it is a not relevant candle.

        :param candle: Last Candle evaluated
        """
        # Store Candle Routine
        self.store_candle(candle)

        # FillNA method
        for indicator in self._indicator_list:
            indicator.fillna()

    def store_candle(self, candle):
        """
        Store Candle routine

        :param candle: Candle to be stored
        """

        self._datetimes.append(candle.datetime)
        self._candle_complete.append(candle.complete)
        self._last_candle_dt = copy.copy(candle.datetime)

    def save_output(self):
        """
        Combines the output of all the indicators in a single pandas DataFrame.

        """
        # Initializes IndicatorDataManager
        odm = IndicatorDataManager(self._currency, self._broker_instance)

        df = self.generate_df()
        odm.save_output(df, self._timestamp)

    def generate_df(self):
        # Initialize Variables
        df = None

        # Get candles index
        index = self._datetimes

        # Gets output from indicators
        for indicator in self._indicator_list:

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

        df['complete_{}'.format(ref.ts_to_letter[self._timestamp])] = np.array([self._candle_complete]).T

        df.index = index

        self._datetimes = []
        self._candle_complete = []

        # Returns values
        return df
