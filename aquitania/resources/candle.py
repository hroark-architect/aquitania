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

This file contains one of the most basic classes of Aquitania.

This was one of the first files that I had worked on, and it still contains much of the original code

It has had some changes that were later reverted when I was still deciding on how to implement the classes and was
considering the option of using a 'list_of_candles' class. This was later solved by using states and pandas DataFrames
to store and process larger chunks of data.

28/11/2017 - I did some big refactoring on this class and deleted all the getters and setters that were originally used,
apparently getters and setters in Python is a bad implementation.

15/03/2018 - Did a big refactor a couple weeks ago and changed the whole internal mechanisms of this class, made a
pretty ingenious solution to store already inverted high and low values into tuples that will be accessed according to
indicator movement.

16/04/2018 - Added .close_time and .open_time attributes and refactor methods to generate these data.
"""

import datetime

import aquitania.resources.datetimefx as dtfx
from copy import copy


class Candle:
    """
    Candle class store the naked essentials of the element Candle, and provides methods which are recurrent calculations
    in a easy to use fashion.
    """

    def __init__(self, ts, currency, dt, open_, high, low, close, volume, complete):
        """
        Initialize Candle object with the naked essentials.

        :param ts: (int) Timestamp
        :param currency: (str) Asset Name
        :param dt: OpenTime (Datetime, can be 'pd.timestamp' as well)
        :param open_: Open value (Used open_ because there is a python variable called open)
        :param high: High value
        :param low: Low value
        :param close: Close value
        :param volume: Volume
        :param complete: Complete (Boolean)
        """

        # Initializes variables
        self.ts = ts
        self.currency = currency
        self.datetime = dt
        self.open_time, self.close_time = self.init_open_close_times()
        self.open, self.high, self.low, self.close = (-open_, open_), (-low, high), (-high, low), (-close, close)
        self.volume = volume
        self.complete = complete

    def color(self, up):
        """
        Returns Candle's color according to following code:

        :return: Returns 1 if green, 2 if doji, 0 if red
        :rtype: Int
        """
        if self.close[up] > self.open[up]:
            return 1
        elif self.close[up] == self.open[up]:
            return 2
        else:
            return 0

    def size(self, up):
        """
        Returns Candle's absolute size.

        :return: Candle size
        :rtype: Float
        """
        return self.high[up] - self.low[up]

    def body(self, up):
        """
        Returns Candle's body size.

        :return: Candle body size
        :rtype: Float
        """
        return abs(self.open[up] - self.close[up])

    def body_max(self, up):
        """
        Returns Candle's body max value.

        :return: Candle body max value
        :rtype: Float
        """
        return max(self.close[up], self.open[up])

    def body_min(self, up):
        """
        Returns Candle's body min value.

        :return: Candle body min value
        :rtype: Float
        """
        return min(self.close[up], self.open[up])

    def shadow(self, up):
        """
        Returns Candle's shadow size.

        :return: Candle shadow size
        :rtype: Float
        """
        return self.size(up) - self.body(up)

    def upper_shadow(self, up):
        """
        Returns Candle's upper shadow size.

        :return: Candle upper shadow size
        :rtype: Float
        """
        return self.high[up] - self.body_max(up)

    def lower_shadow(self, up):
        """
        Returns Candle's upper shadow size.

        :return: Candle upper shadow size
        :rtype: Float
        """
        return self.body_min(up) - self.low[up]

    def lower_than(self, candle, up):
        """
        Checks if given Candle is lower than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is lower.
        :rtype: Boolean
        """
        if self.low[up] < candle.low[up]:
            return True
        else:
            return False

    def higher_than(self, candle, up):
        """
        Checks if given Candle is higher than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is higher.
        :rtype: Boolean
        """
        if self.high[up] > candle.high[up]:
            return True
        else:
            return False

    def ascending(self, candle, up):
        """
        Checks if given Candle is ascending to current Candle (has both higher low and high values)

        :param candle: Given Candle to know whether it is ascending to current Candle
        :param up: True if Mov is Alta

        :return: True if it is ascending
        :rtype: Boolean
        """
        if self.low[up] > candle.low[up]:
            if self.high[up] > candle.high[up]:
                return True
            else:
                return False
        else:
            return False

    def new_ts(self, ts):
        """
        Creates an identical copy of current the Candle object.

        :return: Identical copy of the current Candle object
        :rtype: Candle
        """
        return Candle(ts, self.currency, self.datetime, self.open[1], self.high[1], self.low[1], self.close[1],
                      self.volume, ts == 0)

    def copy(self):
        """
        Creates an identical copy of current the Candle object.

        :return: Identical copy of the current Candle object
        :rtype: Candle
        """
        return copy(self)

    def lower_eclipses(self, candle, up):
        """
        Checks if given Candle is lower than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is lower.
        :rtype: Boolean
        """
        if self.low[up] < candle.low[up]:
            return True
        elif self.low[up] == candle.low[up]:
            if self.high[up] > candle.high[up]:
                return True
            else:
                return False
        else:
            return False

    def higher_eclipses(self, candle, up):
        """
        Checks if given Candle is higher than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is higher.
        :rtype: Boolean
        """
        if self.high[up] > candle.high[up]:
            return True
        elif self.high[up] == candle.high[up]:
            if self.low[up] < candle.low[up]:
                return True
            else:
                return False
        else:
            return False

    def eclipses(self, candle, up):
        """
        Checks if given Candle eclipses (higher high and lower low) current Candle.

        :param candle: Given Candle to be compared with current Candle
        :param up: True if Mov is Alta

        :return: True if given Candle eclipses current Candle
        :rtype: Boolean
        """
        if self.low[up] < candle.low[up]:
            if self.high[up] >= candle.high[up]:
                return True
            else:
                return False
        elif self.low[up] == candle.low[up]:
            if self.high[up] > candle.high[up]:
                return True
            else:
                return False
        else:
            return False

    def japanese_candlestick(self, up, jc_up):
        """
        Returns True if it is one of the more traditional types of Japanese Candlestick reversal patterns.

        :return: True if it is a type of Japanese Candlestick
        :rtype: Bool
        """

        # Initializes Variables
        shadow = self.shadow(up)
        body = self.body(up)
        upper_shadow = self.upper_shadow(up)
        lower_shadow = self.lower_shadow(up)

        # Doji Routine
        if body == 0 or shadow / body >= 12:
            return True

        # Japanese Candlestick Up Routine
        elif jc_up:
            if lower_shadow / body >= 2:
                return True

        # Japanese Candlestick Down Routine
        elif upper_shadow / body >= 2:
            return True
        return False

    def is_doji(self, up):
        shadow = self.shadow(up)
        body = self.body(up)
        return body == 0 or shadow / body >= 12

    def num_profit(self, distance, up):
        """
        Add numeric profit to close value.

        :param distance: Distance in absolute price value
        :param up: True if up

        :return: Value of profit reference
        :rtype: float
        """
        return self.close[up] + distance

    def num_stop(self, distance, up):
        """
        Add numeric stop to close value.

        :param distance: Distance in absolute price value
        :param up: True if up

        :return: Value of stop reference
        :rtype: float
        """
        return self.close[up] - distance

    def marubozu(self, up):
        """
        Returns if it is Marubozu Japanese Candlestick pattern.

        :param up: True if up

        :return: True if Marubozu
        :rtype: bool
        """
        # Initialize variables
        shadow = self.shadow(up)
        body = self.body(up)

        # Marubozu Routine
        if shadow == 0 or body / shadow >= 15:
            return True
        else:
            return False

    def init_open_close_times(self, ts=None):
        """
        Initializes Candle with open and close time values.

        :return: Candle open time, Candle close time
        :rtype: tuple of 2 datetime elements
        """
        if ts is None:
            ts = self.ts
        # This if elif structure looks ridiculous but it is really fast.
        if ts == 0:
            return self.datetime, self.datetime
        elif ts == 1:
            return self.div_by_sec(300)
        elif ts == 2:
            return self.div_by_sec(900)
        elif ts == 3:
            return self.div_by_sec(1800)
        elif ts == 4:
            return self.div_by_sec(3600)
        elif ts == 5:
            return self.daily_criteria()
        elif ts == 6:
            return self.weekly_criteria()
        elif ts == 7:
            return self.monthly_criteria()
        else:
            raise ValueError('Invalid Candle TimeStamp')

    def div_by_sec(self, seconds):
        open_time = (self.datetime.timestamp() // seconds) * seconds
        close_time = open_time + seconds - 60

        return dtfx.dt_from_ts(open_time), dtfx.dt_from_ts(close_time)

    def daily_criteria(self):
        open_time = (self.datetime.timestamp() // 86400) * 86400
        close_time = open_time + 86400 - 60

        # Puts Monday together with Sunday
        if self.datetime.weekday() == 0:
            open_time -= 86400
            open_time = dtfx.dt_from_ts(open_time)
        else:
            open_time = dtfx.dt_from_ts(open_time)

        if self.datetime.weekday() == 6:
            close_time += 86400
            close_time = dtfx.dt_from_ts(close_time)
        elif self.datetime.weekday() == 4:
            close_time = dtfx.next_market_close(self.datetime)
        else:
            close_time = dtfx.dt_from_ts(close_time)

        return open_time, close_time

    def weekly_criteria(self):
        # Need to divide in to groups:
        #  1. 3-5 Thursday to Saturday
        if 3 <= self.datetime.weekday() <= 5:
            open_time = (self.datetime.timestamp() // 604800) * 604800 - 345600
        # 2. Other weekdays
        else:
            open_time = (self.datetime.timestamp() // 604800) * 604800 + 259200

        close_time = dtfx.dt_from_ts(open_time + 604800 - 60)
        if 5 >= close_time.weekday() >= 4:
            close_time = dtfx.next_market_close(self.datetime)

        return dtfx.dt_from_ts(open_time), close_time

    def monthly_criteria(self):
        open_time = datetime.datetime(self.datetime.year, self.datetime.month, 1)

        if self.datetime.month == 12:
            close_time = dtfx.previous_candle(datetime.datetime(self.datetime.year + 1, 1, 1), 1)
        else:
            close_time = dtfx.previous_candle(datetime.datetime(self.datetime.year, self.datetime.month + 1, 1), 1)

        if 5 >= close_time.weekday() >= 4:
            close_time = dtfx.last_market_close(close_time)

        return open_time, close_time

    def is_same_open_time(self, candle):
        return isinstance(self, candle.__class__) and self.open_time == candle.open_time

    def __eq__(self, other):
        return isinstance(self, other.__class__) and self.datetime == other.datetime and self.currency == \
               other.currency and self.ts == other.ts

    def __gt__(self, other):
        return isinstance(self, other.__class__) and self.datetime > other.datetime

    def __hash__(self):
        return hash(self.datetime)

    def __repr__(self):
        """
        Overwrite parent class method to display constructor.

        Implemented in 20/01/2018 while reading Luciano Ramalho's Book: Fluent Python.

        :return: Constructor in string form (helpful to debug)
        :rtype: String
        """
        return 'Candle(%r, %r, %r, %r, %r, %r, %r, %r, %r)' % (
            self.ts, self.currency, self.datetime, self.open[1], self.high[1], self.low[1], self.close[1], self.volume,
            self.complete)

    def __str__(self):
        """
        Overwrites parent class method to print the object.

        Displays the Candle values in a easy to understand fashion:
            Datetime
            O: Open
            H: High
            L: Low
            C: Close
            V: Volume
            Ts: Timestamp
            Cur: Currency

        :return: Returns string object consisting of print logic
        :rtype: String
        """
        return str(self.datetime) + ' O: ' + str(self.open[1]) + ' H: ' + str(self.high[1]) + ' L: ' + str(
            self.low[1]) + ' C: ' + str(self.close[1]) + ' V: ' + str(self.volume) + ' Ts: ' + str(
            self.ts) + ' Cur: ' + self.currency
