from aquitania.resources.candle cimport Candle

cdef class IndicatorLoader:
    """
    An IndicatorLoader object holds all indicators for a specific Financial Security
    """

    cdef:
        public list indicator_list
        int _asset
        int _timestamp
        object _broker_instance
        list _datetimes
        list _candle_complete

    cpdef void feed(self, Candle candle)

    cdef void store_candle(self, Candle candle)

    cpdef void save_output(self)

    cdef object generate_df(self)
