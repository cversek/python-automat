class EventParser(object):
    def __init__(self, event_stream = None):
        self.event_stream = event_stream
    
    def __iter__(self):
        if self.event_stream is None:
            raise IOError("EventParser must be initialized with a stream to run in iterator mode")
        return self
    
    def parse_all(self):
        return [val for val in self]
    
    def next(self):
        event_stream = self.event_stream 
        feed = self.feed
        while True:
            event = event_stream.next()
            obj = feed(event)
            if not obj is None:
                #return any objects created during parsing
                return obj
                         
    def feed(self,event):
        event_type, content = event
        #content['timestamp'] = content['time']
        handler_name = "handle_%s" % event_type       #construct the event handler name
        handler = None        
        try:                    #retrieve and call the handler
            handler = self.__getattribute__(handler_name)
        except AttributeError:  #handler not found for event
            return None
        obj = handler(content)
        #return any objects created during parsing
        return obj

###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    from automat.core.filetools.pickle_file import PickleFile
    import sys
    PF = PickleFile(sys.argv[1])
    EP = EventParser(PF)
    EP.parse_all()
