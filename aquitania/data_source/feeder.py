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

Feeder was by far the toughest module to conceive so far (02/12/2017).

It generates all timestamp based on simple calculations from G01 Candles.

It has some clever tricks, in special it doesn't feed every incomplete candle, only those incomplete candles with a new
high or low value, because all other information would not be relevant.

One of my most beautiful designs so far.

17/04/2018 - Making a big refactor on the whole Aquitania project, I will make it public, so I am reassuring that the
code is beautiful and the designs are elegant. Removed many methods that were used to verify opening and closing candle
times. Now I am currently moving this methods inside the Candle class.

21/04/2018 - Eventually there might be a need to create a different type of Feeder, if don't use any event based
indicators this kind of Feeder makes no sense as it iterates line by line and doesn't leverage on Numpy features. If we
are only going to process things like SMAs and Bollinger Bands, it is quite easy to make an add-on to calculate this
directly on Numpy.
"""

from aquitania.resources.candle import Candle
import datetime


class Feeder:
    """
    Feeder is an object that will receive as input G01 Candles and generate complete and incomplete candles of several
    timestamps:

        1. G01
        2. G05
        3. G15
        4. G30
        5. G60
        6. Daily
        7. Weekly
        8. Monthly
    """

    def __init__(self, list_of_loaders, currency):
        """
        Feeder class is initialized with the list_of_loaders to whom the Candles will be fed.

        :param list_of_loaders: List of Loaders, each element in the list refers to a timestamp.
        """

        # Initialize variables
        self._loaders = list_of_loaders
        self.currency = currency
        self._candles = None

    def init_build(self, candle):
        """
        Initialize the internal variables of the Feeder object.

        :param candle: First Candle to be fed to the Feeder
        """

        # Initialize variables
        self._candles = self.create_init_candle_array(candle, len(self._loaders))

    def create_init_candle_array(self, candle, number_of_times):
        return [self.first_candle_ts(candle.new_ts(ts), ts) for ts in range(number_of_times)]

    def first_candle_ts(self, candle, ts):
        # Set timestamp
        candle.ts = ts
        # It distorts candle to enable feeder to feed first candle of larger timestamps
        candle.high = tuple([high * 0.95 for high in candle.high])
        # If time stamp more than g01, candle is Incomplete
        candle.complete = False if ts > 0 else True
        return candle

    def feed(self, candle):
        """
        Feeds candle to all Loaders.

        :param candle: Input Candle
        """
        # Goes through every timestamp
        criteria_table = self.generate_criteria_table(candle)

        self.missing_closed_candles(criteria_table)

        for ts in reversed(range(0, 8)):
            self.make_candle(ts, candle, criteria_table)

    def missing_closed_candles(self, criteria_table):
        """
        This method purpose is to deal with candles that should have closed but didn't because they were actually
        missing from the feed. For example, a candle of '15Min' should close on 08h14, but we only had the 08h13 candle
        on the feed, and now we are at 08h15, we had a gap.

        This method checks if there should be a closing candle that was not yet closed in all timestamps, and gets the
        largest possible close time and propagates it to all timestamps.

        :param criteria_table: (list of Bool) Criteria Table that check if a Candle should be closed that isn't
        """
        # Checks if there is a .complete Candle that meets the criteria, if not returns
        if not any([criteria and not self._candles[i].complete for i, criteria in enumerate(criteria_table)]):
            return

        # Creates a dummy variable to compare with closing times
        dt = datetime.datetime(1970, 1, 2)

        # Gets closing datetime to propagate to all timestamps
        for ts, criteria in enumerate(criteria_table):
            if criteria and not self._candles[ts].complete:
                self._candles[ts].complete = True
                dt = max(self._candles[ts].close_time, dt)

        # Define close value
        close = self._candles[0].close

        # Timestamp 0 routine ('1Min' timestamp only works with complete Candles, it is a bit of a different logic)
        self._candles[0].datetime = dt
        self._loaders[0].fillna(self._candles[0])

        # Routine for timestamps > 1, .feed() if it is complete, and .fillna() if it is not complete
        for ts in reversed(range(1, 8)):
            self._candles[ts].datetime = dt
            self._candles[ts].close = close
            if self._candles[ts].complete:
                self._loaders[ts].feed(self._candles[ts])
            else:
                self._loaders[ts].fillna(self._candles[ts])

    def make_candle(self, ts, candle, criteria_table):
        """
        Creates the Candle a specific timestamp and feeds it to its respective Loader.

        :param ts: Timestamp
        :param candle: G01 Candle
        :param criteria_table: criteria table to check if a new Candle should be built
        """

        # Checks if there is the need to create a new Candle
        if criteria_table[ts]:
            self.new_candle_routine(ts, candle)

        else:
            # Check if there is the need to update values (high, low, close)
            self.set_values(ts, candle)

    def generate_criteria_table(self, candle):
        """
        Evaluates if it is time to create a new Candle.
        :param candle: Input Candle

        :return: True if new candle is to be created
        :rtype: Boolean
        """

        return [candle.datetime > candle_ts.close_time for candle_ts in self._candles]

    def new_candle_routine(self, ts, candle):
        """
        Creates new Candle if necessary and feeds indicators the complete candle.

        :param ts: Timestamp of Candle to be created
        :param candle: Input G01 Candle
        """

        # Feeds incomplete candle
        self.new_candle(ts, candle)
        if self.is_closing_candle(ts, candle):
            # Set correct attributes to candle
            self._candles[ts].complete = True

        self._loaders[ts].feed(self._candles[ts])

    def new_candle(self, ts, candle):
        """
        Creates a new Candle for a given timestamp from a G01 Candle.

        :param ts: Timestamp of Candle to be created
        :param candle: Input G01 Candle
        """
        if ts == 0:
            self._candles[ts] = candle
        else:
            self._candles[ts] = candle.new_ts(ts)

    def set_values(self, ts, candle):
        """
        Routine to update incomplete candles of larger timestamps.

        :param ts: Timestamp of Candle to be updated
        :param candle: Input G01 Candle
        """
        loader = self._loaders[ts]

        # Proxy to know whether to feed larger timestamps
        is_relevant = False

        # Checks if needs to update high value
        if candle.high[1] > self._candles[ts].high[1]:
            self._candles[ts].high = (self._candles[ts].high[0], candle.high[1])
            self._candles[ts].low = (-candle.high[1], self._candles[ts].low[1])
            is_relevant = True

        # Check if needs to update low value
        if candle.low[1] < self._candles[ts].low[1]:
            self._candles[ts].low = (self._candles[ts].low[0], candle.low[1])
            self._candles[ts].high = (-candle.low[1], self._candles[ts].high[1])
            is_relevant = True

        # Updates close value and volume
        self._candles[ts].close = candle.close
        self._candles[ts].volume += candle.volume
        self._candles[ts].datetime = candle.datetime

        # Feeds closing candle
        if self.is_closing_candle(ts, candle):
            # Set correct attributes to candle
            self._candles[ts].complete = True
            loader.feed(self._candles[ts])
        elif is_relevant:
            loader.feed(self._candles[ts])
        else:
            loader.fillna(self._candles[ts])

    def is_closing_candle(self, ts, candle):
        """
        Routine to know whether a Candle is the closing Candle.

        :param ts: Timestamp of Candle to be updated
        :param candle: Input G01 Candle

        :return: True if it is the closing Candle
        :rtype: Boolean
        """
        return candle.datetime == self._candles[ts].close_time

    def exec_df(self, df, counter=0, reference=250000):
        """
        Feed all Candles of DataFrame to the instantiated indicators.

        Every time it saves the output into disk it yields so that the IndicatorManager can save its state.

        :param df: (pandas DataFrame) Candles to be fed
        :param counter: (int) Candles counter
        :param reference: (int) Number of Candles to be counted before saving a batch into disk
        """
        # If DataFrame is empty finishes process
        if df.shape[0] == 0:
            return

        # Instantiate the first candle
        self.instantiate_first_candle(df.iloc[0])

        # Routine to execute the DataFrame
        for dt_tm, open_, high, low, close, volume in df.itertuples():  # itertuples() is much faster than iterrows()

            # Instantiates Candle
            candle = Candle(0, self.currency, dt_tm, open_, high, low, close, volume, True)

            # Feeds Candle
            self.feed(candle)

            # Adds to counter
            counter += 1

            # Check number of iterations
            if counter > reference:
                # Zeroes counter
                reference += 250000

                # Saves output
                self.save_output()
                yield dt_tm

        # Finished all Candles, save it all to disk
        self.save_output()
        yield dt_tm  # Need to be yield here to run one more save loop in IndicatorManager

    def instantiate_first_candle(self, df_line):
        """
        Feeder need to have a few Candle References already instantiated to work with.

        This methods gets the first candle of the DataFrame and create those references through .init_build().

        :param df: (pandas DataFrame) Candles to be fed
        """
        # If Candle states are already initialized there is no need to run this method
        if self._candles is not None:
            return

        # Get Candle Values
        dt_tm, open_, high, low, close, volume = df_line.name, *df_line.values

        # Instantiates Candle
        candle = Candle(0, self.currency, dt_tm, open_, high, low, close, volume, True)

        # Initializes Candle states
        self.init_build(candle)

    def save_output(self):
        # Saves output of indicators
        # TODO consider a less volatile storage than .h5
        # TODO need to save state and output at the same time

        for loader in self._loaders:
            loader.save_output()
