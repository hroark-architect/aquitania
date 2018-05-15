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

Created this class on February 17th 2018. After working on the Titanic challenge on Kaggle, I had some ideas as how to
organize my models and facilitate testing other models and doing ensemble models in the future.
"""

import abc
import pandas as pd

class AbstractModel:
    __metaclass__ = abc.ABCMeta

    def __init__(self, clf):
        self.clf = clf
        self.importance_of_columns = None
        self.features = None

    def get_importance_columns(self):
        return pd.Series(self.importance_of_columns, index=self.features).sort_values()

    @abc.abstractmethod
    def fit(self, X, y):
        # Makes it easier to read columns
        self.features = X.columns

    @abc.abstractmethod
    def predict(self, X):
        pass
