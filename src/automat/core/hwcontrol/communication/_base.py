class BaseCommunicationsMixIn:
    """Partial Interface for GPIB remotely contolled instruments"""
    def __init__(self):
        pass
    #Standard Interface Helper methods
    def _send(self, command):
        raise NotImplementedError
    def _read(self):
        raise NotImplementedError
    def _exchange(self, command):
        """Write a command, pause, read the response use only for query commands 
           which return quickly.  If the completion time of the command is large
           or uknown use the method _wait_on_command 
        """
        self._send(command)
        return self._read()
    def _wait_on_command(self, command):
        """Send a command, then wait for a response somehow"""
        raise NotImplementedError
    def _wait_on_exchange(self,command):
        """Call '_wait_on_command' then read and return the response"""
        self._wait_on_command(command,mask,poll_delay)
        return self._read()
