###############################################################################
import re
from automat.core.filetools.base_parser import BaseParser

###############################################################################
class Error(Exception): pass
###############################################################################
class NISpyParser(BaseParser):
    def __init__(self, istream = None, debug = False):
        BaseParser.__init__(self, istream = istream, debug = debug)
        #compile parsing regexes
        self.WhitespaceLineRegex = re.compile(r'^\s+$')
        self.APICallRegex        = re.compile(r'^(\d+)\.  (\w+)\s*\((.*)\)$')
        self.StartTimeRegex      = re.compile(r'Start Time: (\d\d):(\d\d):(\d\d\.\d\d\d)')
        self.CallDurationRegex   = re.compile(r'Call Duration:? (\d\d):(\d\d):(\d\d\.\d\d\d)')
        self.StatusByteRegex     = re.compile(r'ibsta: 0x(\d+)')
        self.ibrspRegex          = re.compile(r'^(UD\d), (\d+) \((0x\w+)\)')           #serial poll
        self.ibwrtRegex          = re.compile(r'^(UD\d), "([^"]+)", (\d+) \(0x\w+\)')  #write
        self.ibrdRegex           = re.compile(r'^(UD\d), "([^"]+)", (\d+) \(0x\w+\)')  #read
        self._curr_line_group    = []
        self._curr_rec           = {}
        self.line_num            = 0
                
    def feed(self, line):
        self.line_num += 1
        #seperate information records on whitespace lines
        m = self.WhitespaceLineRegex.match(line) 
        if m:
            rec = BaseParser.feed(self, self._curr_line_group)
            self._curr_line_group = []  #reset the current group
            return rec
        else:  
            self._curr_line_group.append(line.strip()) 
            return None
    #--------------------------------------------------------------------------
    # Information Record Parsing
    #--------------------------------------------------------------------------
    def process(self, line_group):
        #create record, cache this also in class scope for introspective debugging
        self._curr_rec = rec = {}
        rec['info']    = "\n".join(line_group)
        #GPIB API call
        api_call_line = line_group[0].strip()
        m = self.APICallRegex.match(api_call_line)
        if m:
            rec['number']   = int(m.group(1))
            rec['api_call'] = api_call = {}
            api_call['func'] = func = m.group(2)
            api_call['args'] = m.group(3)
            #further process the API call
            handler_name = "_handle_api_call_%s" % func #construct the event handler name
            try:                    
                #retrieve and call the handler
                handler = self.__getattribute__(handler_name)
                api_call['info'] = handler(rec)
            except AttributeError:  #handler not found for event
                api_call['info'] = {'desc':'unknown API call'}
        else:
            raise Error(ValueError("api_call doesn't match the regex"))
        #timing info
        timing = line_group[2].strip()
        m1 = self.StartTimeRegex.search(timing)
        m2 = self.CallDurationRegex.search(timing)
        if m1 and m2:
            rec['start_time'] = [int(m1.group(1)),
                                 int(m1.group(2)),
                                 float(m1.group(3))]
            rec['call_duration'] = [int(m2.group(1)),
                                    int(m2.group(2)),
                                    float(m2.group(3))]
        else:
            raise ValueError, "timing doesn't match the regex:\n%s" % timing
        #status byte info
        status_line = line_group[3].strip()
        m = self.StatusByteRegex.match(status_line)
        if m:
            sta = m.group(1)
            rec['status_byte'] = int(sta,16) #convert from hex literal
        else:
            #ignore if it doesn't match
            rec['status_byte'] = None
            #raise Error(ValueError("status line doesn't match the regex:\n%s" % status_line))
        #finished
        return rec
    #--------------------------------------------------------------------------
    # GPIB API Call Parser Handlers
    #-------------------------------------------------------------------------- 
    def _handle_api_call_ibrsp(self, rec):
        "GPIB serial poll"
        args = rec['api_call']['args']
        m = self.ibrspRegex.match(args)
        if not m:
            raise Error(ValueError("args don't match: %s" % args))
        info = {}
        dev = m.group(1)
        info['dev']     = dev
        info['sta_dec'] = m.group(2)
        info['sta_hex'] = m.group(3)
        info['desc']    = 'serial poll'
        return info
        
    def _handle_api_call_ibwrt(self, rec):
        "GPIB write"
        args = rec['api_call']['args']
        m = self.ibwrtRegex.match(args)
        if not m:
            raise Error(ValueError("args don't match: %s" % args))
        info = {}
        info['desc'] = 'write'
        dev = m.group(1)
        info['dev'] = dev
        info['cmd'] = cmd = m.group(2)
        return info
        
    def _handle_api_call_ibrd(self, rec):
        "GPIB read"
        args = rec['api_call']['args']
        m =  self.ibrdRegex.match(args)
        if not m:
            raise Error(ValueError("args don't match: %s" % args)) 
        info = {}
        info['desc'] = 'read'
        dev = m.group(1)
        info['dev'] = dev
        #parse the output buffer to get the response
        rec_info = rec['info']
        buff = rec_info.split("\n")
        buff = buff[5:]
        #print "***START" + "*"*80
        #print buff
        #print "***END" + "*"*80
        #output as ascii follows 60 chars of hexadecimal
        buff = "".join([ line.strip()[60:] for line in buff])
        #last 2 are CRLF
        buff = buff[:-2]
        info['resp'] = buff
        return info
        
###############################################################################
# TEST CODE
###############################################################################
if __name__ == "__main__":
    import sys
    fname = sys.argv[1]
    istream = open(fname,'r')
    parser = NISpyParser(istream, debug = True)
    for rec in parser:
        print rec
