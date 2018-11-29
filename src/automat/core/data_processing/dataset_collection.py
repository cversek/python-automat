###############################################################################
import shelve
import yaml

###############################################################################
DEFAULT_YAML_INDENT = 4
###############################################################################
class DataSetCollection(object):
    """An ordered collection of DataSet objects.
    """    
    def __init__(self, datasets = None, metadata = None):
        if datasets is None:
            datasets = []
        self.datasets = datasets
        if metadata is None:
            metadata = {}        
        self.metadata = metadata
        self.index  = -1 #start off, not on the list

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.datasets)

    def __getitem__(self, i):
        return self.datasets[i]

    def __setitem__(self, i, dataset):
        self.datasets[i] = dataset

    def __getslice__(self, i,j):
        return self.datasets[i:j]

    def overwrite(self, dataset):
        if self.index < 0:
            raise IndexError("cannot overwrite the start index -1")
        self.__setitem__(self.index, dataset)

    def __next__(self):
        if self.index < len(self.datasets) - 1:
            self.index += 1
            return self.datasets[self.index]
        else:
            raise StopIteration
    
    def prev(self):
        if self.index > 0:
            self.index -= 1
            return self.datasets[self.index]     
          
        else:
            raise StopIteration       

    def curr(self):
        return self.datasets[self.index]

    def rewind(self):
        self.index = -1 

    def get_metadata(self,key=None):
        if key is None:
            return self.metadata.copy()
        else:
            return self.metadata[key]  
  
    def set_metadata(self, key, val):
        self.metadata[key] = val

    def update_metadata(self, overrides):
        self.metadata.update(overrides)
    
    def append(self, dataset):
        self.datasets.append(dataset)
    
    #--------------------------------------------------------------------------
    # OUTPUT METHODS

    def to_shelf(self, filename):
        "store to a new shelf database; will overwrite any existing file of same name"
        shelf = shelve.open(filename,'n')
        shelf['metadata'] = self.metadata
        shelf['datasets'] = self.datasets
        shelf.close()

    def to_yaml(self, indent = DEFAULT_YAML_INDENT, newline = '\n'):
        "output as a YAML formatted string"
        try:
            from yaml import CDumper as Dumper
        except ImportError:
            from yaml import Dumper   
        buff = []
        buff.append('---')
        buff.append(yaml.dump({'metadata':self.metadata}, indent=indent, Dumper = Dumper, default_flow_style = False))
        buff.append('datasets:')
        sub_buff = []
        for ids in self.datasets:
            sub_buff.append('-') #place yaml list marker
            for line in ids.to_yaml_lines(level = 1, indent = indent):
                sub_buff.append(line)
        sub_buff = newline.join(sub_buff)
        buff.append(sub_buff)
        buff.append('...') 
        buff = newline.join(buff)        
        return buff
 
    #--------------------------------------------------------------------------
    # CLASS METHODS
    @classmethod
    def from_shelf(cls, filename):
        """Class factory function which builds a DataSetCollection object from 
           a stored shelf file description.
        """
        shelf = shelve.open(filename,'r')
        md  = shelf['metadata']
        ids = shelf['datasets']
        obj = cls(datasets = ids, metadata = md)
        return obj 
