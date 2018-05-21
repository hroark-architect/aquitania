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

This module is comprised of two classes:
1. FeedManager
2. HistoricDataManager

FeedManager creates feeds for live usage.

HistoricDataManager creates databases of candles mainly to do historic tests and to create states that will be used
on live trading.
"""
import time
import multiprocessing as mp
import pandas as pd
import aquitania.resources.datetimefx as dtfx


class HistoricDataManager:
    """
    There are three main functions on the HistoricDataManager:
        1. Download Candles from server
        2. Process Candles to get them ready for storage
        3. Store candles

    As to optimize those functions and to reduce processing time, this module was built using multiprocessing.
    Each one of the 3 functions stated above has its own process, which enables us multi-thread.

    We were able to drastically reduce processing time with those measures.

    This class manages the multiprocessing, most of the hard coding is done inside the data_source module.
    """

    def __init__(self, broker_instance, finsec, is_san_n_store):
        # Checks if list or not
        self.finsec = finsec

        # Define attributes
        self._broker_instance = broker_instance

        # TODO improve this sanitize routine for live feed
        self.is_san_n_store = is_san_n_store

        self.live_start_dates = None

    def load_data(self):
        """
        Loads data from disk and returns the corresponding DataFrame.

        :return: All G01 candles of currency instantiated.
        :rtype: pandas DataFrame
        """

        df = self._broker_instance.load_data(self.finsec)
        return df

    def get_live_data(self):
        """
        Streams live_data through a MultiProcessing Queue().

        :return: Live Candles
        :rtype: List of Lists
        """
        # Create queue variables:
        q1 = mp.Queue()
        q2 = mp.Queue()
        q3 = mp.Queue()

        # Manages if candle importing is still ongoing.
        step1 = mp.Value('i', 1)
        step2 = mp.Value('i', 1)

        # Assigns a process to each one of the functions below:
        p = mp.Process(target=self.download_candles, args=(self.get_live_start_dates(), step1, q1))
        w = mp.Process(target=self.process_data, args=(step1, step2, q1, q2, q3))

        # Start all the multiprocessing
        p.start()
        w.start()

        # Wait for the multiprocessing to finish and join all of them.
        p.join()
        w.join()

        if not q3.empty():
            list_of_candles = q3.get()
            self.live_start_dates = list_of_candles[-1][0]
            return list_of_candles
        return None

    def get_live_start_dates(self):
        if self.live_start_dates is None:
            return self.get_historic_start_dates()
        else:
            return self.live_start_dates

    def update_historic_database(self, q3):
        # Create queue variables:
        q1 = mp.Queue()
        q2 = mp.Queue()

        # Manages if candle importing is still ongoing.
        step1 = mp.Value('i', 1)
        step2 = mp.Value('i', 1)

        # Assigns a process to each one of the functions below:
        p = mp.Process(target=self.download_candles, args=(self.get_historic_start_dates(), step1, q1))
        w = mp.Process(target=self.process_data, args=(step1, step2, q1, q2, q3))
        z = mp.Process(target=self.add_candles_database, args=(step2, q2))

        # Start all the multiprocessing
        p.start()
        w.start()
        z.start()

        # Wait for the multiprocessing to finish and join all of them.
        p.join()
        w.join()
        z.join()

        # Only sanitize on next run
        self.is_san_n_store = False

    def get_historic_start_dates(self):
        return self._broker_instance.get_historic_data_status(self.finsec)

    def download_candles(self, start_date, step1, q1):
        """
        Function that manages candle download from the server, uses more specific functions inside broker.

        :broker_instance Is the instance of the broker connection.
        :q1 Queue 1 is the one that will transport raw data from server download to data processor.
        """
        self._broker_instance.candle_downloader(start_date, self.finsec, q1)
        step1.value = 0

    def process_data(self, step1, step2, q1, q2, q3):
        """
        Function that processes raw data to storage ready data.

        :broker_instance Is the instance of the broker connection.
        :q1 Queue 1 is the one that will transport raw data from server download to data processor.
        :q2 Queue 2 is the one that will transport processed data to be stored on the computer.
        """
        while bool(step1.value) or not q1.empty():
            time.sleep(1)
            while not q1.empty():
                data_package = q1.get()
                c_cndl = self._broker_instance.data_processing_manager(data_package)

                # Checks if object is > 0
                if len(c_cndl) > 0:
                    # Goes to storage
                    q2.put(c_cndl)

                    # Goes to live feed
                    if isinstance(q3, mp.queues.Queue):
                        q3.put(c_cndl)

        step2.value = 0

    def add_candles_database(self, step2, q2):
        """
        Function that stores process data in the select
        
        :broker_instance Is the instance of the broker connection.
        :q2 Queue 2 is the one that will transport processed data to be stored on the computer.
        """
        # Initializes counter to verify if it is necessary to sanitize candles
        size = 0

        while bool(step2.value) or not q2.empty():
            time.sleep(1)
            while q2.empty() is False:
                list_candles = q2.get()

                # Creates pd.DataFrame in case it is already not, it is here and not in step1 for performance reasons
                if not isinstance(list_candles, pd.DataFrame):
                    list_candles = pd.DataFrame(list_candles,
                                                columns=['datetime', 'fi', 'ts', 'open', 'high', 'low', 'close',
                                                         'volume'])
                    list_candles.set_index('datetime', inplace=True)

                if list_candles.shape[0] > 0:
                    self._broker_instance.store(list_candles)
                    size += list_candles.shape[0]

        # Sanitizes candles (remove duplicates if any) in case it fetched more than 500 candles
        if size > 500:
            print('{}Sanitizing {} candles database.'.format(dtfx.now(), self.finsec))
            self._broker_instance.sanitize(self.finsec)
