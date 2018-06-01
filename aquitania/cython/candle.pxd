from cpython.datetime cimport datetime

cdef class Candle:
    cdef:
        public int ts
        public int currency
        public int datetime
        public int open_time
        public int close_time
        public tuple open
        public tuple high
        public tuple low
        public tuple close
        public long volume
        public bint complete

    cpdef higher_than(self, Candle candle, bint up)

    cpdef ascending(self, Candle candle, bint up)

    cpdef new_ts(self, int ts)

    cpdef lower_eclipses(self, Candle candle, bint up)

    cpdef higher_eclipses(self, Candle candle, bint up)

    cpdef eclipses(self, Candle candle, bint up)

    cpdef datetime init_open_close_times(self, int ts)
