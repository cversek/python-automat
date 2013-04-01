class CommandMatch(object):
  """provides parsing handling for Command.match"""
  def __init__(self,command,m,isQuery):
    self.command = command
    self.match   = m
    self.isQuery = isQuery
  def parse(self, resp=None):
    """will parse as a set command if resp is None and self.isQuery == False
       OR as a query return value if resp is not None and self.isQuery == True
    """
    isQuery = self.isQuery
    if resp is None and not isQuery:
      groups = self.match.groups()
      if groups:
        #parse the value from the command string match
        val = groups[0]
        return self.command.set_conv(val)
      else: #is direct set command (no value required)
        return None
    elif resp is not None and isQuery:  
      #try to match the resp_regex
      match = self.command.resp_regex.match(resp)
      if match:
        return self.command.resp_conv(match)
      else:
        return None
    else:  #nothing to do
      return None
