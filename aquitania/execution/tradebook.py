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
from aquitania.execution.order import Order


class TradeBook:

    def __init__(self, broker_instance, list_of_trades=[]):
        self.broker_instance = broker_instance
        self.trades = list_of_trades
        self.sync()

    def get_used_margin(self):
        used_margin = 0

        for trade in self.trades:
            used_margin += trade.margin_in_usd

        return used_margin

    def add(self, order):
        self.trades.append(order)

    def sync(self):
        new_list = []
        list_of_trades = self.broker_instance.get_list_of_trades()
        for oanda_trade in list_of_trades:
            added = False
            for trade in self.trades:
                if trade.currency == oanda_trade['instrument'] and oanda_trade['currentUnits'] == abs(trade.size):
                    new_list.append(trade)
                    added = True
            if added is False:
                order = self.create_order_from_oanda(oanda_trade)
                new_list.append(order)
                print('Order from Oanda added into TradeBook')

        self.trades = new_list

    def create_order_from_oanda(self, oanda_trade):
        currency = oanda_trade['instrument']

        size = float(oanda_trade['currentUnits'])
        if size < 0:
            size = abs(size)
            is_buy = False
        else:
            is_buy = True

        entry_point = oanda_trade['price']

        precision_digits = len(entry_point.split('.')[1])

        is_limit = True

        margin_used = float(oanda_trade['marginUsed']) * 100

        order = Order(self.broker_instance, currency, is_buy, size, 0.0, 0.0, entry_point, precision_digits, is_limit,
                      margin_used)
        order.open = True
        return order

    def __getitem__(self, position):
        """
        Overwrites parent class method to get item from the object.

        Returns an item from .trades attribute.

        This enables us to use a slew of Pythonic methods.

        This was added through Luciano Ramalho's book: Fluent Python. (20/01/2018)

        :param position: desired Position.
        :return: Trade located in [position]
        :rtype: Order
        """
        return self.trades[position]
