from gpib import GpibError
from Gpib import Gpib  #object oriented interface
import time

#Get the Base for all communications mixins
from _base import BaseCommunicationsMixIn

#specify the smallest time between sending a command and
#noticing a response
DEFAULT_DELAY = 0.01


TIMEOUT_CODE_MAP = {
    'TNONE':    0,  #Never timeout.
    'T10us':    1,  #10 microseconds
    'T30us':    2,  #30 microseconds
    'T100us':   3,  #100 microseconds
    'T300us':   4,  #300 microseconds
    'T1ms':     5,  #1 millisecond
    'T3ms':     6,  #3 milliseconds
    'T10ms':    7,  #10 milliseconds
    'T30ms':    8,  #30 milliseconds
    'T100ms':   9,  #100 milliseconds
    'T300ms':   10, #300 milliseconds
    'T1s':      11, #1 second
    'T3s':      12, #3 seconds
    'T10s':     13, #10 seconds
    'T30s':     14, #30 seconds
    'T100s':    15, #100 seconds
    'T300s':    16, #300 seconds
    'T1000s':   17, #1000 seconds
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
            self.gpib = Gpib(gpib_name)
        except GpibError, exc:
            msg = "failed to find device named '%s'" % self.gpib_name
            raise Error(exc,msg)
        #fix for older versions of Gpib
        if hasattr(self.gpib, "rsp"):
            self.gpib.serial_poll = getattr(self.gpib, "rsp")
        self.EOL = EOL

    #Implementation of the Base Interface Helper methods
    def _send(self,command,delay = DEFAULT_DELAY):
        try:
            self.gpib.write(command)
            # a dirty hack to prevent hangups
            # maybe we should poll the status byte?
            time.sleep(delay)
        except GpibError, err:
            msg = "could not write to device at gpib_name '%s'" % self.gpib_name
            raise Error(err, info = msg)

    def _read(self, chunk_size = 512):
        buff = []
        try:
            while True:
                chunk = self.gpib.read(chunk_size)
                buff.append(chunk)
                if check_EOL(chunk,self.EOL):
                    buff = "".join(buff)
                    return buff.strip()
        except GpibError, err:
            msg = "could not read from device at gpib_name '%s'" % self.gpib_name
            raise Error(err, info=msg)

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
            stb = ord(self.gpib.serial_poll())
    def _wait_on_exchange(self,command, mask=None, poll_delay = DEFAULT_DELAY):
        """Call '_wait_on_command' then read and return the response
        """
        self._wait_on_command(command,mask,poll_delay)
        return self._read()
    def _clear(self):
        self.gpib.clear()
    def _set_timeout(self,val):
        val = TIMEOUT_CODE_MAP[val]
        try:
            self.gpib.timeout(val)
        except AttributeError: #older versions of linux-gpib use function 'tmo'
            self.gpib.tmo(val)
    def _isStatusBitSet(self,bit):
        "Mask out the value of the nth status bit"
        bit = int(bit)
        if not 0 <= bit <= 7:
            raise Error("Status Bit must be 0 <= bit <= 7")
        #serial poll the instrument and get the status byte
        # and convert the character to an integer
        stb = ord(self.gpib.serial_poll())
        #shift left to the bit location and extract value, returns True/False
        return bool(sta & (1 << bit))
    def _close(self):
        pass #do nothing?
