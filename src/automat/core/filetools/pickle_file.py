import os 
import bz2, gzip, zipfile
#use the faster library if available
try: 
    import cPickle as pickle 
except ImportError:
    import pickle

#extension lookup for various compressed file objects
FILE_TYPES = {
    'bz2': bz2.BZ2File,
    'gz' : gzip.GzipFile,
    'zip': zipfile.ZipFile,
    'pkl': open,
}

###############################################################################
class PickleFile(object):
    """A class which provides a file-like iterator for an 
       (optionally compressed) file of pickled python objects.
    """
    def __init__(self,filename,mode='r'):
        self.filename = filename
        #guess the file type from the extension
        base, ext = os.path.splitext(filename)
        file_type = ext.lstrip('.')
        try:    
            stream = FILE_TYPES[file_type](filename,mode)
        except KeyError:
            raise IOError, "unkown extension '%s'" % file_type
        self.unpickler = pickle.Unpickler(stream)
    def __iter__(self):
        #make object iterable
        return self
    def next(self):
        try:
            return self.unpickler.load()
        except EOFError:
            #stop at the end of the file
            raise StopIteration
    def read(self):
        "get a list of all the objects at once"
        return [obj for obj in self]

###############################################################################
# TEST CODE
###############################################################################       
if __name__ == "__main__":
    import sys
    PF = PickleFile(sys.argv[1])
    for event in PF:
        print event
