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
import time
import pandas as pd


class Order:
    def __init__(self, broker_instance, currency, spread, is_buy, size, stop, profit, entry_point, precision_digits,
                 is_limit, margin_in_usd):
        self.executed = False
        self.open = False

        self.broker_instance = broker_instance
        self.currency = currency
        self.is_buy = is_buy
        self.size = size
        self.spread = spread
        self.stop = self.calc_stop(stop)
        self.profit = self.calc_profit(profit)
        self.is_limit = is_limit
        self.entry_point = entry_point
        self.precision_digits = precision_digits
        self.margin_in_usd = margin_in_usd

    def calc_stop(self, stop):
        if self.is_buy:
            return stop
        else:
            return stop + self.spread

    def calc_profit(self, profit):
        if self.is_buy:
            return profit
        else:
            return profit + self.spread

    def eval_price(self, price):
        if self.is_buy:
            if self.profit != 0 and price >= self.profit:
                self.profit_hit()
            elif self.stop != 0 and price <= self.stop:
                self.stop_hit()
        else:
            if self.profit != 0 and price <= self.profit:
                self.profit_hit()
            elif self.stop != 0 and price >= self.stop:
                self.stop_hit()

    def profit_hit(self):
        if self.check_trade_on_broker():
            self.exit_at_market()

    def stop_hit(self):
        if self.check_trade_on_broker():
            self.exit_at_market()

    def check_trade_on_broker(self):
        lot = self.broker_instance.get_list_of_trades()
        for t in lot:
            if t['instrument'] == self.currency:
                if abs(float(t['currentUnits'])) == self.size:
                    return True
        return False

    def exit_at_market(self):
        if self.is_buy:
            size = -self.size
        else:
            size = self.size

        while not self.broker_instance.order(0.0, 0, size, self.currency):
            print('order failed: ', self)
            time.sleep(1)
        else:
            self.open = False

    def enter_at_limit(self):
        print('enter at limit')
        if self.is_buy:
            size = self.size
        else:
            size = -self.size

        order_exec = self.broker_instance.order(self.entry_point, self.precision_digits, size, self.currency,
                                                self.profit, self.stop)

        if order_exec[0]:
            self.executed = True
            self.open = True

        return self.to_df(order_exec[1], order_exec[2])

    def to_df(self, price_executed, id):
        data = [[id, self.currency, self.is_buy, self.size, self.executed, self.open, self.entry_point, self.spread,
                price_executed]]
        columns = ['id', 'currency', 'is_buy', 'size', 'is_exec', 'is_open', 'entry_point', 'spread', 'price_executed']
        return pd.DataFrame(data, columns=columns)

# TODO improve order execution routine
# work with execution data (get execution price)
# need to handle when order was in fact executed
