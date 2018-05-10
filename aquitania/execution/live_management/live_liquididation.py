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

from aquitania.data_source.broker.oanda import OandaStream


class LiveLiquidation:
    def __init__(self, broker_instance):
        self.broker_instance = broker_instance

    def get_currencies(self):
        currencies = set()
        for trade in self.broker_instance.get_list_of_trades():
            currencies.add(trade['instrument'])

        return list(currencies)

    def routine_for_stream(self, currency, price):
        # TODO how to deal with this issue?
        return
        # for trade in self.order_manager.tradebook:
        #   if trade.currency == currency and trade.open:
        #      trade.eval_price(float(price))

    def run_stream(self):
        # TODO when entering a trade find a way to update stream

        print('restart')
        currencies = self.get_currencies()
        print(currencies)
        stream = OandaStream(currencies)

        if currencies:
            stream_data = stream.stream()

            for line in stream_data:
                print(line)
                if line['type'] == 'PRICE':
                    currency = line['instrument']
                    price = line['bids'][0]['price']
                    self.routine_for_stream(currency, price)
