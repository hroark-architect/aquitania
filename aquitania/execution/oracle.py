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
import numpy as np
from aquitania.execution.oracle_criteria import OracleCriteria


class Oracle:
    """
    The Oracle predicts the future. It has learned through multiple years of careful studies on historical data and
    sophisticated Artificial intelligence methods to avail on profitable trading opportunities.

    This is the decision making part of Aquitania, the Oracle metaphor is a very good one indeed, because it is this
    part of the system that will in fact predict the future and guide the decisions that will be taken.
    """

    def __init__(self, signal, model_manager, features, transformer, bet_sizing_dict, i_bet_sizing_dict):
        """
        Instantiates the Oracle with all the necessary requirements for it.
        :param signal: (Signal) Signal Indicator
        :param model_manager: (ModelManager) Model Manager
        :param features: (pandas DataFrame columns) Features to be evaluated on the strategy
        :param transformer: (IndicatorTransformer) Transformer that was used during the backtest
        :param bet_sizing_dict: (pandas DataFrame) Truth Table for normal trades
        :param i_bet_sizing_dict: (pandas DataFrame) Truth Table for inverted trades
        """
        # Initializes  variables
        self.signal = signal
        self.model_manager = model_manager
        self.features = features
        self.transformer = transformer

        # Instantiates Criteria object (object that will compare predictions with truth tables)
        self.criteria = OracleCriteria(transformer, bet_sizing_dict, i_bet_sizing_dict)

    def predict(self, output):
        """
        Oracle predicts the future given an output from the indicators.

        :param output: (pandas DataFrame) Output of all indicators pre-processed

        :return: tuple containing 5 elements:
            make_trade (bool): True if trade
            is_inverted (bool): True if trade needs to be inverted
            size (float): order size
            proba (int): bracket of probability
            used_ratio (int): bracket of ratio
        :rtype: tuple of 5 elements
        """
        # Instantiates Variables
        signal_id, complete = self.signal.ok, 'complete_{}'.format(self.signal.ok[0])

        # Only evaluates if there is an output, the signal candle is closed, and there is a valid signal
        if output is not None and output[complete].any() and output[signal_id].any():
            # Reshapes output
            output_array = np.array(output).reshape(1, -1)

            # Get predictions for given output
            predict_proba = self.model_manager.predict(output_array)[0]

            # Get proba_bracket
            proba_bracket = self.transformer.get_proba_bin(predict_proba)

            # Calculates Ratios
            ratio, inverse_ratio = output[['ratio', 'ratio_inverted']].values[0]  # Result is a list of lists

            # Returns evaluate if the trading Criteria was met
            return self.criteria.met(proba_bracket, ratio, inverse_ratio)

        else:
            # Don't Trade
            return False, False, 0.0, 0, 0
