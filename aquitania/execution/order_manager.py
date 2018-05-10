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

import pandas as pd

from aquitania.execution.margin_manager import MarginManager
from aquitania.execution.order import Order
from aquitania.execution.risk_manager import RiskManager
import aquitania.resources.references as ref


class OrderManager:
    def __init__(self, broker_instance, currencies_obj):
        self.broker_instance, self.currencies_obj = broker_instance, currencies_obj

        self.risk_manager = RiskManager(broker_instance, currencies_obj)
        self.margin_manager = MarginManager(broker_instance, currencies_obj)

    def new_order(self, currency_int, is_buy, size_str, stop, profit, entry_point):
        stop, profit, entry_point = abs(stop), abs(profit), abs(entry_point)

        currency = ref.currencies_list[currency_int]

        size = self.calculate_order_size(currency, float(size_str), abs(entry_point - stop))

        # Gets the maximum size limit per order for specific currency
        max_size = self.risk_manager.max_exposure_for_one_trade(currency)

        # Checks if trade is over the maximum limit per order
        if size > max_size:
            size = max_size

        # Checks total_exposure
        used_margin = self.broker_instance.get_used_margin()

        # Remaining margin routine
        balance = self.broker_instance.get_account_nav()
        remaining_margin = (balance * self.risk_manager.max_exposure) - used_margin

        margin = self.margin_manager.calculate_used_margin_in_usd(currency, size)
        if margin > remaining_margin:
            size = self.margin_manager.calculate_size_given_margin(currency, remaining_margin)

        # Check if order exceeds maximum order size
        # TODO use float on the source
        max_order = float(self.currencies_obj.dict[currency].max_order)

        if max_order < size:
            size = max_order

        # Calculate Entry Point for Limit Order
        entry_quote, precision_digits, spread = self.calculate_entry_quote(is_buy, currency, entry_point)

        print('sizes: ', size_str, ' ', size)
        size = round(size)

        if size > 0:
            # Create new Order object
            new_order = Order(self.broker_instance, currency, spread, is_buy, size, stop, profit, entry_quote,
                              precision_digits, is_limit=True, margin_in_usd=margin)

            df = new_order.enter_at_limit()
            return df
        else:
            return self.insufficient_margin_df(currency, is_buy, size, entry_quote, spread)

    def insufficient_margin_df(self, currency, is_buy, size, entry_quote, spread):
        data = [[0, currency, is_buy, size, False, False, entry_quote, spread, 0.0]]
        columns = ['id', 'currency', 'is_buy', 'size', 'is_exec', 'is_open', 'entry_point', 'spread', 'price_executed']
        return pd.DataFrame(data, columns=columns)

    def calculate_entry_quote(self, is_buy, currency, entry_point):
        entry = abs(entry_point)
        spread = self.currencies_obj.dict[currency].spread

        if is_buy:
            entry = entry + (spread * 2)
        else:
            entry = entry - spread

        precision_digits = self.currencies_obj.dict[currency].precision_digits

        print(entry, precision_digits)
        print(round(entry, precision_digits))

        spread = self.currencies_obj.dict[currency].spread

        return entry, precision_digits, spread

    def calculate_order_size(self, currency, bet_size, stop_in_pips):
        balance = self.broker_instance.get_account_balance()

        currency_1, currency_2 = currency.split('_')

        option_1 = 'USD_' + currency_2
        option_2 = currency_2 + '_USD'

        if option_1 == 'USD_USD':
            stop_in_pips_in_usd = stop_in_pips
        else:
            for currency_pair in ref.currencies_list:
                if currency_pair == option_1:
                    stop_in_pips_in_usd = stop_in_pips / self.currencies_obj.dict[currency_pair].last_bid
                elif currency_pair == option_2:
                    stop_in_pips_in_usd = stop_in_pips * self.currencies_obj.dict[currency_pair].last_bid

        order_size = ((bet_size * balance) / stop_in_pips_in_usd) // 1

        return order_size
