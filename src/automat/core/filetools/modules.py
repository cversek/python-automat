def chain_import(chained_path):
    """allows import of a nested module from a package
    """
    try: 
        chain = chained_path.split('.')                                    #attempt on stringlike object first
    except AttributeError:
        chain = [mod for grp in chained_path for mod in grp.split('.')]    #normalize chain to sequence of single module names, no '.'s
    module_path = ".".join(chain)                                          #full path of the final module
    mod = __import__(module_path)                                          #import the module
    for submod in chain[1:]:                                               #descend the chain to retrieve the final module object
        mod = getattr(mod, submod)
    return mod
