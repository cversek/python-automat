DEFAULT_MAX_QUERY_RETRY = 3

class CommandInterfaceMixIn:
    """ A Mixin class which interfaces a CommandSet class with a
        required CommunicationsMixIn"""
    def __init__(self,command_set, max_query_retry = DEFAULT_MAX_QUERY_RETRY):
        self.command_set = command_set
        self.max_query_retry = max_query_retry
    def _cmd_query(self,cmd_name, attempt=0):
        "query a command given its 'name' or 2-letter 'cmd' code"
        try:
            cmd  = self.command_set[cmd_name]
            resp = self._exchange(cmd.cmd_query())
            resp = cmd.filter_resp(resp)
            return resp
        except Exception, exc: #something bad happened
            if attempt >= self.max_query_retry:
                raise IOError, "exceed the maximum number of retries (%d) for a command query\nlast exception:%s" % (self.max_query_retry, exc)        
            else: #try again recursively
                return self._cmd_query(cmd_name,attempt = attempt + 1)                    
        
    def _cmd_set(self,cmd_name, val=''):
        "set using a command given its 'name' or 2-letter 'cmd' code"
        cmd = self.command_set[cmd_name]
        self._send(cmd.cmd_set(val))
    def _cmd_read(self,cmd_name, val=''):
        cmd = self.command_set[cmd_name]
        wf = cmd.wait_flag
        cmd_str = cmd.cmd_set(val)
        resp = None
        if wf is None:  #do not wait for gpib signal
            resp = self._exchange(cmd_str)
        else:           #wait for gpib signal bits
            resp = self._wait_on_exchange(cmd_str,wf)
        return cmd.resp_conv(resp)
    def _cmd_reset(self,cmd_name):
        cmd = self.command_set[cmd_name]
        self._send(cmd.cmd_reset())
       
