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

from sklearn.ensemble import ExtraTreesClassifier
from aquitania.brains.models.abstract_model import AbstractModel


class ExtraTrees(AbstractModel):
    """
    RandomForest class gets a list of currencies a signal and exits and creates an algorithm to predict patterns.
    """

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            kwargs = {'n_jobs': -1, 'n_estimators': 40}

        super().__init__(ExtraTreesClassifier(kwargs))

    def fit(self, X, y):
        self.clf.fit(X, y)
        super().fit(X, y)

    def get_predictions(self, X):
        return self.clf.predict_proba(X)
