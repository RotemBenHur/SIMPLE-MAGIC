def get_all_paths(Dval, gates_list):
    last_gate = gates_list[-1]
    gate_num = len(Dval[0])
    gate_rows = range(len(Dval) - gate_num, len(Dval), 1)
    input_rows = range(1, len(Dval) - gate_num, 1)
    foundPaths = 0
    paths = []
    
    # Iterate all columns in Dval
    for i in range(len(Dval[0])):
    
        # If gate #i is connected to last_gate, get all the paths with this sub-path
        if Dval[len(input_rows) + last_gate - 1][i] == 1:
            ret = get_all_paths(Dval, gates_list + [i + 1])
            
            # Append the paths to the path list
            if ret != None and not len(ret) == 0:
            
                # Append the paths 
                for path in ret:
                    paths.append(path)
            foundPaths = foundPaths + 1
    if not foundPaths:
        return [gates_list]
    else:
        return paths
                
def get_all_paths_wrapper(Dval):
    gate_num = len(Dval[0])
    gate_rows = range(len(Dval) - gate_num, len(Dval), 1)
    input_rows = range(1, len(Dval) - gate_num, 1)
    
    # Find all first gates in paths
    paths = []
    for i in range(len(Dval[0])):
        isFirst = False
        for j in input_rows:
            if Dval[j-1][i] == 1:
                isFirst = True
                break
        if isFirst:
        
            # Get all the paths that start with this first gate 
            gate_paths = get_all_paths(Dval, [i+1])
            
            # Add the paths to the path list
            for path in gate_paths:
                paths.append(path)
    return paths        
