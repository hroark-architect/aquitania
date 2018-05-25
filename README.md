# aquitania
:dollar: A framework for building trading bots

# work in progress
Documentation will be released in July 2018. 

It is currently an unstable version.

## Installation

You can install it from the PyPI:

```shell
$ pip install aquitania
```
PS: If you are using linux you may need to run it as root because of the aquitania dependencies.
TODO: Investigate what dependencies need root.

## Usage

### Running your first simulation:

```
from aquitania import Bot

aq = Bot()  # Instantiates with default 'test' broker
aq.run()
```

### Instantiating Aquitania with a different data source:

```
aq = Aquitania(broker='oanda')  # (ex.: 'test, 'oanda', 'fxcm')
```

### Running a Live Simulation:

```
aq.run(is_live=True)
```

### Selecting assets:

```
aq = Aquitania(list_of_asset_ids=['USD_JPY', 'EUR_JPY'])
```

### Setting start date for historical simulations:
```
import datetime
aq = Aquitania(start_dt=datetime.datetime(1971, 2, 1))
```

### Cleaning past simulations data:

```
aq.clean_data()
```

### Creating a custom indicator:


```
from aquitania.indicator.signal.abstract_signal import AbstractSignal


class Doji(AbstractSignal):
    """
    Technical Analysis Doji Candle Pattern.
    """

    def __init__(self, obs_id):
        # Instantiates Variables
        columns = ['ok', 'profit', 'stop', 'entry']
        is_open = False  # if this indicator allow open candles 
        last_output = (False, 0.0, 0.0, 0.0)  # Values that will be show until there is no real output from indicator

        # Initializes AbstractSignal
        super().__init__(obs_id, columns, is_open, last_output)

    def indicator_logic(self, candle):
        """
        Logic of the indicator that will be run candle by candle.
        """
        profit, loss, entry = 0.0, 0.0, 0.0

        self.up = candle.upper_shadow(up=True) < candle.lower_shadow(up=True)

        # Check if it is a Doji
        is_ok = candle.is_doji(self.up)

        if is_ok:
            # Generate Exit points
            loss = candle.low[self.up]
            profit = candle.num_profit(candle.close[self.up] - loss, self.up)
            entry = candle.close[self.up]

        return is_ok, profit, loss, entry

```

Save it as doji.py

### Getting started with a custom strategy using the Doji indicator:

```
import datetime
from aquitania import Aquitania
from aquitania.strategies.strategies_abc import Strategy
from doji import Doji


class TestStrategy(Strategy):

    def __init__(self):
        super().__init__()

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

        self.signal = Doji('d_doji')

        return [self.signal]

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


if __name__ == '__main__':
    aq = Aquitania(
        broker='test',  # Broker Name (ex.: 'test, 'oanda', 'fxcm')
        list_of_asset_ids=['GBP_USD'],  # Asset ids to be processed
        is_clean=False,  # if True will reset all historical data
        start_dt=datetime.datetime(1971, 2, 1),  # start date for historical simulations
        strategy_=TestStrategy()  # Strategy to be used
    )
    aq.clean_data()  # Cleaning past simulations data
    aq.run()
```