import re
from command_match import CommandMatch

class Error(Exception):
   """Base class for exceptions in this module."""
   def __init__(self,detail, info=""):
     self.detail = detail
     self.info   = info
   def __str__(self):
     if self.info:
       return "%s\n%s" % (self.detail,self.info)
     else:
       return str(self.detail)

RegexSubGroupRegex = re.compile("\(.+\)")

class Command(object):
    """Object for handling information and parsing related to ASCII remote commands"""
    def __init__(self, spec, dev_info = {'name':''}):
        #required attributes
        try:
            self.cmd  = spec['cmd']
            self.name = spec['name']
        except KeyError, info:
            raise Error("Command Specification Error:", info)
        #optional attributes
        self.set_pattern = spec.get('set_regex',None)
        self.set_regex   = _build_regex(self.set_pattern)
        sc = spec.get('set_conv',None)
        self.set_conv    = _build_conv(sc)
        self.set_range   = spec.get('set_range',None)
        #make sure that range is numerical
        try:
            if sc == 'int':
                self.set_range = map(int,self.set_range)
            elif sc == 'float':
                self.set_range = map(float,self.set_range)      
        except TypeError:
            pass #ignore failing in map command
        self.set_names   =  spec.get('set_names',{}) #a dictionary for filtering command values by name
        self.reset_val   =  spec.get('reset_val',None)
        self.query_cmd   =  spec.get('query_cmd',None)
        #build the query regex to match the query command, escaping the '?' chars
        if self.query_cmd:
            self.query_regex = _build_regex(escape_regex_chars(self.query_cmd))
        else:
            self.query_regex = None
        self.resp_regex  = _build_regex(spec.get('resp_regex',None))
        self.resp_conv   = _build_conv(spec.get('resp_conv',None))
        #to signify to gpib bus that command has completed
        self.wait_flag   = spec.get('wait_flag',None)
        self.desc  = spec.get('desc','')
        self.ref   = spec.get('desc','')
        #additional metadata
        self.dev_info = dev_info
    def set_interp(self,val):
        "a function to interpolate values into a set command string"
        if self.set_regex is not None:
            return RegexSubGroupRegex.sub(str(val),self.set_pattern)
        else:
            return "%s%s" % (self.cmd,val)
    #Common Formatting for Call strings
    def cmd_reset(self):
        "get the command string that sets the command to its default"
        if self.reset_val is None:
            raise  Error("have not specified 'reset_val' in command spec",self)
        else:
            return "%s%s" % (self.cmd,self.reset_val)
    def cmd_set(self,val=''):
        "check the range of val and get the command string that sets the command to its default"
        #check if the value is within range
        if self.set_range:
            test_val = float(val) 
            l =  self.set_range[0]
            u =  self.set_range[1]
            if not l <= test_val <= u:
                raise  Error("val = %s is out of range [%s,%s]" % (test_val,l,u), self)
        #filter through the set_names dictionary
        val = self.set_names.get(val,val)
        out = self.set_interp(val)
        #check if the command matches the set regex if it exists
        if self.set_regex:
            m = self.match_set(out)
            #uhh ohh, doesn't match
            if m is None:
                raise  Error("the command string '%s' does not match the 'set_regex': r'%s'" % (out,self.set_pattern), self)
        return out
    def cmd_query(self):
        if self.query_cmd is None:
            Error("cannot query this command", self) 
        return self.query_cmd
    #Response Handlind
    def filter_resp(self,resp):
        #try to match against the response regex
        if self.resp_regex: 
            m = self.resp_regex.match(resp)
            if m: #matched the command
                try: #replace with the first subgroup if possible
                    resp = m.group(1)
                except:
                    pass
        #convert the response            
        resp = self.resp_conv(resp) 
        return resp
    #Regex Matching
    def match(self, string):
        "match a string as either a set or query command - returns (match_obj, query?)"
        m = self.match_set(string)
        if m:
            return CommandMatch(self,m,False) #(command, match, isQuery)
        else:
            m = self.match_query(string)
            if m:
                return CommandMatch(self,m,True)
            else:
                return CommandMatch(self,None,False)
    def match_set(self, string):
        "try matching against the set_regex"
        if self.set_regex:
            return self.set_regex.match(string)
        else:
            return None
    def match_query(self, string):
        "try matching against the query_regex"
        if self.query_regex:
            return self.query_regex.match(string)
        else:
            return None
    #Display Functions
    def comment(self):
        return "%s, (%s)" % (self.desc,self.ref)
    def query_comment(self):
        return "query - %s, (%s)" % (self.desc, self.ref)
    def __str__(self):
        return "%s %s (%s): %s, ref. %s" % (self.dev_info['name'], 
                                            self.cmd, 
                                            self.name,
                                            self.desc,
                                            self.ref)
                                            
###############################################################################                                           
#Helper functions in this module                                           

RegexChars = ['?','*','+','(',')','[',']']

def escape_regex_chars(s):
    #first escape all escapes
    s = s.replace('\\','\\\\')
    for char in RegexChars:
        s = s.replace(char,'\\'+ char)
    return s
                                            
def _build_regex(regex_str):
    "force the regexes to match exactly but allowing whitespace following"
    #pass on None
    if regex_str is None: 
        return None
    else:
        return re.compile(r"^" + regex_str + r"\s*$")
        
TYPE_MAP = {
  "int"  : int,
  "float": float,
  "str"  : str
}

def _build_conv(conv_type):
    """Generate a parser function for a regex match from a type specification"""
    #return a NO OP function if not specified
    if conv_type is None: 
        return lambda val: val
    def conv_func(val):
        return TYPE_MAP[conv_type](val)
#    #get the number of groups in the regex
#    #normalize the form of the type_spec into a list, no duck-typing yet
#    if not isinstance(type_spec, list):
#        type_spec = [type_spec]
#    #get all the type converters
#    TYPE_CONVS = []
#    for type_name in type_spec:
#        try:
#            TYPE_CONVS.append(TYPE_MAP[type_name]) 
#        except KeyError:
#            raise ValueError, "'%s' is not a valid type specifier" % type_name
#    #make immutable or weirdness might occur when is is enclosed in 
#    # the inner function scope
#    TYPE_CONVS = tuple(TYPE_CONVS)
#    
#        
#    #build the parsing function
#    def parse_func(match):
#        groups = match.groups()
#        g_num = len(groups)
#        t_num = len(TYPE_CONVS)
#        #if no subroups specified and one converter, parse the whole match
#        if g_num == 0 and t_num == 1:
#            return TYPE_CONVS[0](match.group(0))
#        elif g_num != t_num: #this validation check should really be done while the yaml file is read
#            raise ValueError, "Number of regex subgroups does not match the number of type converters"
#        else: #match up subgroups [1:] to type converters
#            out = [] 
#            for i,grp in enumerate(groups):
#                out.append(TYPE_CONVS[i](grp))
#            if len(out) == 1: #only one value, unsequence it
#                return out[0]
#            else:             #make immutable
#                return tuple(out)
    #send it back
    return conv_func
