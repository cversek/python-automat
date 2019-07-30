class Device(object):
    """A virtual base class for specifying common behavior of test Intsrumentation"""
    def identify(self):
        raise NotImplementedError("in class %r" % self.__class__)
    def initialize(self):
        raise NotImplementedError("in class %r" % self.__class__)
    def shutdown(self):
        raise NotImplementedError("in class %r" % self.__class__)
    def test(self):
        raise NotImplementedError("in class %r" % self.__class__)

class StubDevice(object):
    """A stubbed out Device"""
    def identify(self):
        return "StubDevice"
    def initialize(self):
        pass
    def shutdown(self):
        pass
    def test(self):
        return (True, "")
        
class NullDevice(StubDevice):
    """A nothing device"""
    def __bool__(self):
        "implements a False truth value"
        return False

class DeviceError(Exception):
    pass
