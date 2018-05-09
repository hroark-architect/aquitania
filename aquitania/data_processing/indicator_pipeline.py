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

Studying Pipelines through 'Hands-On Machine Learning...' on 29/01/2018.
"""


class IndicatorPipeLine:
    def __init__(self):
        pass

    def fit(self):
        pass

    def transform(self):
        pass

    def fit_transform(self, X):
        X = a_favor(X)
        X = max_min(X)
        return X


def a_favor(df):
    for column in df:
        if 'alta' in column:
            df[column] = df[column] == df['signal']
    return df


def max_min(df):
    for column in df:
        if 'sup' in column:
            df[column + '_favor'] = ((df[column] == df['signal']) & (df['signal']))
        if 'res' in column:
            df[column + '_favor'] = ((df[column] == ~df['signal']) & (~df['signal']))
    return df
