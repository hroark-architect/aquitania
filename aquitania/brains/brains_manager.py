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

I am not sure when I first created Abstract classes for model_manager and etc, but it was likely to be around February
2018.

Now it is May 1st of 2018, and I decided to go for a full refactor of the Brains Module. I'll create a Model Abstract
class that will handle ensembles and other more complicated structures inside it and that will behave just as like a
simpler model_manager would on its outside world methods.

I will also create the possibility to work with splitting into Train, Test, and Validation Data, and working to make a
automatic grid search for it.
"""
import _pickle
import pandas as pd

from aquitania.brains.models.random_forest import RandomForestClf
from aquitania.data_processing.analytics_loader import build_ai_df
from aquitania.data_processing.indicator_transformer import IndicatorTransformer
from aquitania.execution.oracle import Oracle
from aquitania.brains.is_oos_split.train_test_split import TrainTestSplit
from aquitania.brains.model_manager import ModelManager


class BrainsManager:
    def __init__(self, broker_instance, list_of_currencies, strategy, selector=None, model=None):
        # Set attributes
        self.broker_instance = broker_instance
        self.list_of_currencies = list_of_currencies
        self.strategy = strategy
        self.transformer = IndicatorTransformer(self.broker_instance, strategy.signal, list_of_currencies)
        self.X, self.y = self.prepare_data()

        # Sets default selector if None is chosen
        if selector is None:
            self.is_oos_selector = TrainTestSplit(test_size=0.15)

        # Sets default model if None is chosen
        if model is None:
            self.model = RandomForestClf()

        # Instantiates results variables
        self.model_manager, self.model_results, self.features = None, None, None

    def run_model(self, model=None, selector=None):
        # Sets previous selector if None is chosen
        if selector is None:
            selector = self.is_oos_selector

        # Sets previous model if None is chosen
        if model is None:
            model = self.model

        # Instantiates ModelManager
        self.model_manager = ModelManager(model, selector, self.transformer)

        # Make predictions
        self.model_results = self.model_manager.fit_predict_evaluate(self.X, self.y)

        # Print feature importance
        print('\n----------------------------')
        print('FEATURE IMPORTANCE:')
        print('----------------------------')
        print(self.model_manager.model.get_feature_importance())

        # Fixing bug of not saving strategy to disk
        self.save_strategy_to_disk()

    def prepare_data(self):
        # Gets Raw Data
        X = build_ai_df(self.broker_instance, self.list_of_currencies, self.strategy.signal.entry)

        # Print DataFrame size
        print('original DataFrame size:', X.shape)

        # Get results set
        y = self.generate_results_set(self.strategy.signal.entry)

        # Transform
        transformed_df = self.transformer.transform(X, y)

        # Return transformed_df
        return transformed_df

    def generate_results_set(self, signal):
        results_set = None
        # Load results set
        for currency in self.list_of_currencies:
            if results_set is None:
                results_set = pd.read_hdf('data/liquidation/' + currency + '_' + signal + '_CONSOLIDATE')
            else:
                temp_df = pd.read_hdf('data/liquidation/' + currency + '_' + signal + '_CONSOLIDATE')
                results_set = pd.concat([results_set, temp_df])

        return results_set

    def save_strategy_to_disk(self):
        """
        Pickles all the required strategy elements to make it work on the LiveEnvironment and make decisions about which
        trades are valid and which aren't.
        """

        # Instantiates Oracle object (Object that makes predictions)
        oracle = Oracle(self.strategy.signal, self.model_manager, self.features, self.transformer, *self.model_results)

        # Saves Oracle into Disk
        with open('data/model_manager/{}.pkl'.format(self.strategy.__class__.__name__), 'wb') as f:
            _pickle.dump(oracle, f)
