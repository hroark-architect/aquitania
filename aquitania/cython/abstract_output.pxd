from abstract_indicator cimport AbstractIndicator

cdef class AbstractIndicatorOutput(AbstractIndicator):
    cdef:
        public str id
        public list columns
        public bint is_open

    cdef void set_output(self, tuple result)

    cpdef void fillna(self)
