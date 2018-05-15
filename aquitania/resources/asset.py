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
import datetime
import os
import _pickle as cPickle
import aquitania.resources.references as ref
import pandas as pd

from aquitania.data_source.broker.abstract_data_source import AbstractDataSource


class AssetInfo:
    # TODO make this export to a txt file and vice versa

    def __init__(self, broker_instance, list_of_currencies=ref.currencies_list):
        self.dict = {}
        for currency in list_of_currencies:
            self.dict[currency] = self.get_currency_object(currency, broker_instance)

    def get_currency_object(self, currency, broker_instance):
        folder = 'data/currencies/'

        if not os.path.exists(folder):
            os.mkdir(folder)

        print('loading... ' + currency)

        for the_file in os.listdir(folder):
            if currency in the_file:
                with open(folder + currency + '.pkl', 'rb') as f:
                    asset_obj = cPickle.load(f)
                    if asset_obj.update_on.month == datetime.datetime.now().month:
                        return asset_obj

        return self.create_new_currency_object(currency, broker_instance)

    def create_new_currency_object(self, currency, broker_instance):
        folder = 'data/currencies/'

        currency_object = Asset(currency, broker_instance)

        # Removes file in case it exists
        try:
            os.remove(folder + currency + '.pkl')
        except:
            pass

        # Writes state to disk
        # TODO there are better implementations than pickle ----> http://www.benfrederickson.com/dont-pickle-your-data/
        with open(folder + currency + '.pkl', 'wb') as f:
            cPickle.dump(currency_object, f)

        return currency_object

    def statistics(self):
        matrix = []
        for c in self.dict.values():
            osc = c.oscillation['D144']
            vol = c.volume['D144']
            min_margin = self.min_margin(c)
            if min_margin is not None:
                min_margin = round(min_margin)
            matrix.append(
                [c.type, c.currency, c.spread / osc, min_margin, c.spread, c.spread_pct, c.last_bid, c.pip, osc,
                 osc / c.last_bid, vol])

        df = pd.DataFrame(matrix).set_index(0).sort_values(2)
        df.columns = ['type', 'spread / osc', 'min_margin', 'spread', 'spread / last_bid', 'last_bid', 'last_bid/10000',
                      'osc', 'osc / last_bid', 'volume']

        return df

    def min_margin(self, c):
        order_size = float(c.min_trade_size) * float(c.last_bid)
        return self.calculate_used_margin_in_usd(c.currency, order_size)

    def calculate_used_margin_in_usd(self, currency, order_size):
        currency_1, currency_2 = currency.split('_')

        option_1 = 'USD_' + currency_2
        option_2 = currency_2 + '_USD'
        print(currency)
        print(option_1)
        print(option_2)
        print(order_size)
        print('')

        if option_1 == 'USD_USD':
            return order_size
        else:
            for currency_pair in ref.all_instruments_list:
                if currency_pair == option_1:
                    return order_size / self.dict[currency_pair].last_bid
                elif currency_pair == option_2:
                    return order_size * self.dict[currency_pair].last_bid


class Asset:
    """
    Asset object, stores qualitative data about an object.
    """
    def __init__(self, asset, broker_instance):
        """
        Instantiates a Currency object and retrieves from the broker all the important information about it.

        :param asset: (str) Asset Name
        :param broker_instance: (DataSource) Broker Instance object
        """
        self.__dict__.update(**broker_instance.gen_asset_dict(asset))


def get_currencies_statistics():
    broker_instance = AbstractDataSource('Oanda', 'Pandas')
    cur = AssetInfo(broker_instance, ref.all_instruments_list)
    df = cur.statistics()
    df.to_csv('currencies.csv')


def get_daily_osc(currency):
    broker_instance = AbstractDataSource('Oanda', 'Pandas')
    cur = AssetInfo(broker_instance, ref.all_instruments_list)
    return cur.dict[currency].oscillation['D144']
