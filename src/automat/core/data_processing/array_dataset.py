###############################################################################
from collections import OrderedDict 
import numpy as np

from datasets import DataSet
###############################################################################
class ArrayDataSet(DataSet):
    """A class which indexes sequences by names
    """
    def __init__(self, fields=None, names=None, metadata=None):
        #create default names if not specified
        if fields is None and names is None:
            raise ValueError, "must specify at least fields or names"
        elif names is None:
            names = ["f%d" % i for i in xrange(len(fields))]
        elif fields is None:
            empty = []
            fields = np.array([empty[:] for x in xrange(len(names))]).transpose()
        else:
            assert len(names) == len(fields)
        #ensure that fields are an array
        self._fields = np.array(fields).transpose()
        #cache the names to mantain ordering
        self._names = names
        #build the underlying data storage structure
        self._build_data_dict()
        #cache te metadata
        if not metadata:
            metadata = {}
        self._metadata = metadata
        
    def _build_data_dict(self):
        self._data = OrderedDict()
        for i, name in enumerate(self._names):
            self._data[name] = self._fields[:,i]
        
    def get_records(self):
        "obtain the data as records, warning: the empty cells are filled out with None objects"
        return list(self._fields)
    
    def append_record(self,record):
        assert len(record) == len(self._names), "the record must contain as many entries as there are fields"
        self._fields = np.vstack((self._fields,record))
        self._build_data_dict()
            
    def extend_records(self, records):
        records = np.array(records)
        assert records.shape[1] == self._fields.shape[1]
        self._fields = np.vstack((self._fields,records))
        self._build_data_dict()
    
    def to_array(self):
        return self._fields
    
###############################################################################
# THIS IS ONLY TESTCODE!
###############################################################################
if __name__ == "__main__":
    DS = ArrayDataSet([(1,2,3),(4,5,6),(7,8,9)], names=("A","B","C"), metadata={'user':'cversek'})

