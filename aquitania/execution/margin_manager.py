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


class MarginManager:
    def __init__(self, broker_instance, currencies_obj):
        self.broker_instance = broker_instance
        self.currencies_obj = currencies_obj

    def calculate_used_margin_in_usd(self, currency, order_size):
        currency_1, currency_2 = currency.split('_')

        option_1 = 'USD_' + currency_1
        option_2 = currency_1 + '_USD'

        if option_1 == 'USD_USD':
            return order_size
        else:
            for currency_pair in ref.currencies_list:
                if currency_pair == option_1:
                    return order_size / self.currencies_obj.dict[currency_pair].last_bid
                elif currency_pair == option_2:
                    return order_size * self.currencies_obj.dict[currency_pair].last_bid

    def calculate_size_given_margin(self, currency, margin):

        currency_1, currency_2 = currency.split('_')

        option_1 = 'USD_' + currency_1
        option_2 = currency_1 + '_USD'

        if option_1 == 'USD_USD':
            order_size = margin
        else:
            for currency_pair in ref.currencies_list:
                if currency_pair == option_1:
                    order_size = margin * self.currencies_obj.dict[currency_pair].last_bid
                elif currency_pair == option_2:
                    order_size = margin / self.currencies_obj.dict[currency_pair].last_bid

        return order_size

    def margin_percentual(self, margin_used):
        balance = self.broker_instance.get_account_balance()
        return margin_used / balance
