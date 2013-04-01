def convert_literal(literal):
    try:
        return int(literal)
    except ValueError:
        pass
    try:
        return float(literal)
    except ValueError:
        pass
    return literal.strip('"').strip("'")
    
def parse_scpi_query(query):
    items = query.split(";")
    curr_path = []
    d = {}
    for item in items:
        partial_path, val = item.split(None,1)
        val = convert_literal(val)
        partial_path = partial_path.split(':') 
        if partial_path[0] == "":
            curr_path = partial_path
        else:
            curr_path = curr_path[:-1]
            curr_path.extend(partial_path)
        key = ":".join(curr_path)
        d[key] = val
    return d  
