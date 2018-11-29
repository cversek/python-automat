from collections import OrderedDict
#automat dependencies
from automat.core.hwcontrol.commands.command import Command

class CommandSet(object):
    """Manages a set of Command objects for a given device as a dictionary subclass"""
    def __init__(self, dev_info = None,commands = None):
        #Two methods of retrieving the command object
        if dev_info is None:
            dev_info = OrderedDict()
            dev_info['name'] = ""
        self.dev_info    = dev_info
        self.cmd_lookup  = OrderedDict()
        self.name_lookup = OrderedDict()
        if commands is None:
            commands = []
        for command in commands:
            self.add(command)
    def __setitem__(self, key, val):
        "Overload the []= operator for item setting to dissallow"
        raise NotImplementedError("use the add(command) method instead")
    def __getitem__(self, key):
        "Overload the [] operator for item getting to look in both lookups"
        try:
            return self.cmd_lookup[key]
        except KeyError:
            #try in the other lookup
            return self.name_lookup[key]
    def add(self, command):
        try:
            #use the parent class method explicitly
            self.cmd_lookup[command.cmd] = command
            #also has by name if available
            if command.name:
                self.name_lookup[command.name] = command
        except NameError:
            raise ValueError("object does not export the Command interface")
    def cmds(self):
        "return the keys from the cmd_lookup"
        return list(self.cmd_lookup.keys())
    def names(self):
        "return the keys from the name_lookup"
        return list(self.name_lookup.keys())
    def match(self,string):
        "finds the first matching command and returns the CommandMatch object"
        for cmd, command in list(self.cmd_lookup.items()):
            cm = command.match(string)
            if cm.match: #there is a match so send it back
                return cm
        #no match was found
        return None
    @classmethod
    def from_yaml(cls,filename):
        "load yaml command set specification file into a CommandSet collection object"
        import yaml #imports here because this is an optional dependency
        f_str = open(filename).read()
        #parse the yaml file
        parsed = yaml.load(f_str)
        dev_info = parsed.get('device',None)
        #build the command set object
        cmd_set  = cls(dev_info = dev_info)
        commands = parsed.get('commands',[])
        for cmd_spec in commands:
            cmd_obj = Command(cmd_spec,dev_info) 
            cmd_set.add(cmd_obj)
        return cmd_set
