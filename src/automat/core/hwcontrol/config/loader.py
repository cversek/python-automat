###############################################################################
import os, platform
from   automat.core.filetools.directories        import fullpath, recur_mkdir

###############################################################################
DEPENDENT_DEVICE_HANDLE_TAG         = '_handle'
DEPENDENT_DEVICE_TAG                = '_device'

###############################################################################


#to cache loaded configurations
_configuration = None

def load(reload_ = False):
    """search for and load the configuration file on the path that is 
       appropriate for the running platform
    """
    global _configuration
    raise NotImplementedError #FIXME
#    #only load if cached or 'reload_' specified
#    if _configuration is None or reload_:
#        config_file_searchpaths = []
#        #add the platform appropriate path to the searchpath
#        config_file_searchpaths.append(pyEIS.pkg_info.platform['config_filepath'])
#        #FIXME - for right now, return the first config file encountered , should 
#        #        probably merge in settings specified in user directory paths
#        for path in config_file_searchpaths:
#            #get real path of links and user directory expansions       
#            path = fullpath(path)     
#            if os.path.isfile(path):
#                #create and cache the configuration
#                _configuration = Configuration(path)
#    #send back the cached configuration
#    return _configuration
