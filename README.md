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

## Usage

### Running your first simulation:

```
from aquitania import Aquitania

aq = Aquitania()  # Instantiates with default 'test' broker
aq.run()
```

### Instantiating Aquitania with a different data source:

```
aq = Aquitania(broker='oanda')
```

### Running a Live Simulation:

```
aq.run(is_live=True)
```

### Selecting assets:

```
aq = Aquitania(list_of_asset_ids=['USD_JPY', 'EUR_JPY'])
```

### Cleaning past simulations data:

```
aq.clean_data()
```

### Creating a custom strategy:

```
# TODO
```

### Creating a custom indicator:

```
# TODO
```
