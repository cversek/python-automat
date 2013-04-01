import threading

class FakeThreadMixIn:
    """A class that safely imitates a threading.Thread object without
       actually threading"""
    def start(self):
        self.run()
    def join(self):
        "Do not block in this non-threaded implementation"
        pass
    def isAlive(self):
        "always signal that the thread has completed"
        return False

class CallbackBase(object):
    """A base class for all callbacks"""
    def __init__(self):
        self.context = {}
    def load_context(self,context):
        self.context = context
    def run(self):
        self.main()
    def main(self):
        raise NotImplementedError    
        
class NonThreadingCallbackBase(CallbackBase,FakeThreadMixIn):
    """A base class for a simple non-threaded callback"""

class ThreadingCallbackBase(CallbackBase,threading.Thread):
    """A base class for a threaded callback"""
    def __init__(self):
        #provide stoping mechanism
        self._stop_event = threading.Event()
        CallbackBase.__init__(self)
        threading.Thread.__init__(self)
    def join(self,timeout=None):
        """
        Stop the thread and refresh it
        """
        self._stop_event.set()
        threading.Thread.join(self, timeout)
        self._refresh()    
    def stop(self):
        self._stop_event.set()
    def _sleep(self,seconds):
        "pause for the specified time unless the stop event is set"
        self._stop_event.wait(seconds)
    def _refresh(self):
        "refresh self allow repeated threading"
        self._stop_event.clear()
        threading.Thread.__init__(self) 

class DoNothingCallback(NonThreadingCallbackBase):
    def main(self):
        pass
