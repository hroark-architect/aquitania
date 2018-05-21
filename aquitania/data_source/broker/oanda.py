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

Repository of all code specific to Oanda Brokerage.

Both as a data source and also as a platform to execute orders in the future.

12/04/2018 - Making a very big refactor here as there is a lot of code not very well written. Decided to work with an
abstract DataSource class. I will implement an abstract class for Storage as well.
"""
import os
import time
import datetime
import oandapyV20.endpoints.accounts as accounts
import json
import oandapyV20.endpoints.orders as orders
import pandas as pd
import numpy as np
import aquitania.resources.datetimefx as dtfx

from oandapyV20 import API, oandapyV20
from dateutil import parser
from aquitania.data_processing.util import generate_folder
from aquitania.data_source.broker.abstract_data_source import AbstractDataSource
from aquitania.resources import references
from oandapyV20.endpoints import instruments
from oandapyV20.endpoints import pricing
from oandapyV20.exceptions import V20Error
from aquitania.resources.datetimefx import next_candle_datetime


class Oanda(AbstractDataSource):
    """
    This class creates objects that establishes connections with Oanda API.

    Attributes - implemented by AbstractDataSource:
    broker_name (str) = Broker (Ex.: 'oanda')
    ds_name (str) = Data Storage Type (Ex.: 'pandas_hdf5')
    ds (AbstractStorageSystem) - Custom object to deal with data storage

    Attributes - broker specific:
    account_ID (str): Oanda's account ID
    token (str): Oanda's API token
    api (API): Oanda's API object
    """

    def __init__(self, broker_name, data_storage_type):
        """
        Initializes Oanda's DataSource object.

        :param broker_name (str): Broker Name (Ex.: 'oanda')
        :param data_storage_type (str): ata Storage Type (Ex.: 'pandas_hdf5')
        """
        # Sets file paths
        self.folder_path = 'data/broker/'
        self.file_path = self.folder_path + 'oanda_data.txt'

        # Loads attributes
        self.account_id, self.token = self.get_trading_data()

        # Sets .ds 'str' calling super DataSource class
        super().__init__(broker_name, data_storage_type, is_live=True)

        # Setup with broker config
        self.account_leverage = 30

        # Configures API access
        self.api = API(access_token=self.token)

    def get_trading_data(self):
        """
        Returns account ID and token to trade with Oanda's API.

        :return: Account ID and token
        :rtype: Tuple containing 2 strings
        """

        # TODO eventually improve path finding - create path finding lib
        if os.path.isfile(self.file_path):
            return self.open_token_file()
        else:
            return self.create_new_token_file()

    def open_token_file(self):
        """
        Opens an exiting token data file to get information

        :return: Account ID and token
        :rtype: Tuple containing 2 strings
        """
        # Reads 'oanda_data.txt' file and retrieves account_id and token
        text_file = open(self.file_path, 'r')
        lines = text_file.readlines()

        # Get Account ID and Token
        account_id = lines[0][0:19]  # Remove spaces on the end of the line
        token = lines[1][0:65]  # Remove spaces on the end of the line

        # Finish Routine
        text_file.close()
        return account_id, token

    def create_new_token_file(self):
        """
        Gets input from the user to get account ID and token and creates a new .txt file.

        :return: Account ID and token
        :rtype: Tuple containing 2 strings
        """
        # Creates routine for the user to input his data into a 'oanda_data.txt' file
        print('\nCreate an account at www.oanda.com\n')

        # User ID insertion routine
        print('Insert your account ID: (format: 123-201-9876541-321)')
        account_id = input()

        # API token insertion routine
        print('Insert your API token: (format: 29d8h4472037d91216602e85f3bf318f-06e90608d9852a3b94fc23fd1cw0889q)')
        token = input()

        # File creation Routine
        generate_folder(self.folder_path)
        text_file = open(self.file_path, 'w')
        text_file.write(account_id + '\n' + token)
        text_file.close()

        return account_id, token

    def new_historic_data_status(self, finsec):
        """
        If it doesn't exist creates a pandas DataFrame to control what has been downloaded.

        :param finsec: Financial Security ID
        """
        # Generate entry params
        params = {'from': datetime.datetime(1970, 2, 1), 'financial instrument': finsec, 'granularity': 'M1'}
        # Parse Date
        date = parser.parse(
            self.connection_historic_data(generate_oanda_params(params, 1))['candles'][0]['time'][0:19])

        # Generate pandas DataFrame
        df = pd.DataFrame([[finsec, date, datetime.datetime(1970, 2, 1)]],
                          columns=['currency', 'start_date', 'end_date'])

        # Save DataFrame to disk
        self.ds.save_controls(finsec, df)

    def connection_historic_data(self, params):
        """
        Makes a candle download request to Oanda.

        :params (dict) is a dictionary comprised by:
            'granularity' : 'M1'
            'financial_instrument' : 'EUR_USD'
            'count': 5000
            'price': 'B' (B for Bid, A for Ask, M for Mid)
            'from': '2018-04-13T14:10:00Z'
        :return raw data from Oanda
        :rtype nested dictionaries follow structure below:
            dictionary nests list of dictionaries that nests a dictionary:
                'instrument'
                'granularity'
                'candles' --> list of dictionaries
                    'complete'
                    'volume'
                    'time'
                    'bid' --> dictionary
                        'o'
                        'h'
                        'l'
                        'c'
        """
        # For some reason Oanda (or oandapyV20) requests two instances of financial instrument as input?
        financial_instrument = params['financial instrument']
        conn_params = instruments.InstrumentsCandles(instrument=financial_instrument, params=params)
        return self.api.request(conn_params)

    def candle_downloader(self, start_date, finsec, q1):
        """
        Download candles from Oanda server using multiprocessor module that is managed on HistoricDataManager.

        This function is specific to be using with the multiprocessor method that was build with HistoricDataManager.

        q1 the variable, of multiprocessing.Queue(), type where candles will be exported from this method later to be
        processed by data_processing_manager.

        :param start_date: (datetime.datetime/np.datetime64) date where candle downloads will start from
        :param finsec: (str) selected Financial Security
        :param q1: (multiprocessing.Queue()) object that continuously exports candles outside of this method
        """

        # Checks if 'start_date' is date format:
        if isinstance(start_date, pd._libs.tslib.Timestamp):
            proc_start_date = next_candle_datetime(start_date.to_pydatetime(), 1)
        elif isinstance(start_date, np.datetime64):
            proc_start_date = next_candle_datetime(datetime.datetime.utcfromtimestamp(start_date.tolist() / 1e9), 1)
        elif isinstance(start_date, datetime.datetime):
            proc_start_date = next_candle_datetime(start_date, 1)
        else:
            raise TypeError('Oanda start_date is of a wrong type. Try datetime.datetime or np.datetime64.')

        # Generate 'entry_params' that will be used to fetch candles
        entry_params = {'from': proc_start_date, 'financial instrument': finsec, 'granularity': 'M1'}

        # Generate dummy raw_data
        raw_data = None

        # Download candle routine
        while raw_data is None or len(raw_data['candles']) == 5000:

            # Check if there was already a first batched download
            if raw_data is not None:
                # Sets correct initial date for the candle request
                candle_time = parser.parse(raw_data['candles'][-1]['time'][0:19])
                entry_params['from'] = next_candle_datetime(candle_time, 1)

            # Avoid process crashing if Oanda's server fail for any reason not responding
            try:
                raw_data = self.connection_historic_data(generate_oanda_params(entry_params, 5000))
                if raw_data:
                    q1.put(raw_data)
            except:
                if raw_data is None and not dtfx.is_fx_working_hours_from_tz(datetime.datetime.now()):
                    return
                Warning('Unable to connect to Oanda. Trying again in 10 seconds.')
                time.sleep(10)

    def get_spread_data(self, finsec):
        """
        Get spread data for specific Financial Security.

        :param finsec: (str) Selected Financial Security

        :return: absolute spread value, spread percentage of last bid, last bid
        :rtype: tuple containing 3 floats
        """

        params = {'financial instrument': finsec, 'granularity': 'M1', "count": 5000, "price": "AB"}
        conn_params = instruments.InstrumentsCandles(instrument=finsec, params=params)
        candles = self.api.request(conn_params)['candles']
        open_list_bid = []
        open_list_ask = []
        for candle in candles:
            open_list_bid.append(float(candle['bid']['o']))
            open_list_ask.append(float(candle['ask']['o']))
        bid_avg = pd.Series(open_list_bid).mean()
        ask_avg = pd.Series(open_list_ask).mean()
        spread = ask_avg - bid_avg
        last_bid = open_list_bid[-1]
        spread_pct = spread / last_bid
        return spread, spread_pct, last_bid

    def get_list_of_instruments(self):
        return self.request_acc_instruments()['instruments']

    def print_string_list_of_instruments(self):
        x = self.get_list_of_instruments()
        strong = '['
        for instrument in x:
            print(instrument)
            strong += '\'' + instrument['name'] + '\', '
        strong = strong[0:-2] + ']'
        print(strong)

    def get_account_balance(self):
        return float(self.request_acc_details()['account']['balance'])

    def get_account_nav(self):
        return float(self.request_acc_details()['account']['NAV'])

    def request_acc_details(self):
        client = oandapyV20.API(access_token=self.token)
        r = accounts.AccountDetails(accountID=self.account_id)
        return client.request(r)

    def request_acc_instruments(self):
        client = oandapyV20.API(access_token=self.token)
        r = accounts.AccountInstruments(accountID=self.account_id)
        return client.request(r)

    def get_list_of_trades(self):
        # [{'instrument': 'AUD_USD', 'initialUnits': '1', 'marginUsed': '0.0080', 'openTime':
        # '2018-01-19T15:54:24.009217193Z',
        # 'financing': '0.0000', 'unrealizedPL': '-0.0001', 'currentUnits': '1', 'price': '0.80017', 'id': '260',
        # 'realizedPL': '0.0000', 'state': 'OPEN'}]

        return self.request_acc_details()['account']['trades']

    def get_used_margin(self):

        list_of_trades = self.get_list_of_trades()

        return sum(float(trade['marginUsed']) for trade in list_of_trades) * self.account_leverage

    def order(self, quote, precision_digits, bet_size, currency, profit, stop):
        tp = {"timeInForce": "GTC", "price": str(round(abs(profit), precision_digits))}
        sl = {"timeInForce": "GTC", "price": str(round(abs(stop), precision_digits))}

        order = {"order": {"units": bet_size, "instrument": currency, "timeInForce": "FOK", "type": "LIMIT",
                           "positionFill": "DEFAULT", "price": str(round(quote, precision_digits)),
                           'takeProfitOnFill': tp,
                           'stopLossOnFill': sl}}

        # client
        api = API(access_token=self.token)

        # create and process order requests
        r = orders.OrderCreate(accountID=self.account_id, data=order)
        print("processing : {}".format(r))
        print("===============================")
        print(r.data)
        print('end of data r.data')
        try:
            response = api.request(r)
        except V20Error as e:
            print("V20Error: {}".format(e))
            return False, 0.0, 0
        else:
            print("Response: {}\n{}".format(r.status_code, json.dumps(response, indent=2)))
            try:
                return True, response['orderFillTransaction']['price'], response['orderFillTransaction']['id']
            except:
                # TODO Improve warning and errors syntax and exception treatment
                Warning('Order failed to execute. Likely not to have a descent available price.')
                return False, 0.0, 0

    def data_processing_manager(self, raw_data):
        """
        Receives raw data from server and outputs processed data.

        :data_package raw data from server in format:
            data_package --> dictionary
                'instrument'
                'granularity'
                'candles' --> list of dictionaries
                    'complete'
                    'volume'
                    'time'
                    'bid' --> dictionary
                        'o'
                        'h'
                        'l'
                        'c'
        :return returns processed data
        :rtype list of lists
            processed_data
                candle_time
                financial_instrument
                timestamp
                open
                high
                low
                close
                volume
        """
        # Instantiates empty list of candles
        list_candles = []

        for candle in raw_data['candles']:

            # Transform Oanda's datetime string to datetime.datetime
            candle_time = parser.parse(candle['time'][0:19])

            # Get currency code
            currency = references.currencies_dict[raw_data['instrument']]

            # Create tuple of candle elements
            export_candle = (candle_time, currency, 0, float(candle['bid']['o']), float(candle["bid"]["h"]), float(
                candle['bid']['l']), float(candle['bid']['c']), candle['volume'])

            # Oanda may feed open candles, check if complete to store in database
            if candle['complete']:
                # Check if valid market hours
                if dtfx.is_fx_working_hours_from_tz(candle_time):
                    # Appends to list of valid only candles
                    list_candles.append(export_candle)

        # May return empty value
        return list_candles

    def get_asset_attributes(self, asset):
        """
        Generate Data Dictionary.

        :param asset: (str) Asset Name

        :return: Dictionary of Data which is data source dependent
        :rtype: dict
        """
        spread, spread_pct, last_bid = self.get_spread_data(asset)
        max_order, min_trade_size, asset_type = self.get_trade_params(asset)

        return {'spread': spread, 'spread_pct': spread_pct, 'last_bid': last_bid, 'max_order': max_order,
                'min_trade_size': min_trade_size, 'type': asset_type}

    def get_trade_params(self, currency):
        var_list = self.get_list_of_instruments()
        for var in var_list:
            if var['name'] == currency:
                return var['maximumOrderUnits'], var['minimumTradeSize'], var['type']


def generate_oanda_params(params, count):
    """
    Generates params necessary as input to request candles from Oanda's server.

    :entry_params is a dictionary comprised of:
            start_date --> datetime,
            financial_instrument --> str (Ex.: 'EUR_USD'),
            ts --> ts in table's format (Ex.: 'g01', 'g05'...)
    :return returns the parameters necessary to request candles from Oanda's
    :rtype dictionary
    """
    # Converts datetime to Oanda's datetime format (str)
    if type(params['from']) == datetime.datetime:
        params['from'] = params['from'].strftime('%Y-%m-%dT%H:%M:%SZ')

    # 5000 is the maximum amount of candles allowed by request on Oanda
    params.update({'count': count})

    # Bid price is the standard we use for that analysis (There is also Mid and Ask quotes)
    params.update({'price': 'B'})

    # Outputs every param generation (one for each request to Oanda)
    print('{}Requesting candles to {} for {} on {}'.format(dtfx.now(), 'Oanda', params['financial instrument'],
                                                                 params['from']))

    return params


# TODO need to rewrite this stream methods and put this inside Oanda main object
class OandaStream:
    """
    Stream candles from Oanda.
    Uses q1 variable to output candles through a multiprocessing Queue()

    This code is very poorly written, I'll leave it here as reference, but it will be trashed soon.
    """

    def __init__(self, currencies):
        """
        Initializes and keeps running stream continually.

        :param currencies: list of currencies that will be used to stream
        """

        self.currencies = currencies

    def output_stream_in_dataframe(self, currencies, q1):
        # TODO add runtime functionality: change currencies, pause stream...
        # Create dictionary with all the usable currencies
        self._dict_df = {k: pd.DataFrame(columns=['']) for k in currencies}

        # Start infinite loop
        while True:
            # Create try/except structure to keep pushing for stream if problems in connection arise

            # Initialize stream function
            data = self.stream(currencies)
            # Initialize data processing
            for line in data:
                # This is for a quotation, not heartbeat
                if line['type'] == 'PRICE':
                    # Throw away unnecessary information
                    data = [float(line['bids'][0]['price'])]
                    # Parse time
                    indexData = [parser.parse(line['time'][0:19])]
                    # Initialize pandas DataFrame
                    self._df = pd.DataFrame([data], index=indexData, columns=[''])
                    # Add FI to df
                    self._dict_df[line['instrument']] = self._dict_df[line['instrument']].append(self._df)

                    # dfrs stands for DataFrame ReSampled - ohlc resample '1Min'
                    self._dfrs = self._dict_df[line['instrument']].resample('1Min', axis=0).ohlc()

                    number_of_rows = self._dfrs.shape[0]
                    if number_of_rows > 1:
                        # Select only 2 last rows
                        # TODO understand this piece of code, not getting what it does to be honest
                        selector = self._dfrs.index[-2]
                        self._dict_df[line['instrument']] = self._dict_df[line['instrument']].loc[selector:]
                        self._dfrs = self._dict_df[line['instrument']].resample('1Min', axis=0).ohlc()
                        number_of_rows = self._dfrs.shape[0]

                    # Adds missing columns
                    self._dfrs['fi'] = [references.currencies_dict[line['instrument']]] * number_of_rows
                    self._dfrs['ts'] = [0] * number_of_rows
                    self._dfrs['volume'] = [0] * number_of_rows
                    # Columns names are bizarre due to ohlc resampling, this corrects them
                    self._dfrs.columns = self._dfrs.columns.map(''.join)
                    self._dfrs.index.name = 'datetime'
                    print(self._dfrs[['fi', 'ts', 'open', 'high', 'low', 'close', 'volume']])
                    q1.put(self._dfrs[['fi', 'ts', 'open', 'high', 'low', 'close', 'volume']])

    def stream(self):
        """
        Description of Raw Stream:
        type ('PRICE'/'HEARTBEAT')
            time (str - 2017-11-01T10:29:20.628235935Z)
            bids
                price (float - 1.16365)
                liquidity (int - 10000000)
            asks
                price (float - 1.16365)
                liquidity (int - 10000000)
            closeoutBid
                price (float - 1.16365)
            closeoutAsk
                price (float - 1.16365)
            status (str - 'tradeable')
            tradeable (boolean - True)
            instrument (str - 'GBP_USD')

        :param input_financial_instrument: List of Financial Instruments (up to 20)
        :return: connection that stream prices
        """
        conn = Oanda()

        input_financial_instrument = self.currencies

        financial_instrument = input_financial_instrument[0]
        for security in input_financial_instrument[1:]:
            financial_instrument += "," + security

        params = {"instruments": financial_instrument}
        conn_params = pricing.PricingStream(accountID=conn.account_id, params=params)
        return conn.api.request(conn_params)
