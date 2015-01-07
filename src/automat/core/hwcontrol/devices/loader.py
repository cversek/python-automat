from automat.core.filetools.modules import chain_import

def load_device_module(module):
    return chain_import(module)
    
def load_device(module,
                **kwargs
               ):
    mod = load_device_module(module)
#    #FIXME - this is a hack to get the dependency devices in the kwargs dict, should be explicit
#    devices = kwargs.pop('devices', None)
#    if not devices is None:
#        kwargs.update(devices)
    try:
        dev = mod.get_interface(**kwargs)
    except:
        print "Error in module '%s'" % mod  #add some tracing info to the error
        raise
    return dev

if __name__ == "__main__":
    pass
