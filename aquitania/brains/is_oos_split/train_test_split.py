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

Made some improvements on this class, decided to make the test set the later part of the temporal data.
"""

import abc

from aquitania.brains.is_oos_split.abstract_is_oos_split import SplitABC


class TrainTestSplit(SplitABC):
    __metaclass__ = abc.ABCMeta

    def __init__(self, test_size=None):
        """
        Instantiates the object and defines the size of the split.

        :param test_size: (float) percentage of data that will be used in the test set.
        """
        self.test_size = test_size
        super().__init__()

    def output(self, X, y):
        """
        Splits X and y according to instantiated 'test_size'.

        It will split in the DataFrame order. It is important to pass an ordered DataFrame if we are working with time
        series. As a general rule we always want our test set to be the more recent data.

        :param X: (pandas DataFrame)  features
        :param y: (pandas Series) labels

        :return: X_train, X_test, y_train, y_test
        :rtype: tuple of (pandas DataFrame, pandas Series, pandas DataFrame, pandas Series)
        """
        # Gets position where DataFrame will be cut
        threshold = int(len(X) * (1 - self.test_size))

        # Returns cut objects
        return X[:threshold], X[threshold:], y[:threshold], y[threshold:]
