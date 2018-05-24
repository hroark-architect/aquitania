########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||||#
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||||#
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||||#
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||||#
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||||#
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||||#
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||#
########################################################################################################################

"""
.. moduleauthor:: H Roark

"""

import pandas as pd

from aquitania.brains.evaluator import Evaluator


class ModelManager:
    def __init__(self, model, is_oos_split_object, transformer):
        self.model = model
        self.is_oos_split_object = is_oos_split_object
        self.transformer = transformer

        self.evaluator = Evaluator(transformer)

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def evaluate(self, X, predictions, y, is_test):
        df = X[['ratio', 'ratio_inverted']].copy()
        df['raw_predict'] = predictions
        df = self.transformer.transform_proba(df)
        df['results'] = y
        eval_df = self.evaluator.evaluate_output(df, is_test)

        return eval_df

    def fit_predict_evaluate(self, X, y):
        """
        Gets the train and test sets and make predictions for them and evaluate how accurate these predictions are.

        It only outputs test predictions. This architecture has a lot of possible improvements to it.

        :param X:
        :param y:
        :return: Evaluation of test predictions
        :rtype
        """
        x_train, x_test, y_train, y_test = self.is_oos_split_object.output(X, y)

        train_predictions = self.grid_search(x_train, y_train)

        # Test goes before train to get Test buckets form prediction proba
        test_predictions = self.predict(x_test)

        # Run evaluation routine
        self.evaluate(x_train, train_predictions, y_train, False)
        test_eval = self.evaluate(x_test, test_predictions, y_test, True)

        self.evaluator.overfit_metrics()

        return test_eval

    def grid_search(self, x_train, y_train):
        score_list = []
        params_list = []
        for params in self.model.gen_grid_search():
            print(params)
            self.model.restart_model(params)
            self.fit(x_train, y_train)
            score = self.model.get_score()
            score_list.append(score)
            params_list.append(params)

        print('Grid Search Results:')
        print(pd.DataFrame([[p, s] for p, s in zip(params_list, score_list)]))

        max_params = params_list[score_list.index(max(score_list))]

        print('Best params:')
        print(max_params)
        self.model.restart_model(max_params)
        self.fit(x_train, y_train)

        return self.predict(x_train)

    def get_features(self):
        # TODO needs to decide how this will deal with multiple models and etc
        return self.model.get_importance_columns()
