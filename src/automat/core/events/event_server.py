import socket, sys, time, datetime, cPickle, Queue, thread
from automat.core.threads.interruptible_thread import InterruptibleThread

###############################################################################
DEFAULT_EVENT_FILE = "events.pkl" #for reporting events from event queue
DEFAULT_LOG_FILE   = "server.log" #for reporting server related events
SOCKET_TIMEOUT     = 1.0          #timeout for accepting connections

def now():
    return datetime.datetime.now()

def reserve_port(port = None):
    "Attempt to reserve requested port. If successful send back socket object."  
    if port is None:
        port = 0 #gets any available port    
    try:
        sock_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_obj.bind(("",port))
        return sock_obj    
    except socket.error:
        return None
        
        
###############################################################################
from event_caching import EventCachingProcess

class EventServer(InterruptibleThread):
    def __init__(self,
                 event_queue,
                 port                  = None,
                 sock_obj              = None,
                 log_func              = None,
                 event_caching_process = None,
                 event_file            = None,
                ):
        #set up the thread
        InterruptibleThread.__init__(self)
        self.event_queue  = event_queue
        self.event_file   = event_file
        if log_func is None:
            def log_func(text):
                print text
        self.log_func = log_func #logging function
        #create a socket which accepts python objects and bind to port
        if sock_obj is None:
            sock_obj = reserve_port(port)
        elif port:
            sock_obj.bind(("",port))       
        sock_obj.listen(5) #accept 5 simultaneous connections
        sock_obj.settimeout(SOCKET_TIMEOUT) #set timeout to not block on accept
        self.sock_obj = sock_obj        
        #configure event udpating thread
        if event_caching_process is None:
            event_caching_process = EventCachingProcess(event_queue = event_queue, event_file = event_file)
        self.event_caching_process = event_caching_process
    
    def shutdown(self, close_sock_obj = True):
        InterruptibleThread.shutdown(self)
        if close_sock_obj:
            self.sock_obj.close()    
        self.log("server shutdown")
             
    def run(self):
        #cache some references
        event_queue   = self.event_queue
        stop_event    = self.stop_event 
        sock_obj      = self.sock_obj
        log           = self.log
        handle_client = self.handle_client
       
        #manage incoming connections
        log("server started")
        while True:
            #check to see if the thread has been requested to stop
            if stop_event.isSet():
                return #exit the thread
            #accept a connectopm
            try:         
                connection, address = sock_obj.accept()
                log("server connected by client at %s" % (address,))
                thread.start_new(handle_client, (connection,address))
            except socket.timeout: #continue with next iteration
                pass      
        
    def handle_client(self,connection,address):
        stop_event    = self.stop_event 
        #get a cursor to shared memory event history
        event_cache_cursor = self.event_caching_process.get_cursor() 
        #send all the previous events
        connection.send(cPickle.dumps(('PAST_EVENTS',event_cache_cursor.next())))
        #keep track of new events arriving, and send them over the socket
        try:
            for events in event_cache_cursor:    
                if events:
                    for event in events:
                        connection.send(cPickle.dumps(event))
                #pause for a bit to conserve processor resources
                stop_event.wait(0.1) 
        except socket.error:
            #connection dropped, end this thread
            self.log("client at %s disconnected" % (address,))
            return
            
    def log(self,msg):
        msg = "%s: %s" % (now(),msg)
        self.log_func(msg)
                       
###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    myHost = ""
    myPort = 50007
    EVENT_QUEUE = Queue.Queue() #to passback events
    ERROR_QUEUE = Queue.Queue() #to collect errors
    EVENT_QUEUE.put("one")
    EVENT_QUEUE.put("two")
    server = EventServer(event_queue = EVENT_QUEUE,
                       port = myPort,
                      )
    def add_event():
        while True:
            EVENT_QUEUE.put(datetime.datetime.now())
            time.sleep(1.0)    
    thread.start_new(add_event, ())
    #must fix this test code
    #try:
    #    server.main_loop()
    #finally:
    #    server.shutdown()
