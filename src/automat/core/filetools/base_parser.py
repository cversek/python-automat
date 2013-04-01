class BaseParser(object):
    def __init__(self, istream = None, debug = False):
        self.istream = istream
        self.debug = debug
        self.obj_num = 0
        self._curr_obj = None

    def __iter__(self): #make object iterable
        "iteration interface"
        if self.istream is None:
            raise Error(IOError("%s must be initialized with 'istream' to run in iterator mode" % self.__class__))
        return self

    def process_all(self):
        return list(self)
    
    def next(self):
        istream = self.istream 
        feed    = self.feed
        while True:
            in_obj  = istream.next()
            out_obj = feed(in_obj)
            if not out_obj is None:
                #return any objects created during parsing
                return out_obj
                
    def feed(self, in_obj):
        self._curr_in_obj = in_obj #cache in class for introspective debugging
        self.obj_num += 1
        try:
            out_obj = self.process(in_obj)
            return out_obj
        except: #handle parser error
            if not self.debug: #reraise the error
                raise
            else:
                #enter debugging mode
                import sys, traceback
                obj_num    = self.obj_num
                in_obj     = self._curr_in_obj
                #print the traceback
                traceback.print_exc(file=sys.stdout)
                #open the debugging console
                print "decoder error caught, entering debugging mode..."
                print "*"*80
                print "obj_num: %d" % self.obj_num
                print "in_obj: %s"  % in_obj
                print "*"*80
                from IPython.Shell import IPShellEmbed
                ipshell = IPShellEmbed([])
                ipshell('(Hit Ctrl-D to exit)')
                sys.exit()

    def process(self, in_obj):
        raise NotImplementedError
