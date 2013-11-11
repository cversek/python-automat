###############################################################################
#Standard Python
import os, sys, threading, time
from warnings import warn
try:
    from collections import OrderedDict
except ImportError:
    from automat.substitutes.ordered_dict import OrderedDict
#Automat framework provided
from automat.core.hwcontrol.config.configuration import Configuration
#from automat.services.configurator import ConfiguratorService
from automat.services.errors import ConfigurationError, DeviceError
###############################################################################
#Module Constants

###############################################################################
#Helper Functions
def stream_print(text, 
                 stream = sys.stdout, 
                 eol = '\n', 
                 prefix = None
                ):
        if prefix:
            stream.write(prefix)
        stream.write(text)
        if eol:
            stream.write(eol)
        stream.flush()
        
################################################################################
class ApplicationBase(object):
    def __init__(self,
                 ignore_device_errors = False,
                 output_stream   = sys.stdout,
                 error_stream    = sys.stderr,
                 textbox_printer = lambda text: None,
                 used_controllers = [],
                ):
        self._ignore_device_errors = ignore_device_errors
        self._output_stream        = output_stream
        self._error_stream         = error_stream
        self._textbox_printer      = textbox_printer
        self._config      = None
        self._log_stream  = None
        self._devices     = OrderedDict()
        self._controllers = OrderedDict()
        self._metadata    = OrderedDict()
        self._used_controllers = used_controllers
        #create an event for synchronize forced shutdown
        self._abort_event = threading.Event()

    def load(self, config_filepath):
        #load the configuration file
        self._config = Configuration(config_filepath)
        #set up the log file
        try:
            log_dir          = self._config['paths']['log_dir']
            log_filepath     = os.sep.join((log_dir,'log.txt'))
            self._log_stream = open(log_filepath,'a')
        except KeyError: #ignore log file absence
            pass

    def initialize(self, used_controllers = None):
        if used_controllers is None:
            used_controllers = []
        for name in used_controllers:
            #self.print_comment("\tLoading and initializing controller '%s'..." % name)
            controller = self._load_controller(name)
            controller.initialize()
            #self.print_comment("\tcompleted")
 
    def setup_textbox_printer(self, textbox_printer):
        self._textbox_printer = textbox_printer

    def print_comment(self, text, eol = '\n', comment_prefix = '#'):
        buff = ""
        if eol:
            lines = text.split(eol)
            buff = eol.join([ comment_prefix + line for line in lines])
        else:
            buff = comment_prefix + text
        stream_print(buff, stream = self._output_stream, eol = eol)
        #also print to the textbox if available
        self._textbox_printer(buff)
    
    def _print_log_msg(self,msg):
        stream_print(msg, stream = self._log_stream)
        self.print_comment("Logged: " + msg)        
              
    def _load_device(self, handle):
        self.print_comment("Loading device '%s'..." % handle)
        try:
            device = self._config.load_device(handle)
            self._devices[handle] = device   #cache the device
            self.print_comment("    success.")
            return device
        except Exception, exc:
            settings = self._config['devices'].get(handle, None)
            if settings is None:
                error_msg = "missing settings for device in config file '%s'" % self._config['config_filepath']
            else:
                error_msg = "bad configuration"
            exc = DeviceError(error_msg = error_msg, 
                              handle    = handle, 
                              settings  = settings, 
                              exc       = exc)
            if not self._ignore_device_errors:
                raise exc
            else:
                warn("ignoring following error:\n---\n%s\n---" % exc, RuntimeWarning)
                
    def _load_controller(self, name):
        #self.print_comment("Loading controller '%s'..." % name)
        try:
            try:
                controller = self._config.load_controller(name)
                self._controllers[name] = controller
                #self.print_comment("    success.")
                return controller
            except Exception, exc:
                self.print_comment("    failed loading controller '%s' with exception: %s" % (name, exc))
                if not self._ignore_device_errors:
                    raise exc
                else:
                    warn("ignoring following error:\n---\n%s\n---" % exc, RuntimeWarning)
        except KeyError:
            pass
            
    def _abort_all_controllers(self):
        try:
            controllers_dict = self._config['controllers']
            for name in controllers_dict.keys():
                controller = self._load_controller(name)
                controller.abort()
        except KeyError:
            pass

################################################################################


class ShellApplication(ApplicationBase):
    def __init__(self, **kwargs):
        commands = kwargs.pop('commands',None)
        if commands is None:
            commands = {}
        self._commands = commands
        self._user_ns  = {}
        self._ipshell = None
        ApplicationBase.__init__(self, **kwargs)
        
    def load(self, config_filepath):
        ApplicationBase.load(self, config_filepath)
        self._load_all_devices()
        self._load_all_controllers()
        
    def _load_all_devices(self):
        for handle in self._config['devices'].keys():
            self._load_device(handle)

    def _load_all_controllers(self):
        try:
            controllers_dict = self._config['controllers']
            for name in controllers_dict.keys():
                self._load_controller(name)
        except KeyError:
            pass

    def start_shell(self,
                    msg = "", 
                    extra_modules = ['time',],
                    pylab_mode = False,
                   ):
        status_msg = []
        status_msg.append(msg)
        
        #load convenient modules if they are installed
        for modname in extra_modules:
            try:
                mod = __import__(modname)
                self._user_ns[modname] = mod
            except ImportError, exc:
                warn("ignoring following error:\n---\n%s\n---" % exc, RuntimeWarning)

        #find the available devices
        items = self._config._device_cache.items()
        items.sort()
        if items:
            status_msg.append("Available devices:")
            for name, device in items:
                status_msg.append("\t%s" % name)
                #add device name to the user name space
                self._user_ns[name] = device
        
        #find the available controllers
        items = self._config._controller_cache.items()
        items.sort()
        if items:
            status_msg.append("Available controllers:")
            for name, controller in items:
                status_msg.append("\t%s" % name)
                #add controller name to the user name space
                self._user_ns[name] = controller
        
        #add all the special commands to the namespace
        self._user_ns.update(self._commands)

        #complete the status message
        status_msg.append('')
        status_msg.append("-- Hit Ctrl-D to exit. --")
        status_msg = '\n'.join(status_msg) 
        #start the shell
#        try:
#            from IPython.frontend.terminal.ipapp import TerminalIPythonApp
#            app = TerminalIPythonApp.instance()
#            app.initialize(argv = argv, user_ns = self._user_ns)
#            app.start()
#        except ImportError: #FIXME support older versions
        try:
            #first try new style >= 0.12 interactive shell
            from IPython.frontend.terminal.embed import InteractiveShellEmbed
            #FIXME change made for ipython >= 0.13
            self._ipshell = InteractiveShellEmbed(
                                                  user_ns = self._user_ns,
                                                  banner1 = status_msg,    #FIXME change made for ipython >= 0.13
                                                 )
            if pylab_mode is True:
                self._ipshell.enable_pylab()
            self._ipshell.mainloop()
        except ImportError:
            #substitue old-style interactive shell
            from IPython.Shell import IPShellMatplotlib as IPYTHON_SHELL
            self._ipshell = IPYTHON_SHELL(user_ns = self._user_ns)
            self._ipshell.mainloop(banner = status_msg)
