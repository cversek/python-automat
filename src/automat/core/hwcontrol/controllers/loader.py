from automat.core.filetools.modules import chain_import


#name tags for defaults loaded directly from the controller module
DEFAULT_CONFIGURATION_NAME   = 'DEFAULT_CONFIGURATION' 
DEFAULT_DEVICES_NAME         = 'DEFAULT_DEVICES'       
DEFAULT_CONTROLLERS_NAME     = 'DEFAULT_CONTROLLERS'   
DEFAULT_METADATA_NAME        = 'DEFAULT_METADATA'

def load_controller_module(module):
    return chain_import(module)                    
    
def load_controller(module,
                    devices             = None,   #dependent devices by handle, <automat.core.hwcontrol.devices.Device> object
                    controllers         = None,   #dependent subcontrollers by handle, <automat.core.hwcontrol.controllers.Controller> object
                    configuration       = None,   #controller configuration settings
                    metadata            = None,   #miscellaneous information                     
                    interface_mode      = None,
                    **kwargs
                    ):
    mod = load_controller_module(module)
                                
    #load the default devices if specified in the controller module and merge in the devices from the config file  
    try:
        default_devices = mod.__getattribute__(DEFAULT_DEVICES_NAME).copy()  #copy to prevent mutability weirdness
        if not devices is None:
            default_devices.update(devices)
        devices = default_devices       
    except AttributeError:
        pass
    #load the default subcontrollers if specified in the controller module and merge in the subcontrollers from the config file  
    try:
        default_controllers = mod.__getattribute__(DEFAULT_CONTROLLERS_NAME).copy()  #copy to prevent mutability weirdness
        if not controllers is None:
            default_controllers.update(controllers)
        controllers = default_controllers       
    except AttributeError:
        pass
    #load the default configuration if specified in the controller module and merge in the configurations from the config file  
    try:
        default_configuration = mod.__getattribute__(DEFAULT_CONFIGURATION_NAME).copy()  #copy to prevent mutability weirdness
        if not configuration is None:        
            default_configuration.update(configuration)
        configuration = default_configuration       
    except AttributeError:
        pass
    #load the default metadata if specified in the controller module and merge in the metadata from the config file  
    try:
        default_metadata = mod.__getattribute__(DEFAULT_METADATA_NAME).copy()  #copy to prevent mutability weirdness
        if not metadata is None:
            default_metadata.update(metadata)
        metadata = default_metadata
    except AttributeError:
        pass
      
    try:        
        if interface_mode is None:
            interface_mode = 'threaded'
        
        controller = None
        try: #try to load through the 'get_interface' function first
            controller = mod.get_interface(interface_mode = interface_mode,
                                           devices        = devices,
                                           controllers    = controllers, 
                                           configuration  = configuration,
                                           metadata       = metadata,
                                          )
        except AttributeError:
            controller = mod.Interface(devices       = devices,
                                       controllers   = controllers, 
                                       configuration = configuration,
                                       metadata      = metadata,
                                      )
        controller.module_path = module    #cache this dynamic information
    except:
        print "Error in module '%s'" % mod  #add some tracing info to the error
        raise
    return controller

if __name__ == "__main__":
    temp = load_device('potentiostat','solartron','SI1287')

