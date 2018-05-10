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

from aquitania.execution.order_size import OrderSize


class RiskManager:

    # TODO deal with different set of leverage rules for weekends (and also atypical events or other...)

    def __init__(self, broker_instance, currencies_obj, max_single_currency_exposure=0.3, max_exposure=90):
        self.broker_instance = broker_instance
        self.currencies_obj = currencies_obj

        self.max_single_currency_exposure = max_single_currency_exposure
        self.max_exposure = max_exposure

    def max_exposure_for_one_trade(self, currency):
        osc = self.currencies_obj.dict[currency].oscillation['D144']
        sizing = OrderSize(self.broker_instance, self.currencies_obj)
        return sizing.calculate_order_size(currency, self.max_single_currency_exposure, osc)

    def alavancagem(self, used_margin):
        balance = self.broker_instance.get_account_balance()
        return used_margin / balance

    def relation_max_exposure(self, used_margin):
        return self.alavancagem(used_margin) / self.max_exposure
