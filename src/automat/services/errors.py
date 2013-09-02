############################################################################### 
import sys
###############################################################################
#Module Constants
ERROR_INDENT      = 4
DEVICE_ERROR_CODE = 2    

###############################################################################
class Error(Exception):
    def __init__(self, err_code = 1):
        self.err_code = err_code


############################################################################### 
class ConfigurationError(Error):
    def __init__(self, error_msg = 'configuration error', key = None, value = None, exc = None):
        Error.__init__(self, err_code = DEVICE_ERROR_CODE)
        self.error_msg   = error_msg
        self.key   = key
        self.value = value        
        self.exc         = exc
        
    def __str__(self):
        msg = ['Configuration Error:']
        indent = " "*ERROR_INDENT
        msg.append("%serror message: %s" % (indent,self.error_msg) )
        if not self.key is None:
            msg.append("%skey: '%s'" % (indent,self.key) )
        if not self.value is None:
            msg.append("%svalue: %s" % (indent, self.value) )
        if not self.exc is None:
            msg.append("%sexception: %s" % (indent,type(self.exc)) )
            exc_msg = str(self.exc)
            if exc_msg:
                msg.append("%sexception message: %s" % (indent,exc_msg) )
        msg = "\n".join(msg) 
        return msg        
############################################################################### 
class DeviceError(Error):
    def __init__(self, error_msg = 'device error', handle = None, device = None, settings = None, exc = None):
        Error.__init__(self, err_code = DEVICE_ERROR_CODE)
        self.error_msg   = error_msg
        self.handle      = handle
        self.device      = device
        self.settings    = settings
        self.exc         = exc
        
    def __str__(self):
        msg = ['Device Error:']
        indent = " "*ERROR_INDENT
        msg.append("%serror message: %s" % (indent,self.error_msg) )
        if not self.handle is None:
            msg.append("%sdevice handle: '%s'" % (indent,self.handle) )
        if not self.device is None:
            msg.append("%sdevice: %s" % (indent, self.device) )
        if not self.settings is None:
            msg.append("%sdevice settings: %s" % (indent,self.settings) )
        if not self.exc is None:
            msg.append("%sexception: %s" % (indent,type(self.exc)) )
            exc_msg = str(self.exc)
            if exc_msg:
                msg.append("%sexception message: %s" % (indent,exc_msg) )
        msg = "\n".join(msg) 
        return msg
