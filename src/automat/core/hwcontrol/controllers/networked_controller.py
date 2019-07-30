###############################################################################
import time, datetime, traceback, socket
from threading import Thread
from queue import Queue
try:
    from collections import OrderedDict
except ImportError:
    from yes_o2ab.support.odict import OrderedDict
    
from automat.core.hwcontrol.controllers.controller import BaseController,Controller
from automat.core.network.pickle_socket import PickleSocket
###############################################################################
SOCKET_TIMEOUT  = 1.0   #timeout for accepting connections
MAX_CONNECTIONS = 5

###############################################################################
class ConnectionHandlerThread(Thread):
    def __init__(self, connection, address, message_queue):
        Thread.__init__(self)
        self.daemon = True  #set the thread daemonic property so it doesn't hang app
        self.connection = connection
        self.address    = address
        self.message_queue = message_queue
        
    def run(self):
        try:
            print("CONNECTION AT %s STARTED" % (self.address,))
            msg = self.connection.load()
            print("FROM %s RECEIVED: %r" % (self.address,msg))
            self.message_queue.put(msg)
        except socket.error:
            #connection dropped, end this thread
            print("CONNECTION AT %s DROPPED" % (self.address,))
            return
        self.close()    
            
    def close(self):
        self.connection.close()
        
###############################################################################
class ClientController(BaseController):
    def __init__(self, **kwargs):
        BaseController.__init__(self, **kwargs)
        server = self.controllers['server']
        port = server.configuration['port']
        self.set_configuration(port=port)
    #--------------------------------------------------------------------------
    # Python Builtin Methods
    def __repr__(self):
        #overloaded from  Controller parent class
        port = int(self.configuration.get('port', 0)) # default of 0 gets any available port at bind time
        s = "<ClientController: %s.%s, port = %s>" % (self.module_path, self.__class__, port)
        return s
        
    def __del__(self):
        try:
            pass
        except AttributeError:  #ignore already collected garbage
            pass
    
###############################################################################
class NetworkedController(Controller):
    """A threaded hardware interface that is to send events through to their 'event_queue' using the 'send_event' method"""
    #--------------------------------------------------------------------------
    # Initialization/Shutdown methods - called externally in various program phases 
    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        self._pickle_socket = None
        self.handler_threads = []
        self.message_queue = Queue()
        
    def initialize(self, **kwargs):
        Controller.initialize(self,**kwargs)
        self.init_socket()
        
    def init_socket(self):
        #create a socket which accepts python objects and bind to port
        port = int(self.configuration.get('port', 0)) # default of 0 gets any available port at bind time
        self._pickle_socket = PickleSocket(timeout=SOCKET_TIMEOUT)
        self._pickle_socket.bind(("", port))     
        self._pickle_socket.listen(MAX_CONNECTIONS) #accept a limited number of simultaneous connections
        
    def shutdown(self):
        Controller.shutdown(self)
        for handler_thread in self.handler_threads:
            handler_thread.close()
            handler_thread.join()
        self._pickle_socket.close()
        
    def accept_connection(self):
        #accept a connection
        try:         
            connection, address = self._pickle_socket.accept()
            #launch a new thread for each connection
            handler_thread = HandlerThread(connection,address,message_queue = self.message_queue)
            handler_thread.start()
            self.handler_threads.append(handler_thread)  #keep track of running threads
            return True
        except socket.timeout: #continue with next iteration
            return False

    def reset(self):
        Controller.reset(self)
        self.init_socket()        
        
    #--------------------------------------------------------------------------
    # Python Builtin Methods
    def __repr__(self):
        #overloaded from  Controller parent class
        port = int(self.configuration.get('port', 0)) # default of 0 gets any available port at bind time
        s = "<NetworkedController: %s.%s, port = %s>" % (self.module_path, self.__class__, port)
        return s
        
    def __del__(self):
        try:
            self.stop()
            self.shutdown()
        except AttributeError:  #ignore already collected garbage
            pass
        
        
