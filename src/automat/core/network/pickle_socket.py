import cPickle
import socket

class UnknownObject(object):
    pass

class PickleSocket:
    '''receive and unpickle python objects over the network'''
    def __init__(self, sock=None, timeout=None, **kwargs):
        if sock is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, **kwargs)
        if timeout is not None:
            sock.settimeout(timeout)
        self.sock = sock
        #make objects for dumping/loading python objects 
        self.wfile     = self.sock.makefile('w')
        self.rfile     = self.sock.makefile('r')
        self.pickler   = cPickle.Pickler(self.wfile)
        self.unpickler = cPickle.Unpickler(self.rfile)
    def bind(self,*args,**kwargs):
        self.sock.bind(*args,**kwargs)
    def get_port(self):
        hostaddr, port = self.sock.getsockname()
        return port
    def listen(self,*args,**kwargs):
        self.sock.listen(*args,**kwargs)
    def accept(self, *args,**kwargs):
        #get a new socket object to handle the connection
        conn, addr = self.sock.accept(*args,**kwargs)
        #wrap the connection with a new PickleSocket object
        conn = PickleSocket(sock=conn)
        return (conn, addr)
    def connect(self,*args,**kwargs):
        self.sock.connect(*args,**kwargs)
    def close(self):
        self.sock.close()
    def dump(self,obj):
        self.pickler.dump(obj)
        self.wfile.flush()
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

