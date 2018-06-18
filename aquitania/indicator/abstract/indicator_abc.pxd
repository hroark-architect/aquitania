from aquitania.resources.candle cimport Candle

cdef class AbstractIndicator:
    cdef:
        public bint up
        public Candle last_candle
        public tuple last_output
        public list output_list

    cpdef void feed(self, Candle candle)

    cdef void set_output(self, tuple result)



