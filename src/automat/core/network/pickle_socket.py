import cPickle
import socket

class UnknownObject(object):
    pass

class PickleSocket:
    '''recieve and unpickle python objects over the network'''
    def __init__(self, sock=None, timeout=None, **kwargs):
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, **kwargs)
        if timeout is not None:
            sock.settimeout(timeout)
        self.sock = sock
    def bind(self,*args,**kwargs):
        self.sock.bind(*args,**kwargs)
    def listen(self,*args,**kwargs):
        self.sock.listen(*args,**kwargs)
    def accept(self, *args,**kwargs):
        return self.sock.accept(*args,**kwargs)
    def connect(self,*args,**kwargs):
        self.sock.connect(*args,**kwargs)
        #make objects for dumping/loading python objects 
        self.pickler   = cPickle.Pickler(self.sock.makefile('w'))
        self.unpickler = cPickle.Unpickler(self.sock.makefile('r'))
    def dump(self,obj):
        self.pickler.dump(obj)
    def load(self):
        try:
            return self.unpickler.load()
        except TypeError:
            return UnknownObject()

                
###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    PS = PickleSocket()
    PS.connect(('localhost',50007))
    while True:
        print PS.load()

