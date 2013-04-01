import socket, sys, time, datetime, Queue, cPickle
from automat.core.threads.interruptible_thread import InterruptibleThread
WAIT_DELAY = 0.100 #100 ms
###############################################################################
class EventCacheCursor(object):
    def __init__(self,event_cache):
        self.event_cache = event_cache
        self.cursor_index = 0
    def __iter__(self):
        return self
    def next(self):
        #get all new events
        events = self.event_cache[self.cursor_index:]
        #advance the cursor
        self.cursor_index = len(self.event_cache)
        return events
    
###############################################################################
class EventCachingProcess(InterruptibleThread):
    def __init__(self, event_queue, event_file = None):
        InterruptibleThread.__init__(self)
        self.setDaemon(True) #will end automatically on exit
        self.event_file     = event_file
        self.event_queue    = event_queue
        #create in memory structure for storing events
        self.event_cache  = [] 
    
    def event_callback(self, event):
        "overload this function to process events as they come in"
        if not self.event_file is None:
            cPickle.dump(event, self.event_file)
            self.event_file.flush()
        return event   
    
    def clear(self):
        "clear the event cache"
        self.event_cache = []
             
    def run(self):
        event_queue    = self.event_queue
        event_cache    = self.event_cache
        event_callback = self.event_callback
        stop_event     = self.stop_event
        while True:
            try:
                #see if an event has arrived
                #throws Queue.Empty if no object in the Queue
                event = event_queue.get(block=False) 
                #process the event with the callback 
                try:
                    event = event_callback(event)
                    #update the event_cache list
                    event_cache.append(event)
                except Exception, exc:
                    import traceback
                    #event callback failure wrap in error event
                    error_type, exc, tb = sys.exc_info()
                    content = {}
                    content['event'] = event
                    content['error_type'] = error_type
                    content['error_msg']  = msg = str(exc)
                    content['traceback']  = traceback.format_exc()                    
                    err_event = ('EVENT_CACHING_ERROR', content)
                    event_callback(err_event)
                    event_cache.append(err_event)  
            except Queue.Empty:
                if stop_event.isSet():
                    return
                #wait for items on Queue to arrive
                stop_event.wait(WAIT_DELAY) 

    def get_cursor(self):
        return EventCacheCursor(self.event_cache)
        

###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    pass
