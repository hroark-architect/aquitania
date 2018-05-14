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

import pandas as pd


def convert_candles_from_nt8(filename, folder):
    """
    Get candles From NT8 and puts them into pandas DataFrame format. Input must end with: '.Bid.txt'

    :param filename: (str) Asset Name (Ex.: AUDJPY - six digits format)
    :param folder: (str) Folder name where the original file is located
    """
    # Routine to convert NT8 into DataFrame
    # TODO add routine to sanitize candles
    cols = ['open', 'high', 'low', 'close', 'volume']
    # TODO check this read_csv
    df = pd.read_csv('{}/{}.Bid.txt'.format(folder, filename), sep=';', parse_dates=[0], index_col=0, columns=cols)
    proc_filename = filename[0:3] + '_' + filename[4:6]
    df.to_hdf('{}/{}.h5'.format(folder, proc_filename))
