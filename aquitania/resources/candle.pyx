import datetime as dtm
import aquitania.resources.datetimefx as dtfx
from copy import copy
import pandas as pd

cdef class Candle:
    """
    Candle class store the naked essentials of the element Candle, and provides methods which are recurrent calculations
    in a easy to use fashion.
    """
    def __init__(self, unsigned char ts_i, unsigned char currency, datetime dt, datetime open_time, datetime close_time, float open, float high, float low, float close, int volume, bint complete):
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
        self.ts = ts_i
        self.currency = currency
        self.datetime, self.open_time, self.close_time = dt, open_time, close_time
        self.open, self.high, self.low, self.close = (-open, open), (-low, high), (-high, low), (-close, close)
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

    cpdef float upper_shadow(self, bint up):
        """
        Returns Candle's upper shadow size.

        :return: Candle upper shadow size
        :rtype: Float
        """
        return self.high[up] - self.body_max(up)

    cpdef float lower_shadow(self, bint up):
        """
        Returns Candle's upper shadow size.

        :return: Candle upper shadow size
        :rtype: Float
        """
        return self.body_min(up) - self.low[up]

    cpdef bint lower_than(self, Candle candle, bint up):
        """
        Checks if given Candle is lower than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is lower.
        :rtype: Boolean
        """
        return self.low[up] < candle.low[up]

    cpdef bint higher_than(self, Candle candle, bint up):
        """
        Checks if given Candle is higher than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is higher.
        :rtype: Boolean
        """
        return self.high[up] > candle.high[up]

    cpdef bint ascending(self, Candle candle, bint up):
        """
        Checks if given Candle is ascending to current Candle (has both higher low and high values)

        :param candle: Given Candle to know whether it is ascending to current Candle
        :param up: True if Mov is Alta

        :return: True if it is ascending
        :rtype: Boolean
        """
        return self.low[up] > candle.low[up] and self.high[up] > candle.high[up]

    cpdef Candle new_ts(self, int ts):
        """
        Creates an identical copy of current the Candle object.

        :return: Identical copy of the current Candle object
        :rtype: Candle
        """
        cdef:
            datetime open_time
            datetime close_time
        open_time, close_time = dtfx.init_open_close_times(self.datetime, ts)
        return Candle(ts, self.currency, self.datetime, open_time, close_time, self.open[1],
        self.high[1], self.low[1], self.close[1], self.volume, ts == 0)

    cpdef Candle copy(self):
        """
        Creates an identical copy of current the Candle object.

        :return: Identical copy of the current Candle object
        :rtype: Candle
        """
        return Candle(self.ts, self.currency, self.datetime, self.open_time, self.close_time, self.open[1],
        self.high[1], self.low[1], self.close[1], self.volume, self.ts == 0)

    cpdef bint lower_eclipses(self, Candle candle, bint up):
        """
        Checks if given Candle is lower than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is lower.
        :rtype: Boolean
        """
        if self.low[up] < candle.low[up]:
            return True
        elif self.low[up] == candle.low[up] and self.high[up] > candle.high[up]:
            return True
        else:
            return False

    cpdef bint higher_eclipses(self, Candle candle, bint up):
        """
        Checks if given Candle is higher than current Candle.

        :param candle: given Candle you want to compare with current Candle.
        :param up: True if Mov is Alta

        :return: True if given Candle is higher.
        :rtype: Boolean
        """
        if self.high[up] > candle.high[up]:
            return True
        elif self.high[up] == candle.high[up] and self.low[up] < candle.low[up]:
            return True
        else:
            return False

    cpdef bint eclipses(self, Candle candle, bint up):
        """
        Checks if given Candle eclipses (higher high and lower low) current Candle.

        :param candle: Given Candle to be compared with current Candle
        :param up: True if Mov is Alta

        :return: True if given Candle eclipses current Candle
        :rtype: Boolean
        """
        if self.low[up] < candle.low[up] and self.high[up] >= candle.high[up]:
            return True
        elif self.low[up] == candle.low[up] and self.high[up] > candle.high[up]:
            return True
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

    cpdef bint is_same_open_time(self, Candle candle):
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
        return '{}: O: {} H: {} L: {} C: {} V: {} Ts: {} Cur: {}'.format(self.datetime, self.open[1], self.high[1],
                                                                         self.low[1], self.close[1], self.volume,
                                                                         self.ts, '')
