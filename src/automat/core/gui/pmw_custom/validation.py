import string
###############################################################################
# Possible return values of validation functions.
OK = 1
ERROR = 0
PARTIAL = -1

class Validator(object):
    "An extensible object that will substitute for a Pmw validator function"
    def __init__(self, 
                    _min = None, 
                    _max = None, 
                    converter = float,
                    ):
        self._min = _min
        self._max = _max
        self.converter = converter
    def convert(self, text):
        "converts the text to the appropriate type"
        val = self.converter(text)
        return val
    def __call__(self, text):
        "signifies validity of text"
#        #prevent from going over the length of the maximum
#        if not self._max is None:
#            if len(text) > len(str(self._max)):
#                return ERROR
        if text in ('', '-', '+'):
            return PARTIAL
        try:
            val = self.convert(text) 
            #test range
            if not self._min is None and val < self._min:
                return PARTIAL
            elif not self._max is None and val > self._max:
                return ERROR
            else:
                return OK
        except ValueError:
            return ERROR
###############################################################################
