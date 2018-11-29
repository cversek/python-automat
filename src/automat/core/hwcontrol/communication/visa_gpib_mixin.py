import time
import visa


#Get the Base for all communications mixins
from ._base import BaseCommunicationsMixIn

#specify the smallest time between sending a command and
#noticing a response
DEFAULT_DELAY = 0.01

TIMEOUT_CODE_MAP = {
    'TNONE':    0.0,  #Never timeout.
    'T10us':    10e-6,  #10 microseconds
    'T30us':    30e-6,  #30 microseconds
    'T100us':   100e-6,  #100 microseconds
    'T300us':   300e-6,  #300 microseconds
    'T1ms':     1e-3,  #1 millisecond
    'T3ms':     3e-3,  #3 milliseconds
    'T10ms':    10e-3,  #10 milliseconds
    'T30ms':    30e-3,  #30 milliseconds
    'T100ms':   100e-3,  #100 milliseconds
    'T300ms':   300e-3, #300 milliseconds
    'T1s':      1.0, #1 second
    'T3s':      3.0, #3 seconds
    'T10s':     10.0, #10 seconds
    'T30s':     30.0, #30 seconds
    'T100s':    100.0, #100 seconds
    'T300s':    300.0, #300 seconds
    'T1000s':   1000.0, #1000 seconds
}

def check_EOL(string, EOL = None):
    if EOL is None:
        if string.endswith('\n'):
            return True
        elif string.endswith('\r'):
            return True
        else:
            return False
    elif string.endswith(EOL):
        return True
    else:
        return False 
    

class Error(Exception):
   """Base class for exceptions in this module."""
   def __init__(self,exc, info=""):
     self.exc = exc
     self.info   = info
   def __str__(self):
     if self.info:
       return "%s; %s" % (self.exc,self.info)
     else:
       return str(self.exc)

class GPIBCommunicationsMixIn(BaseCommunicationsMixIn):
  """Partial Interface for GPIB remotely contolled instruments"""
  def __init__(self,gpib_name, EOL = None):
    self.gpib_name = gpib_name
    try:
      self.gpib = visa.instrument(gpib_name)
    except visa.VisaIOError as exc:
      msg = "failed to find device named '%s'" % self.gpib_name
      raise Error(exc,msg)
    self.EOL = EOL
  #Implementation of the Base Interface Helper methods
  def _send(self,command,delay = DEFAULT_DELAY):
    try:
        self.gpib.write(command)
        # a dirty hack to prevent hangups
        # maybe we should poll the status byte?
        time.sleep(delay)
    except visa.VisaIOError as err:
        msg = "could not write to device at gpib_name '%s'" % self.gpib_name
        raise Error(err, info = msg)
         
  def _read(self, chunk_size = None):
    #chunk size is ignored but included for compatibility with linux_gpib_mixin
    try:
        return self.gpib.read()
    except visa.VisaIOError as err:
        msg = "could not read from device at gpib_name '%s'" % self.gpib_name
        raise Error(err, info=msg)
  def _exchange(self, command):
    """Write a command, pause, read the response use only for query commands 
       which return quickly.  If the completion time of the command is large
       or uknown use the method _wait_on_exchange 
    """
    return self.gpib.ask(command)
  def _wait_on_command(self, command, mask=None, poll_delay = DEFAULT_DELAY):
    """Send a command, then serial poll until one of the mask events is matched.
       'mask' is an integer with bit events defined by the particular instrument.
       If no mask is specified the command will return when the status changes
    """
    if mask is None: #not specified
      mask = 0xFF #match any event
    self._send(command, delay = poll_delay)
    time.sleep(poll_delay)
    #serial poll the instrument and get the status byte
    # and convert the character to an integer
    stb = 0 #start with no flags
    while(not(stb & mask)):
      time.sleep(poll_delay)
      stb = self.gpib.stb
  def _wait_on_exchange(self,command, mask=None, poll_delay = DEFAULT_DELAY):
    """Call '_wait_on_command' then read and return the response
    """
    self._wait_on_command(command,mask,poll_delay)
    return self._read()
  def _clear(self):
    pass    
    #self.gpib.clear()
  def _set_timeout(self, val):
    val = TIMEOUT_CODE_MAP.get(val,val) #filter string style code values for compatibilty with linux-gpib
    self.gpib.timeout = val
  def _isStatusBitSet(self,bit):
    "Mask out the value of the nth status bit"
    int(bit)
    if not 0 <= bit <= 7:
      raise Error("Status Bit must be 0 <= bit <= 7")
    #serial poll the instrument and get the status byte
    # and convert the character to an integer
    stb = self.gpib.stb
    #shift left to the bit location and extract value, returns True/False
    return bool(sta & (1 << bit))
