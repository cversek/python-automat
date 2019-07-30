import yaml
from . import command
from . import command_set
import re

def load(filename):
    "load yaml command set specification file into a CommandSet collection object"
    f_str = open(filename).read()
    #parse the yaml file
    parsed = yaml.load(f_str)
    dev_info = parsed.get('device',{})
    #build the command set object
    cmd_set  = command_set.CommandSet(dev_info)
    commands = parsed.get('commands',[])
    for cmd_spec in commands:
        cmd_obj = command.Command(cmd_spec,dev_info) 
        cmd_set.add(cmd_obj)
    return cmd_set
