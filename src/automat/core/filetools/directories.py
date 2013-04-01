""" Functions for managing directories
"""
import os, re

def fullpath(path):
    "regularizes a path including '~' for user home directory"
    path = os.path.expanduser(path)
    path = os.path.realpath(path)
    return path
    
def recur_mkdir(path):
    "make all directories in path, if they do not already exist"
    path = fullpath(path)
    subdirs = path.split(os.path.sep)
    for i in range(2,len(subdirs)+1):
        partial_path = os.path.sep.join(subdirs[:i])
        if not os.path.isdir(partial_path):
            os.mkdir(partial_path)
    

def dirwalk(path):
    "walk a directory tree, using a generator"
    if os.path.isdir(path):
        yield path
        for f in os.listdir(path):
            fullpath = os.path.join(path,f)
            if os.path.isdir(fullpath) and not os.path.islink(fullpath):
                for x in dirwalk(fullpath):  # recurse into subdir
                    yield x

def escape_brackets(path):
    "replace square brackets with []] and []] to fix problems with path patterns"
    def bracketrepl(m):
        if m.group(0) == "[":
            return "[[]"
        elif m.group(0) == "]":
            return "[]]"
    return re.sub("[][]",bracketrepl,path)
