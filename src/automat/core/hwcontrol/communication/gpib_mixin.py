#dynamically load the correct GPIB driver depending on platform setup
#try importing the visa driver first
try:
    from .visa_gpib_mixin import GPIBCommunicationsMixIn
except ImportError:  #probably because VISA driver or python-visa is not installed (Maybe platform is linux)
    #try importing the linux-gpib driver
    from .linux_gpib_mixin import GPIBCommunicationsMixIn

