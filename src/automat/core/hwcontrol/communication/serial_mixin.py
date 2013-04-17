import serial #pyserial library
from serial.serialutil import SerialException
import time

#Get the Base for all communications mixins
from _base import BaseCommunicationsMixIn

#specify the smallest time between sending a command and
#noticing a response
DEFAULT_DELAY = 0.05
DEFAULT_TIMEOUT = 1.0

class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self,detail, info=""):
        self.detail = detail
        self.info   = info
    def __str__(self):
        if self.info:
            return "%s\n%s" % (self.detail,self.info)
        else:
            return str(self.detail)

class SerialCommunicationsMixIn(BaseCommunicationsMixIn):
    """Partial Interface for RS232 remotely contolled instruments"""
    def __init__(self,port,baudrate=9600, timeout=DEFAULT_TIMEOUT,EOL='\r\n',delay=DEFAULT_DELAY,**kwargs):
        #translate escaped string to ascii literals        
        if EOL == "\\n":
            EOL = '\n'
        elif EOL == '\\r':
            EOL = '\r'
        elif EOL == '\\r\\n':
            EOL = '\r\n'    
        self.EOL = EOL
        self.delay = delay
        try:
            self.ser = serial.Serial(port,baudrate=baudrate,timeout=timeout,**kwargs)
        except SerialException,details:
            raise Error(details,"failed to find device on port '%s'" % port)
        try:
            if not self.ser.isOpen():
                self.ser.open()
        except SerialException,details:
            raise Error(details,"failed to open serial connection")
    
    #Implementation of the Base Interface Helper methods
    def _send(self, command, append_EOL = True):
        if append_EOL:
            command += self.EOL
        self.ser.write(command) #add the end of line to the command
        self.ser.flushOutput()
        # a dirty hack to prevent hangups
        # maybe we should poll somehow?
        if self.delay:
            time.sleep(self.delay)
 
    def _read(self, strip_EOL = True):
        resp = self.ser.readline()
        if strip_EOL:
            resp = resp.rstrip(self.EOL)
        return resp
        
    def _read_char(self):
        c = self.ser.read(1)
        return c

    def _exchange(self,command):
        "Relay a command and get the response"
        #remove any possible crud in the buffer
        self.ser.flushInput()         
        self._send(command)     #send the command
        resp = self._read()     #read the response 
        return resp
