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

This class was created on late December 2017, that was when I started working with AI using only Random Forest
algorithms.

Going through a big refactor on 17th February 2018, create AbstractModel class, removed a lot of content inside of this
class, it was almost doing everything alone, now I moved out a lot of its functionality, and it is being designed to be
a piece of a whole system of models and predictors.
"""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from aquitania.brains.models.abstract_model import AbstractModel


class RandomForestClf(AbstractModel):
    """
    RandomForest class gets a list of currencies a signal and exits and creates an algorithm to predict patterns.
    """

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            kwargs = {'n_jobs': -1, 'max_features': .5, 'n_estimators': 25, 'min_samples_leaf': 25}

        self.kwargs = kwargs

        super().__init__(RandomForestClassifier(**kwargs))

    def fit(self, X, y):
        self.clf.fit(X, y)
        self.importance_of_columns = self.clf.feature_importances_

        super().fit(X, y)

    def predict(self, X):
        return self.clf.predict_proba(X).T[1]

    def get_feature_importance(self):
        return pd.Series(self.importance_of_columns, index=self.features).sort_values(ascending=False)

    def gen_grid_search(self):
        gs_params = []
        max_features = [((i + 1) / 4) for i in range(4)]
        n_est = [((i + 2) ** 4) for i in range(3)]
        min_samples_leaf = [1, 5, 21, 89, 377, 2584]
        for i in max_features:
            for e in n_est:
                for s in min_samples_leaf:
                    gs_params.append(
                        {'max_features': i, 'n_estimators': e, 'min_samples_leaf': s, 'n_jobs': -1, 'oob_score': True})
        return gs_params

    def restart_model(self, params):
        self.__init__(**params)

    def get_score(self):
        return self.clf.oob_score_
