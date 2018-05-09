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

import aquitania.resources.references as ref


class OrderSize:
    def __init__(self, broker_instance, currencies_obj):
        self.broker_instance = broker_instance
        self.currencies_obj = currencies_obj

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
