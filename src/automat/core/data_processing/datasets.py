###############################################################################
import shelve, copy
import numpy
###############################################################################
class DataSet(object):
    """A class which indexes sequences by names
    """
    def __init__(self, fields=None, names=None, metadata=None):
        #create default names if not specified
        if fields is None and names is None:
            raise ValueError, "must specify at least fields or names"
        elif names is None:
            names = ["f%d" % i for i in xrange(len(fields))]
        elif fields is None:
            fields = [[] for x in xrange(len(names))]
        else:
            assert len(names) == len(fields)
        #ensure that fields are lists
        fields = map(list,fields)       
        #cache the names to mantain ordering
        self._names = names        
        #build the underlying data storage structure        
        self._data = dict(zip(names,fields))
        #cache te metadata
        if not metadata:
            metadata = {}
        self._metadata = metadata    
    def __getitem__(self,indx):
        "allow index by name or column number"
        try: 
            #attempt to index by name first        
            return self._data[indx]
        except KeyError:
            #might be an integer try fetching in order
            try:            
                name = self._names[indx]
                return self._data[name]            
            except (IndexError, TypeError):
                #reraise as a key error
                raise KeyError, indx
    def get(self, key, value = None):
        return self._data.get(key, value)
    def names(self):
        return self._names
    def fields(self):
        return self.get_fields_fromnames(self._names)  
    def get_records(self):
        "obtain the data as records, warning: the empty cells are filled out with None objects"
        fields = self.fields()
        records = map(None,*fields)
        return records
    def get_fields_fromnames(self,names):
        out = []        
        for name in names:
            out.append(self.__getitem__(name))
        return out
    def get_metadata(self,key=None, default=None):
        if key is None:
            return self._metadata
        else:
            return self._metadata.get(key, default)
    def append_record(self,record):
        assert len(record) == len(self._names), "the record must contain as many entries as there are field"
        fields = self.fields()
        for item,field in zip(record,fields):
            field.append(item)
    def set_metadata(self, key, val):
        self._metadata[key] = val
    def update_metadata(self, overrides):
        self._metadata.update(overrides)
    def to_array(self):
        return numpy.array(self.get_records())
    def to_dict(self):
        "convert the dataset to a dict, copies all data"
        return copy.deepcopy(self._data) 

    def to_shelf(self, filename):
        "store to a new shelf database; will overwrite any existing file of same name"
        shelf = shelve.open(filename,'n')
        shelf['metadata'] = self._metadata
        shelf['names']    = self._names
        shelf['data']     = self._data
        shelf.close()

    def to_yaml(self,level=0, indent=2, newline='\n'):
        return newline.join(self.to_yaml_lines(level=level,indent=indent))
    def to_yaml_lines(self, level=0, indent=2):
        "convert the dataset to a YAML specification"               
        lines = []
        #output the metadata
        md = self._metadata        
        md_lines = []        
        spaces = " "*indent*level        
        md_lines.append("%smetadata:" % spaces)         
        if not md:
            #force an empty dictionary instead of None
            md_lines = [" ".join(md_lines+['{}'])]
        else:
            level += 1
            spaces = " "*indent*level
            for key, val in md.items():
                md_lines.append("%s%s: %s" % (spaces,key,val))
            level -= 1        
        lines.extend(md_lines)
        #output the data
        d = self._data        
        d_lines = []
        spaces = " "*indent*level        
        d_lines.append("%sdata:" % spaces)
        level += 1        
        spaces = " "*indent*level
        for name in self._names:
            field = d[name]
            d_lines.append("%s%s: %r" % (spaces,name,list(field)) )
        level -= 1        
        lines.extend(d_lines)
        return lines
    def to_csv_file(self, filepath, sep=",",comment_char="#", newline="\n", column_header = True, embed_metadata=True):
        text  = self.to_csv(sep=sep, 
                            comment_char=comment_char,
                            newline=newline,                            
                            column_header=column_header,
                            embed_metadata=embed_metadata,
                            ) 
        f = open(filepath,'w')
        f.write(text)
        f.close()       

    def to_csv(self, sep=",",comment_char="#", newline="\n", column_header = True, embed_metadata=True):
        lines = self.to_csv_lines(sep=sep, 
                                  comment_char=comment_char,
                                  column_header=column_header,
                                  embed_metadata=embed_metadata,
                                  )
        return newline.join(lines)
    def to_csv_lines(self, sep=",", comment_char="#",column_header=True,embed_metadata=True):
        lines = []
        if embed_metadata:
            lines.append("%s<METADATA>" % comment_char)
            for name, val in self._metadata.items():
                lines.append("%s%s: %s" % (comment_char,name,val) )
            lines.append("%s</METADATA>" % comment_char)
        if column_header:
            names_line = sep.join(self.names())
            lines.append("%s%s" % (comment_char,names_line) )
        #obtain the data as rows
        records = self.get_records()
        for rec in records:
            data_strs = map(str,rec)
            data_line = sep.join(data_strs)
            lines.append(data_line)
        return lines
        
    ###########################################################################
    @classmethod
    def from_dict(cls, spec):
        """Class factory function which builds a dataset obj from a dictionary 
            specification
        """
        data = spec['Data']
        metadata = spec['Metadata']
        names = data.keys()
        #fields are column data
        fields  = [data[name] for name in names]         
        dataset = cls(fields, names=names, metadata=metadata)
        return dataset
    @classmethod    
    def from_shelf(cls, filename):
        """Class factory function which builds a dataset obj from a shelf database file
        """
        shelf = shelve.open(filename)
        metadata = shelf['metadata']
        names    = shelf['names']
        data     = shelf['data']
        shelf.close()
        #fields are column data
        fields  = [data[name] for name in names] 
        dataset = cls(fields, names=names, metadata=metadata)
        return dataset  
          
    @classmethod    
    def from_yaml(cls, yaml_text):
        """Class factory function which builds a dataset obj from a YAML 
           specification
        """
        import yaml #require only if used
        spec = yaml.load(yaml_text)
        cls.from_dict(spec)
        
###############################################################################
# THIS IS ONLY TESTCODE!
###############################################################################
if __name__ == "__main__":
    DS = DataSet([(1,2,3),(4,5,6),(7,8,9)], names=("A","B","C"), metadata={'user':'cversek'})

