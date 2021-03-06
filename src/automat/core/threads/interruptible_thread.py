###############################################################################
from threading import Thread, Event
import signal
###############################################################################

class AbortInterrupt(Exception):
    "Interrupts an InterruptibleThread"
    pass

#def IgnoreKeyboardInterrupt():
#    """
#    Sets the response to a SIGINT (keyboard interrupt) to ignore.
#    """
#    return signal.signal(signal.SIGINT,signal.SIG_IGN)

#def NoticeKeyboardInterrupt():
#    """
#    Sets the response to a SIGINT (keyboard interrupt) to the
#    default (raise KeyboardInterrupt).
#    """
#    return signal.signal(signal.SIGINT, signal.default_int_handler)

###############################################################################
class InterruptibleThread(Thread):
    """An extension of the Thread class to provide interruptible threading support"""
    def __init__(self,
                 stop_event  = None,   #to synchronize controlled exit 
                 abort_event = None,   #to synchronize forced exit
                 **kwargs              #additional arguments to pass to Thread.__init__
                ):
        #configure the thread
        Thread.__init__(self, **kwargs)
        #enable controlled exit
        if stop_event is None:
            stop_event  = Event()
        self.stop_event = stop_event        
        #enable forced exit
        if abort_event is None:
            abort_event  = Event()
        self.abort_event = abort_event
    
    def join(self,timeout=None):
        """ Joins up control flow
        """
        Thread.join(self, timeout)

    def sleep(self, time):
        self.abort_event.wait(time)
        
    def abort(self):
        """ signals the thread to abort
        """
        self.abort_event.set()

    def shutdown(self):
        self.stop_event.set()
        self.join()
    
    def abort_breakout_point(self):
        if self.check_abort_event():
            raise AbortInterrupt("user requested abort")    
    
    def check_abort_event(self):
        "use in subclasses to mark forced exit points in the thread"
        return self.abort_event.isSet()
            
    def check_stop_event(self):
        "use in subclasses to mark controlled exit points in the thread"
        return self.stop_event.isSet()
