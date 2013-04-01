###############################################################################
import Queue, threading
from automat.core.threads.interruptible_thread import InterruptibleThread, AbortInterrupt
###############################################################################

###############################################################################
class Controller:
    """A threaded hardware interface that is to send events through to their 'event_queue' using the 'send_event' method"""
    #--------------------------------------------------------------------------
    # Initialization/Shutdown methods - called externally in various program phases 
    def __init__(self, 
                 devices             = None, #should be a dictionary containing only dependent device interfaces 
                 controllers         = None, #should be a ductionary containing only dependent controller interfaces
                 configuration       = None,
                 metadata            = None,
                 ):
        if devices is None:
            devices = {}
        self.devices = devices
        if controllers is None:
            controllers = {}
        self.controllers = controllers
        #settings relevant to the control process
        if configuration is None:
            configuration = {}
        self.configuration = configuration
        #miscellaneous information
        if metadata is None:
            metadata = {}
        self.metadata = metadata
        #self.configure(**kwargs) #apply remaining arguments to the configuration, overwriting defaults selectively
        
        #objects for thread execution and communication
        self.thread      = None
        self.event_queue = None
        self.stop_event  = None
        self.abort_event = None
        #maintain state of the controller  
        self._controller_mode_set = set(['object_initialized'])
        #holds information relevant to the controllers context
        self.context = {}  

    def thread_init(self,  
                    event_queue = None,  #to pass back controller events
                    stop_event  = None,  #to synchronize controlled exit
                    abort_event = None,  #to synchronize forced exit
                   ):
        self._require_controller_modes('object_initialized')
        if event_queue is None:
            event_queue = Queue.Queue()
        self.event_queue = event_queue
        if stop_event is None:
            stop_event = threading.Event()
        self.stop_event  = stop_event        
        if abort_event is None:
            abort_event = threading.Event()
        self.abort_event = abort_event        
        self.thread = InterruptibleThread(target = self.main,        #this ties the thread into the overloadable execution path 
                                          stop_event  = stop_event, 
                                          abort_event = abort_event
                                         )
        #cascade thread initializations into the controller dependencies
        for handle, subcontroller in self.controllers.items():
            subcontroller.thread_init(event_queue = event_queue, stop_event = stop_event, abort_event = abort_event)           
        self._controller_mode_set.discard('thread_shutdown')        
        self._controller_mode_set.add('thread_initialized')

    def thread_shutdown(self):
        try:    
            self.thread.shutdown()  #from InterruptibleThread
        except RuntimeError:  #when thread has not been run yet
            pass       
        #cascade device initializations into the controller dependencies
        for handle, subcontroller in self.controllers.items():
            subcontroller.thread_shutdown()  
        self._controller_mode_set.discard('running_as_thread')
        self._controller_mode_set.discard('running_as_blocking_call')
        self._controller_mode_set.discard('thread_initialized')
        self._controller_mode_set.add('thread_shutdown')   

    def thread_reset(self):
        self.thread_shutdown()
        self.thread_init(event_queue = self.event_queue, stop_event = self.stop_event, abort_event = self.abort_event)

    def thread_isAlive(self):
        return self.thread.isAlive()

    def set_devices(self,**kwargs):
        for key, val in kwargs.items():
            if not self.devices.has_key(key):  
                raise KeyError, "'%s' is not a valid subdevice name, must be one of %r" % (key, self.devices.keys())
            self.devices[key] = val

    def get_devices(self):
        return self.devices.copy()

    def set_controllers(self,**kwargs):
        for key, val in kwargs.items():
            if not self.controllers.has_key(key):  
                raise KeyError, "'%s' is not a valid subcontroller name, must be one of %r" % (key, self.controllers.keys())
            self.controllers[key] = val

    def get_controllers(self, name = None):
        if name is None:
            return self.controllers.copy()
        else:
            return self.controllers[name]
    
    def set_configuration(self, ignore_extra_fields = False, **kwargs):
        for key, val in kwargs.items():
            if not ignore_extra_fields and not self.configuration.has_key(key):  
                raise KeyError, "'%s' is not a valid configuration field, must be one of %r" % (key, self.configuration.keys())
            self.configuration[key] = val
    
    def get_configuration(self):
        return self.configuration.copy()

    def set_metadata(self, **kwargs):
        self.update_metadata(kwargs)

    def get_metadata(self):
        return self.metadata

    def update_metadata(self, new_metadata):
        self.metadata.update(new_metadata)

    def load_context(self, context):
        #holds information relevant to the controllers context
        self.context = context  
        
    def initialize_devices(self):
        "initialize all the devices, often can be overloaded in child class"
        for handle, device in self.devices.items():
            device.initialize()
        #cascade device initializations into the controller dependencies
        for handle, subcontroller in self.controllers.items():
            subcontroller.initialize_devices()
        self._controller_mode_set.discard('devices_shutdown')                  
        self._controller_mode_set.add('devices_initialized')
    
    def shutdown_devices(self):
        "shutdown all the devices, often can be overloaded in child class"
        for handle, device in self.devices.items():
            device.shutdown()
        #cascade device initializations into the controller dependencies
        for handle, subcontroller in self.controllers.items():
            subcontroller.shutdown_devices()    
        self._controller_mode_set.discard('devices_initialized')        
        self._controller_mode_set.add('devices_shutdown')
    
    def stop(self):
        self.stop_event.set()
    
    def abort(self):
        self.abort_event.set()
    
    def shutdown(self):
        self.shutdown_devices()
        self.thread_shutdown()

    def reset(self):
        self.shutdown()
        self.thread_reset()        
        self.initialize_devices()

    def sleep(self, time):
        self.abort_event.wait(time)        
        
    #--------------------------------------------------------------------------
    # Run methods
    def main(self):
        "the main functionality, must be overloaded in child class"
        raise NotImplementedError, "this abstract method must be overloaded in any child classes"
        
    def start(self):
        "run the 'main' method in a separate thread, this call should not block"
        if not 'devices_initialized' in self._controller_mode_set:
            self.initialize_devices()
        if not 'thread_initialized' in self._controller_mode_set:
            self.thread_init()
        self._require_controller_modes('thread_initialized','devices_initialized')
        self._controller_mode_set.add('running_as_thread')
        self.thread.start() #will run self.main as the target in a seperate thread
          
    def run(self):
        "run the 'main' method in non-threaded mode (will block)"
        self._require_controller_modes('thread_initialized','devices_initialized')
        self._controller_mode_set.add('running_as_blocking_call')
        self.thread.run()  #will run self.main as the target and block until completion
        
    def join(self):
        "join the thread started for the 'main' method"
        self._require_controller_modes('thread_initialized','devices_initialized')
        self.thread.join() #will run self.main as the target in a seperate thread_init
    #--------------------------------------------------------------------------
    # Helper Methods - call from within child class
    def _send_event(self, event_type, content):
        "use within child class to send events to the queue"
        self._require_controller_modes('thread_initialized')
        event = (event_type, content)  #events have standard 2-tuple form
        self.event_queue.put(event)
        
    def _thread_check_abort_event(self):
        """use to synchronize forced thread shutdown
           raises AbortInterupt if the abort_event has been set"""
        self._require_controller_modes(['running_as_thread','running_as_blocking_call'])
        self.thread.check_abort_event()
        
    def _thread_abort_breakout_point(self):
        """use to synchronize forced thread shutdown
           raises AbortInterupt if the abort_event has been set"""
        self._require_controller_modes(['running_as_thread','running_as_blocking_call'])
        self.thread.abort_breakout_point()
        
    def _thread_check_stop_event(self):
        """use to synchronize controlled thread shutdown"""
        self._require_controller_modes(['running_as_thread','running_as_blocking_call'])
        return self.thread.check_stop_event()
        
    def _require_controller_modes(self, *args):
        "require controller modes, modes grouped within list => OR"        
        for mode_group in args:
            if isinstance(mode_group,str): #a string, not other sequence
                if not mode_group in self._controller_mode_set:
                    msg = "control flow requires the mode '%s' which must be a member of the current mode set: %r" % (mode_group, self._controller_mode_set)
                    self._raise_error(msg)           
            else: #should be a non-string sequence
                mode_group = set(mode_group) #convert to do set operations
                intersection = self._controller_mode_set.intersection(mode_group)
                if not intersection:
                    msg = "control flow requires one of the modes %r to be a member of the current mode set: %r" % (mode_group, self._controller_mode_set)
                    self._raise_error(msg)
                    
    def _raise_error(self, msg = "",exc = None):
         raise ControllerError(controller = self, msg = msg, exc = exc)         
        
    #--------------------------------------------------------------------------
    # Python Builtin Methods
    def __repr__(self):
        #overloaded from Thread parent class
        s = "<Controller: %s.%s>" % (self.module_path, self.__class__)
        return s

#########################################################################################
class NullController(Controller):
    def main(self):
        pass

#########################################################################################
class ControllerError(Exception):
    def __init__(self, controller, msg, exc = None):
        self.controller = controller
        self.msg = msg
        self.exc = exc
        
    def __str__(self):
        error_msg = []
        error_msg.append("\n\tcontroller: %r" % self.controller)
        error_msg.append("\tmsg: %s" % self.msg)
        if not self.exc is None:
            error_msg.append("\texception: %s" % self.exc)
        return "\n".join(error_msg)
        
        
