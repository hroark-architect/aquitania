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
from sklearn.model_selection import StratifiedKFold

from aquitania.brains.model_selection.abstract_model_selection import AbstractModelSelection


class KFolder(AbstractModelSelection):
    def __init__(self, number_splits=10):
        self.model_selector = StratifiedKFold(n_splits=number_splits)
        self.number_repeat = number_splits

    def output_fit(self, X, y):
        output = [(X.iloc[x_tuple[0]], y.iloc[x_tuple[0]]) for x_tuple in self.model_selector.split(X, y)]
        x_output, y_output = zip(*output)
        return x_output, y_output

    def output_predict(self, X):
        return self.model_selector.split(X)
