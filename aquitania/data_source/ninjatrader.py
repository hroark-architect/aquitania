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

from datetime import datetime

import os
import pandas as pd

from aquitania import resources as dtfx
from aquitania.resources.candle import Candle


class ConvertCandlesToNT8:
    def __init__(self, df, currency):
        bidType = 'Bid'
        filename = currency + '.' + bidType + ".txt"
        file = open(filename, 'w')
        for datetime, upen, high, low, close, volume in df.itertuples():
            candle = Candle(datetime, upen, high, low, close, volume)
            # yyyyMMdd HHmmss; open price; high price; low price; close price; volume
            str_time = candle.getDateTime().strftime('%Y%m%d %H%M%S')
            str_o = str(candle.getOpenValue())
            str_h = str(candle.getHighValue())
            str_l = str(candle.getLowValue())
            str_c = str(candle.getCloseValue())
            vol = str(candle.getVolume())
            sep = '; '
            line = str_time + sep + str_o + sep + str_h + sep + str_l + sep + str_c + sep + vol
            print(line)
            file.write(line + '\n')
        file.close()


class ConvertCandlesFromNT8:
    """
    Get candles From NT8 and puts them into pandas DataFrame format.
    """

    def __init__(self, filename):
        """
        Needs 'filename' for export NT8 file.

        :param filename: File name (String)
        Important to notice the file must be in folder: 'repository/test/'
        File must end with: '.Bid.txt'
        """
        # Initializes list that will store lines of what will be a DataFrame
        x = []

        # Creates attribute filename (will be used in other methods)
        self.filename = filename

        # Routine to convert NT8 into DataFrame
        with open('repository/test/' + self.filename + '.Bid.txt', 'r') as file:
            for line in file:
                line = line.strip()
                line = line.split(";")
                line[0] = dtfx.next_candle_datetime(datetime.strptime(line[0], '%Y%m%d %H%M%S'), -1)
                is_working = dtfx.is_fx_working_hours_from_tz(line[0])

                # candle_time = dtfx.next_candle_datetime(datetime.strptime(line[0], '%Y%m%d %H%M%S'), -1)
                # line = (candle_time, float(line[1]), float(line[2]), float(line[3]), float(line[4]), int(line[5]))
                line = map(self.convert_string_to_float, line)
                if is_working:
                    x.append(line)

        self.df = pd.DataFrame(x, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        self.df = self.df.set_index('datetime')

        self.write_to_disk()

    def write_to_disk(self):
        """
        Writes 'self.df' to disk in HDF5 format.
        """
        path = 'repository/test/processed_ninja_' + self.filename
        if os.path.isfile(path):
            os.unlink(path)

        with pd.HDFStore(path) as hdf:
            hdf.append(key='G01', value=self.df, format='table', data_columns=True, dropna='any')

    def convert_string_to_float(self, element):
        """
        Checks if it is string, in case it is converts to float.

        :param element: Element to be converted in case it is String

        :return: Converted element (in case entry element was String)
        :rtype: Float (If entry String) or Other (if entry Other)
        """
        if isinstance(element, str):
            element = float(element)

        return element


def get_stored_data(type_data_storage, currency):
    if type_data_storage == 'Pandas':
        return load_currency_hdf5(currency)


def load_currency_hdf5(currency):
    currency = currency.replace("_", "")

    folder = 'repository/test/'

    # Create folder if it doesn't exist
    if not os.path.isdir(folder):
        os.makedirs(folder)

    with pd.HDFStore(folder + 'processed_ninja_' + currency) as hdf:
        df = hdf.get(key='G01')
        return df
