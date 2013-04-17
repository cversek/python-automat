###############################################################################
import os, copy, platform
try:
    #in python >= 2.7 this is in standard library
    from   collections import OrderedDict
except ImportError:
    #for older python version, use drop in substitue
    from automat.substitutes.ordered_dict import OrderedDict

from   configobj import ConfigObj
from   automat.core.filetools.directories        import fullpath, recur_mkdir
import automat.core.hwcontrol.devices.loader     as device_loader
import automat.core.hwcontrol.controllers.loader as controller_loader
from   automat.core.threads.mutex import Mutex
###############################################################################
DEFAULT_MUTEX_TIMEOUT = 10 #seconds

###############################################################################
class Configuration(ConfigObj):
    """ A dictionary-like ConfigObj subclass that groups runtime parameters 
        with user specified settings from configuration files.
    """
    def __init__(self, config_filepath):
        #load all the configuration file
        ConfigObj.__init__(self, config_filepath)
        self['config_filepath']  = config_filepath  
        #get information from the system at run time
        self._load_system_params()
        #setup paths
        self._setup_paths()
        #convert values
        self._convert_values()
        #for storing loaded device drivers
        self._device_cache = OrderedDict()
        #for storing mutexes on device resources
        self._device_mutexes = {}
        #for storing loaded controller interfaces
        self._controller_cache = OrderedDict()

    def _load_system_params(self):
        "get information from the system at run-time"
        self['platform'] = platform.platform()
        try:
            self['user'] = os.getlogin()           #works on Unix compatible systems
        except AttributeError:
            self['user'] = os.environ['USERNAME']  #maybe works on Windows as well
   
    def _setup_paths(self):
        "configure the paths and create, if necessary"
        try:
            paths_dict = self['paths']
            for pathvar, path in paths_dict.items():
                #regularize the path
                path = fullpath(path)            
                if not os.path.isdir(path):
                    #create the path if it doesn't exist
                    recur_mkdir(path)
                #overwrite with expanded path
                self['paths'][pathvar] = path
        except KeyError:
            pass
        

    def _convert_values(self):
        "convert the object type of some values in the configuration"        
        #overload in child classes        
        pass    
             
    def load_device(self, handle):
        "load a device and it's dependencies (recursively)"
        #avoid loading the device again if it is in the cache
        if self._device_cache.has_key(handle):
            mutex = self._device_mutexes.get(handle)
            if not mutex is None:
                mutex.acquire()
            return self._device_cache[handle]
        settings = self._load_device_settings(handle)
        #implement a mutex if configured
        mutex = None
        mutex_settings = settings.pop('mutex', None)
        if not mutex_settings is None:
            name    = mutex_settings.get('name',handle) #default to handle if not specified
            timeout = mutex_settings.get('timeout', DEFAULT_MUTEX_TIMEOUT)
            mutex   = Mutex(name=name, default_timeout=timeout)
            mutex.acquire()
            self._device_mutexes[handle] = mutex
        device = device_loader.load_device(**settings)
        device._mutex = mutex #attach the mutex
        self._device_cache[handle] = device
        return device

    def load_device_module(self, handle):
        module          = settings.get('module', None)
        mod = device_loader.load_device_module(module)
        return mod

    def _load_device_settings(self, handle):
        #load the device and cache it
        try:
            devices = self['devices']
        except KeyError:
            config_filepath = self['config_filepath']
            raise ValueError, "no 'devices' section speficied in the config_file: '%s'" % config_filepath
        try:
            #get the loaded settings if they exist
            settings = devices[handle].dict()  #deepcopy into a dict object, so weird things don't happen
        except KeyError:
            config_filepath = self['config_filepath']
            raise ValueError, "the device with handle '%s' has not been specified in the 'devices' section of the config_file: '%s'" % (handle, config_filepath)
        #scan the settings for device dependencies and load recursively
        devices = settings.get('devices',{})
        for left_handle,right_handle in devices.items():
            dev = self.load_device(right_handle)
            devices[left_handle] = dev
        settings['devices'] = devices            
        return settings
        

    def load_controller(self, handle, interface_mode = None):
        #avoid loading the controller again if it is in the cache
        if self._controller_cache.has_key(handle): 
            #print "loading controller '%s' from cache" % handle        
            return self._controller_cache[handle]
        #print "loading controller '%s' from settings" % handle        
        settings = self._load_controller_settings(handle)
        module           = settings.get('module', None)
        devices          = settings.get('devices',None)
        subcontrollers   = settings.get('controllers',None)
        configuration    = settings.get('configuration',None)
        
        controller = controller_loader.load_controller(interface_mode = interface_mode,
                                                       module         = module,
                                                       devices        = devices, 
                                                       controllers    = subcontrollers, 
                                                       configuration  = configuration,
                                                      )
        
        #cache the controller        
        self._controller_cache[handle] = controller
        return controller
            
    def _load_controller_module(self, settings):
        "load the controller module"
        module           = settings.get('module', None)
        mod = controller_loader.load_controller_module(module)
        return mod

    def _load_controller_settings(self, handle):
        #load the device and cache it
        try:
            controllers_section = self['controllers']
        except KeyError:
            config_filepath = self['config_filepath']
            raise ValueError, "no 'controllers' section speficied in the config_file: '%s'" % config_filepath
        try:
            #get the loaded settings if they exist
            settings = controllers_section[handle].dict() #get a deepcopy dict object so weird things don't happen
        except KeyError:
            config_filepath = self['config_filepath']
            raise ValueError, "the controller with handle '%s' has not been specified in the 'controllers' section of the config_file: '%s'" % (handle, config_filepath)    
        #scan the settings for device dependencies and load recursively
        devices = settings.get('devices',None)
        if not devices is None:
            for left_handle,right_handle in devices.items():
                dev = self.load_device(right_handle)
                devices[left_handle] = dev
        #scan for other controller dependencies and load recursively
        subcontrollers = settings.get('controllers',None)
        if not subcontrollers is None:
            for left_handle,right_handle in subcontrollers.items():
                con = self.load_controller(right_handle)
                subcontrollers[left_handle] = con                 
        return settings
    
    
