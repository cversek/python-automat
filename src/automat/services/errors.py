############################################################################### 
import sys
###############################################################################
#Module Constants
ERROR_INDENT      = 4
CONFIGURATION_ERROR_CODE = 2
DEVICE_ERROR_CODE        = 3
CRASHDUMP_FILENAME = '.crash_dump.txt~'
ERRORLOG_FILENAME  = '.error_log.txt~'

###############################################################################
class Error(Exception):
    def __init__(self, err_code, **kwargs):
        self.err_code = err_code
        Exception.__init__(self, **kwargs)

############################################################################### 
class ConfigurationError(Error):
    def __init__(self,
                 error_msg = 'configuration error',
                 key = None,
                 value = None,
                 exc = None
                ):
        Error.__init__(self, err_code = CONFIGURATION_ERROR_CODE)
        self.error_msg = error_msg
        self.key       = key
        self.value     = value
        self.exc       = exc
        
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
    def __init__(self, 
                 error_msg = 'device error',
                 handle = None,
                 device = None,
                 settings = None,
                 exc = None
                ):
        Error.__init__(self, err_code = DEVICE_ERROR_CODE)
        self.error_msg = error_msg
        self.handle    = handle
        self.device    = device
        self.settings  = settings
        self.exc       = exc
        
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

###############################################################################
class handleCrash(object):
    """Wraps a top-level script function in an error handling routine that 
       for a crash prints an informative message and dumps the exception 
       details to a file. Use as a decorator.
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            self.func(*args, **kwargs)
        except SystemExit as exc:
            sys.exit(0)
        except:
            error_type, exc, tb = sys.exc_info()
            msg = str(exc)
            print('*'*80)
            print("A fatal error has occured: %s" % error_type) 
            print(msg)
            print('*'*80)
            print("Writing crash info to '%s'." % CRASHDUMP_FILENAME) 
            crashdump_file = open(CRASHDUMP_FILENAME,'w')
            import traceback
            traceback.print_exc(file=crashdump_file)
            crashdump_file.close()
            print("Aborting program.")
            print("press 'enter' key to continue...")
            input()
            try:
                sys.exit(exc.err_code)
            except AttributeError:
                sys.exit(1)
                
##############################################################################
class ErrorLogger(object):
    def __init__(self):
        self.file = None
    def log(self, msg):
        if self.file is None:
            self.file = open(ERRORLOG_FILENAME, 'w')
        self.file.write(msg)
        self.file.flush()
