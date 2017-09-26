import re
import pdb

def readoperations(data, varLegendRow, varLegendCol):
    
    # last row is gnd, for conversion of NOT to NOR
    D = []
    types = []
    for i in xrange(len(varLegendCol)+1):
        types.append(0)
    for i in xrange(len(varLegendRow)+1):
        l = []
        for j in xrange(len(varLegendCol)):
            l.append(0)
        D.append(l)
    occurences = re.findall("inv1.*?\(\.a\((.*?)\).*?\.O\((.*?)\)\);", data, re.DOTALL)
    for occur in occurences:
        in1 = occur[0].replace(" ","")
        out = occur[1].replace(" ","")
    
        # update dependecies
        in1Idx = varLegendRow.index(in1)
        outIdx = varLegendCol.index(out)
        D[in1Idx][outIdx] = 1
        D[len(varLegendRow)][outIdx] = 1 # gnd => 1 every column of a NOT gate
        types[outIdx] = 1    
    occurences = re.findall("nor2.*?\(\.a\((.*?)\).*?\.b\((.*?)\).*?\.O\((.*?)\)\);", data, re.DOTALL)
    for occur in occurences:
        in1 = occur[0].replace(" ","")
        in2 = occur[1].replace(" ","")
        out = occur[2].replace(" ","")
    
        # update dependecies
        in1Idx = varLegendRow.index(in1)
        in2Idx = varLegendRow.index(in2)
        outIdx = varLegendCol.index(out)
        D[in1Idx][outIdx] = 1
        D[in2Idx][outIdx] = 1
        types[outIdx] = 2    
    occurences = re.findall("nor3.*?\(\.a\((.*?)\).*?\.b\((.*?)\).*?\.O\((.*?)\)\);", data, re.DOTALL)
    for occur in occurences:
        in1 = occur[0].replace(" ","")
        in2 = occur[1].replace(" ","")
        in3 = occur[2].replace(" ","")
        out = occur[3].replace(" ","")
    
        # update dependecies
        in1Idx = varLegendRow.index(in1)
        in2Idx = varLegendRow.index(in2)
        in3Idx = varLegendRow.index(in3)
        outIdx = varLegendCol.index(out)
        D[in1Idx][outIdx] = 1
        D[in2Idx][outIdx] = 1
        D[in3Idx][outIdx] = 1
        types[outIdx] = 3    
    return D, types
        
def generate_Z3_file(name, D, types, InputString, latency, numrows=1000, numcols=1000):
    
    # Get needed data from files
    optfilename = name + '_python_Z3input.txt'
    print optfilename
    opt = file(optfilename,'wb')
    
    Dval  = D
    r = len(Dval)
    c = len(Dval[0])
    #Dval  = [Dval[r - 1][:] , Dval[0:r - 1][:]]
    Dval.insert(0, Dval.pop())
    gate_num = len(Dval[0])
    gate_rows = range(len(Dval) - gate_num, len(Dval), 1)
    input_rows = range(1, len(Dval) - gate_num, 1)
    
    # Create .mod file
    opt.write(';## Define params\n')
    opt.write('(declare-const GATENUM Int)\n')
    opt.write('(declare-const COLNUM Int)\n')
    opt.write('(declare-const ROWNUM Int)\n')
    opt.write('(assert (= GATENUM %d))\n' % gate_num)
    opt.write('(assert (= COLNUM %d))\n' % numcols)
    opt.write('(assert (= ROWNUM %d))\n' % numrows)
    opt.write('\n')
    opt.write(';## Define variables\n')
    
    for i in xrange(1, gate_num + 1):
        opt.write('(declare-const g%d_Rin1 Int)\n'% i)
        opt.write('(declare-const g%d_Cin1 Int)\n'% i)
        if types[i-1] == 2:
            opt.write('(declare-const g%d_Rin2 Int)\n'% i)
            opt.write('(declare-const g%d_Cin2 Int)\n'% i)
        opt.write('(declare-const g%d_Rout Int)\n'% i)
        opt.write('(declare-const g%d_Cout Int)\n'% i)
        opt.write('(declare-const g%d_T Int)\n' % i)
    for i in xrange(len(InputString)):
        opt.write('(declare-const %s_Row Int)\n'% InputString[i])
        opt.write('(declare-const %s_Col Int)\n'% InputString[i])
        
    opt.write('(declare-const Latency Int)\n')
    opt.write('(declare-const sumRowsCols Int)\n')
    opt.write('\n')
    opt.write(';## Constraints\n')
    opt.write(';# Bounds\n')
    
    for i in xrange(1, gate_num + 1):
        opt.write('(assert (> g%d_T 0))\n' % i)

    for i in xrange(1, gate_num + 1):
        opt.write('(assert (and (> g%d_Rin1 0) (<= g%d_Rin1 ROWNUM)))\n' % (i,i))
        opt.write('(assert (and (> g%d_Cin1 0) (<= g%d_Cin1 COLNUM)))\n' % (i,i))
        if types[i-1] == 2:
            opt.write('(assert (and (> g%d_Rin2 0) (<= g%d_Rin2 ROWNUM)))\n' % (i,i))
            opt.write('(assert (and (> g%d_Cin2 0) (<= g%d_Cin2 COLNUM)))\n' % (i,i))
        opt.write('(assert (and (> g%d_Rout 0) (<= g%d_Rout ROWNUM)))\n' % (i,i))
        opt.write('(assert (and (> g%d_Cout 0) (<= g%d_Cout COLNUM)))\n' % (i,i))
    for i in xrange(1, len(InputString) + 1):
        opt.write('(assert (and (> %s_Row 0) (<= %s_Row ROWNUM)))\n' % (InputString[i-1],InputString[i-1]))
        opt.write('(assert (and (> %s_Col 0) (<= %s_Col COLNUM)))\n' % (InputString[i-1],InputString[i-1]))
    opt.write('\n');

    opt.write(';# Unique rows or columns\n');
    for i in xrange(1, gate_num + 1):
        if types[i-1] == 1:
            opt.write('(assert (or\n')
            opt.write('    (and (= g%d_Rin1 g%d_Rout) (not(= g%d_Cin1 g%d_Cout))) ;Either rows are equal and columns are different\n' % (i,i,i,i))
            opt.write('    (and (not(= g%d_Rin1 g%d_Rout)) (= g%d_Cin1 g%d_Cout)) ;Or columns are equal and rows are different\n' % (i,i,i,i))
            opt.write('  )\n')
            opt.write(')\n')
        elif types[i-1] == 2:
            opt.write('(assert (or\n')
            opt.write('    (and (= g%d_Rin1 g%d_Rin2 g%d_Rout) (not(= g%d_Cin1 g%d_Cin2)) (not(= g%d_Cin1 g%d_Cout)) (not(= g%d_Cin2 g%d_Cout))) ;Either rows are equal and columns are different\n' % (i,i,i,i,i,i,i,i,i))
            opt.write('    (and (not(= g%d_Rin1 g%d_Rin2)) (not(= g%d_Rin1 g%d_Rout)) (not(= g%d_Rin2 g%d_Rout)) (= g%d_Cin1 g%d_Cin2 g%d_Cout)) ;Or columns are equal and rows are different\n' % (i,i,i,i,i,i,i,i,i))
            opt.write('  )\n')
            opt.write(')\n')
    
    opt.write('\n');
    opt.write(';# Parallel operation of NOR2 gates\n');
    for i in xrange(1, gate_num + 1):
        for j in xrange(i+1, gate_num + 1):
            if types[i-1] == types[j-1] and types[i-1] == 2: # If both gates are NOR2
                opt.write('(assert\n')
                opt.write('  (or (not(= g%d_T g%d_T))\n' %  (i,j))
                opt.write('    (and (or (and (= g%d_Cin1 g%d_Cin1) (= g%d_Cin2 g%d_Cin2)) (and (= g%d_Cin1 g%d_Cin2) (= g%d_Cin2 g%d_Cin1))) (= g%d_Cout g%d_Cout) (and (= g%d_Rin1 g%d_Rin2 g%d_Rout) (= g%d_Rin1 g%d_Rin2 g%d_Rout)))\n' % (i,j,i,j,i,j,i,j,i,j,i,i,i,j,j,j))   
                opt.write('    (and (or (and (= g%d_Rin1 g%d_Rin1) (= g%d_Rin2 g%d_Rin2)) (and (= g%d_Rin1 g%d_Rin2) (= g%d_Rin2 g%d_Rin1))) (= g%d_Rout g%d_Rout) (and (= g%d_Cin1 g%d_Cin2 g%d_Cout) (= g%d_Cin1 g%d_Cin2 g%d_Cout)))\n' % (i,j,i,j,i,j,i,j,i,j,i,i,i,j,j,j))   
                opt.write('  )\n')
                opt.write(')\n')
    opt.write('\n')
    
    opt.write(';# Parallel operation of NOT gates\n');
    for i in xrange(1, gate_num + 1):
        for j in xrange(i+1, gate_num + 1):
            if types[i-1] == types[j-1] and types[i-1] == 1: # If both gates are NOT
                opt.write('(assert\n')
                opt.write('  (or (not(= g%d_T g%d_T))\n' %  (i,j))
                opt.write('    (and (= g%d_Cin1 g%d_Cin1) (= g%d_Cout g%d_Cout) (= g%d_Rin1 g%d_Rout) (= g%d_Rin1 g%d_Rout))\n' % (i,j,i,j,i,i,j,j))
                opt.write('    (and (= g%d_Rin1 g%d_Rin1) (= g%d_Rout g%d_Rout) (= g%d_Cin1 g%d_Cout) (= g%d_Cin1 g%d_Cout))\n' % (i,j,i,j,i,i,j,j))
                opt.write('  )\n')
                opt.write(')\n')
    opt.write('\n')
    
    opt.write(';# NOT and NOR2 gates cannot operate in the same clock cycle\n')
    for i in xrange(1, gate_num + 1):
        for j in xrange(i+1, gate_num + 1):
            if not (types[i-1] == types[j-1]): # If one of the gates is NOT and the other is NOR2
                opt.write('(assert (not (= g%d_T g%d_T)))\n' % (i,j))
    opt.write('\n')
    
    opt.write(';# All outputs are different\n')
    for i in xrange(1, gate_num + 1):
        for j in xrange(i+1, gate_num + 1):
            opt.write('(assert (or (not(= g%d_Cout g%d_Cout)) (not(= g%d_Rout g%d_Rout))))\n' % (i,j,i,j))
    opt.write('\n')
    
    opt.write(';# Conectivity constraints\n')
    for i in xrange(1, gate_num + 1):
        inputs = [gate_rows.index(k)+1 for k in gate_rows if Dval[k][i - 1] == 1] 
        for j in xrange(len(inputs)): # No protection against loops. Netlist must be valid.
            opt.write('(assert (= g%d_Rout g%d_Rin%d))\n' % (inputs[j],i,j+1))
            opt.write('(assert (= g%d_Cout g%d_Cin%d))\n' % (inputs[j],i,j+1))
            opt.write('(assert (< g%d_T g%d_T))\n' % (inputs[j],i))
        circuit_inputs =  [input_rows.index(k)+1 for k in input_rows if Dval[k][i-1] == 1] 
        for j in xrange(len(circuit_inputs)): # No protection against loops. Netlist must be valid.
            opt.write('(assert (= %s_Row g%d_Rin%d))\n' % (InputString[circuit_inputs[j]-1],i,j+len(inputs)+1))
            opt.write('(assert (= %s_Col g%d_Cin%d))\n' % (InputString[circuit_inputs[j]-1],i,j+len(inputs)+1))
    opt.write('\n')
    
    opt.write(';# Circuit inputs constraints\n')
    for i in xrange(1, gate_num + 1):
        for j in xrange(len(InputString)):
            opt.write('(assert (not (and (= %s_Row g%d_Rout) (= %s_Col g%d_Cout))))\n' % (InputString[j], i, InputString[j], i))
    for i in xrange(len(InputString)):
        for j in xrange(i + 1, len(InputString)):
            opt.write('(assert (not (and (= %s_Row %s_Row) (= %s_Col %s_Col))))\n' % (InputString[i], InputString[j], InputString[i], InputString[j]))
    opt.write('\n')
    
    opt.write(';# Latency constraints\n')
    for i in xrange(1, gate_num + 1):
        opt.write('(assert (>= Latency  g%d_T))\n' % i)
    opt.write('\n')

    opt.write(';# Energy constraints\n')
    opt.write('(assert (= sumRowsCols (+ \n')
    for i in xrange(1, gate_num + 1):
        if types[i - 1] == 1:
            opt.write('g%d_Rin1 g%d_Cin1 g%d_Rout g%d_Cout\n' % (i, i, i, i))
        elif types[i - 1] == 2:
            opt.write('g%d_Rin1 g%d_Rin2 g%d_Cin1 g%d_Cin2 g%d_Rout g%d_Cout\n' % (i, i, i, i, i, i))
    for i in xrange(len(InputString)):
        opt.write('%s_Row %s_Col\n' % (InputString[i], InputString[i]))
    opt.write(')))\n')
    opt.write('\n')

    opt.write(';## Objective function\n')
    opt.write('(assert (= Latency %d))\n' % latency)
    opt.write('(minimize(+ sumRowsCols 0))\n')
    opt.write('(check-sat)\n')
    opt.write('(get-model)\n')
    opt.close()
    return optfilename
    
def netlist_to_z3(filename, latency):
    BenchmarkStrings = [filename]
    for ii in xrange(len(BenchmarkStrings)):
        bmfId = file(BenchmarkStrings[ii]) # open file
        data = bmfId.read()
        
        # read input/output/wire
        
        InputString = re.search("input (.*?);", data, re.DOTALL).groups(0)[0].replace(" ","").replace('\n','').split(',')
        
        OutputString = re.search("output (.*?);", data, re.DOTALL).groups(0)[0].replace(" ","").replace('\n','').split(',')
            
        WireString = re.search("wire (.*?);", data, re.DOTALL).groups(0)[0].replace(" ","").replace('\n','').split(',')

        # map variables to numbers
        varLegendCol = WireString + OutputString
        varLegendRow = InputString + WireString + OutputString
    
        # analyze dependencies
        D, types = readoperations(data,varLegendRow,varLegendCol)
        bmfId.close() # close file
        
        r = len(varLegendRow)+1
        c = varLegendCol
        
        return generate_Z3_file(BenchmarkStrings[ii], D, types, InputString, latency, r, r)
