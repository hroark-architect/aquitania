from aquitania.indicator.abstract.indicator_abc cimport AbstractIndicator

cdef class AbstractIndicatorOutput(AbstractIndicator):
    cdef:
        public str id
        public list columns
        public bint is_open

    cpdef void save_output(self)
