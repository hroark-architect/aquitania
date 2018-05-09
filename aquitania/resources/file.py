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

import _pickle as cPickle

import os


# TODO there are better implementations than pickle ----> http://www.benfrederickson.com/dont-pickle-your-data/
def open(folder, filename):
    try:
        with open(folder + filename + '.pkl', 'rb') as f:
            return cPickle.load(f)
    except:
        return None


def save(object, folder, filename):
    try:
        os.remove(folder + filename + '.pkl')
    except:
        pass

    # Writes state to disk
    print(folder + filename + '.pkl')
    with open(folder + filename + '.pkl', 'wb') as f:
        cPickle.dump(object, f)
    print('seriously?')
