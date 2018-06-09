from cpython.datetime cimport datetime

cdef class Candle:
    cdef:
        public unsigned char ts
        public unsigned char currency
        public datetime datetime
        public datetime open_time
        public datetime close_time
        public tuple open
        public tuple high
        public tuple low
        public tuple close
        public long volume
        public bint complete

    cpdef bint lower_than(self, Candle candle, bint up)

    cpdef bint higher_than(self, Candle candle, bint up)

    cpdef bint ascending(self, Candle candle, bint up)

    cpdef Candle new_ts(self, int ts)

    cpdef Candle copy(self)

    cpdef bint lower_eclipses(self, Candle candle, bint up)

    cpdef bint higher_eclipses(self, Candle candle, bint up)

    cpdef bint eclipses(self, Candle candle, bint up)

    cpdef bint is_same_open_time(self, Candle candle)

    cpdef bint upper_shadow(self, bint up)

    cpdef bint lower_shadow(self, bint up)
