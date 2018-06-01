from candle cimport Candle

cdef class Feeder:
    cdef public int asset
    cdef list _loaders
    cdef list _candles

    cdef feed(self, Candle candle)

    cdef missing_closed_candles(self, list criteria_table)

    cdef make_candle(self, int ts, Candle candle, list criteria_table)

    cdef generate_criteria_table(self, Candle candle)

    cdef new_candle_routine(self, int ts, Candle candle)

    cdef new_candle(self, int ts, Candle candle)

    cdef set_values(self, int ts, Candle candle)

    cdef is_closing_candle(self, int ts, Candle candle)

    cpdef exec_df(self, object df)

    cdef instantiate_first_candle(self, df_line)