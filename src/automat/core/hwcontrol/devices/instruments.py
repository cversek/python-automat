from automat.core.hwcontrol.devices.device import Device

class Instrument(Device):
    """A virtual base class for specifying common behavior of test Instrumentation"""
    pass

class Make(Instrument):
    """A virtual base class for specifying common behavior of test Instrumentation"""
    pass

class Model(Make):
    """A virtual base class for specifying common behavior of test Instrumentation"""
    pass
