class Device(object):
    """A virtual base class for specifying common behavior of test Intsrumentation"""
    def identify(self):
        raise NotImplementedError
    def initialize(self):
        raise NotImplementedError
    def shutdown(self):
        raise NotImplementedError
    def test(self):
        raise NotImplementedError

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
    def __nonzero__(self):
        "implements a False truth value"
        return False

class DeviceError(Exception):
    pass
