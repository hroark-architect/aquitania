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

12/04/2018 - Created a simple selector instead of a complicated structure I used before.
"""

from aquitania.data_source.broker.oanda import Oanda
from aquitania.data_source.broker.fxcm import FXCM
from aquitania.data_source.broker.test_broker import TestBroker


def select_broker(broker_name, data_storage_name):
    """
    Instantiates a DataSource object (there is a AbstractDataSource class).

    DataSource objects defines all the methods necessary to communicate and fetch data from a single source as well as
    to send orders into market and to get some kind of broker specific information.

    There are behaviors that still need to be refactored and improved, in special the ones related to Currency class.

    One interesting thing to do in the future is to make Aquitania work with multiple DataSource objects simultaneously
    as different kinds of data requires different DataSources.

    :param broker_name: (str) Broker Name (Ex.: oanda, fxcm, test)
    :param data_storage_name: (str) Identifier of Data Storage System (pandas_hdf5)
    """
    broker_name = broker_name.lower()
    if broker_name == 'oanda':
        return Oanda(broker_name, data_storage_name)
    elif broker_name == 'fxcm':
        return FXCM(broker_name, data_storage_name)
    elif broker_name == 'test':
        return TestBroker(broker_name, data_storage_name)
    else:
        raise NameError('Invalid Broker Name')
