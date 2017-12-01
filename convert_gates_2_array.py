'''
Created on Jul 25, 2017

@author: ameerh
'''
import sys
import re
#from sets import Set
import argparse
import plotTableWithCircles
import plotLegendTable
import random

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    OKCYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    ### parse input flags ###
print(bcolors.OKGREEN+'Parsing Command Line...'+bcolors.ENDC)
parser = argparse.ArgumentParser(description='Convert Z3 synthesis tool output to a matrix', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-f', default='./gates.txt',help='input gates file')
args=parser.parse_args()    
    ### open the file ###
print(bcolors.OKGREEN+'Parsing Input File...'+bcolors.ENDC)
try:
    f = ' '.join(open(args.f, 'rt').readlines())
except: 
    print(bcolors.FAIL+'Could not Parse Input File: gates.txt'+bcolors.ENDC)
    sys.exit(1)
    
    
    ### parse the file ###
rows = set()
cols = set()
Ts = set()
memristors = set()
data_matrix = {}
max_gate = 0
for gate in re.findall(r'\(define\-fun\sg([0-9]+)\_([RCT].*)\s\(\)\sInt\s+([0-9]+)\)', f):
    if gate[1][0] == 'R':
        rows.add(gate[2])
    elif gate[1][0] == 'C':
        cols.add(gate[2])
    elif gate[1][0] == 'T':
        Ts.add(gate[2])
    try:
        data_matrix[gate[0]][gate[1]] = gate[2]
    except:
        data_matrix[gate[0]] = {}
        data_matrix[gate[0]][gate[1]] = gate[2]
    max_gate = max(max_gate,int(gate[0]))    

inputs = set()
input_indices = []
output_indices = []
zero_rows = set()
zero_cols = set()
for input in re.findall(r'\(define\-fun\s(.*)\_(Row|Col)\s\(\)\sInt\s+([0-9]+)\)', f):
    inputs.add(input[0])
    if input[1] == 'Row':
        rows.add(input[2])
    elif input[1] == 'Col':
        cols.add(input[2])
    try:
        if input[1] == 'Row':
            data_matrix[input[0]]['Rin1'] = input[2]
        elif input[1] == 'Col':
            data_matrix[input[0]]['Cin1'] = input[2]
    except:
        data_matrix[input[0]] = {}
        if input[1] == 'Row':
            data_matrix[input[0]]['Rin1'] = input[2]
        elif input[1] == 'Col':
            data_matrix[input[0]]['Cin1'] = input[2]

    ### print the matrix and numbers ###
print(bcolors.OKGREEN+'Printing Output Matrix...'+bcolors.ENDC)
columns_params =  ['Rin1','Cin1','Rin2','Cin2','Rin3', 'Cin3', 'Rout', 'Cout','T']
sys.stdout.write(''.ljust(10))
for column in columns_params:
    sys.stdout.write(bcolors.HEADER+column.ljust(10)+bcolors.ENDC)
print('')    

for gate in range(1,max_gate+1):
    sys.stdout.write(bcolors.OKCYAN+('g#' +str(gate)).ljust(10)+bcolors.ENDC)
    for column in columns_params:
        try:
            sys.stdout.write(data_matrix[str(gate)][column].ljust(10))
        except:
            sys.stdout.write('-'.ljust(10))
    print('')    
    memristors.add(data_matrix[str(gate)]['Rin1']+','+data_matrix[str(gate)]['Cin1'])    
    try:
        memristors.add(data_matrix[str(gate)]['Rin2']+','+data_matrix[str(gate)]['Cin2']) 
        memristors.add(data_matrix[str(gate)]['Rin3']+','+data_matrix[str(gate)]['Cin3'])
    except:
        pass
    memristors.add(data_matrix[str(gate)]['Rout']+','+data_matrix[str(gate)]['Cout']) 
    output_indices.append((data_matrix[str(gate)]['Rout'], data_matrix[str(gate)]['Cout']))

for input in inputs:
    sys.stdout.write(bcolors.OKCYAN+(input).ljust(10)+bcolors.ENDC)
    for column in columns_params:
        try:
            sys.stdout.write(data_matrix[str(input)][column].ljust(10))
        except:
            sys.stdout.write('-'.ljust(10))
    print('')
    memristors.add(data_matrix[str(input)]['Rin1']+','+data_matrix[str(input)]['Cin1'])
    try:
        memristors.add(data_matrix[str(input)]['Rin2']+','+data_matrix[str(input)]['Cin2'])
        memristors.add(data_matrix[str(input)]['Rin3']+','+data_matrix[str(input)]['Cin3'])
    except:
        pass
    input_indices.append((data_matrix[str(input)]['Rin1'], data_matrix[str(input)]['Cin1']))

# Calculate the number of zero columns
for gate in range(1,max_gate+1):
    inputs_outputs = input_indices + output_indices
    found = False
    for io in inputs_outputs:
        if data_matrix[str(gate)]['Rin1'] == io[0] and data_matrix[str(gate)]['Cin1'] == io[1]:
            found = True
            break
    if not found:
        zero_rows.add(data_matrix[str(gate)]['Rin1'])
        zero_cols.add(data_matrix[str(gate)]['Cin1'])
    found = False
    for io in inputs_outputs:
        if 'Rin2' in data_matrix[str(gate)] and data_matrix[str(gate)]['Rin2'] == io[0] and data_matrix[str(gate)]['Cin2'] == io[1]:
            found = True
            break
    if not found and 'Rin2' in data_matrix[str(gate)]:
        zero_rows.add(data_matrix[str(gate)]['Rin2'])
        zero_cols.add(data_matrix[str(gate)]['Cin2'])
    found = False
    for io in inputs_outputs:
        if 'Rin3' in data_matrix[str(gate)] and data_matrix[str(gate)]['Rin3'] == io[0] and data_matrix[str(gate)]['Cin3'] == io[1]:
            found = True
            break
    if not found and 'Rin3' in data_matrix[str(gate)]:
        zero_rows.add(data_matrix[str(gate)]['Rin3'])
        zero_cols.add(data_matrix[str(gate)]['Cin3'])
        
# Create a graphic table

# Zip rows, cols and times
rowsDict = {}
i = 1
for r in sorted(rows, key=int):
    rowsDict[r] = i
    i = i + 1
colsDict = {}
i = 1
for c in sorted(cols, key=int):
    colsDict[c] = i
    i = i + 1
timesDict = {}
colorDict = {}
i = 1
for t in sorted(Ts, key=int):
    timesDict[t] = i
    
    # Create random color for each clock cycle
    colorDict[t] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    i = i + 1


 # Create a dictionary which its keys are the cells in the table, and the values
 # are the gate inputs and outputs.
table_cells = {}
for gate in range(1,max_gate+1):
    rand_color = colorDict[data_matrix[str(gate)]['T']]
    indices_tuple_rin1 = (rowsDict[data_matrix[str(gate)]['Rin1']], colsDict[data_matrix[str(gate)]['Cin1']])
    if indices_tuple_rin1 in table_cells:
        table_cells[indices_tuple_rin1].append(('A%d' % gate, rand_color))
    else:
        table_cells[indices_tuple_rin1] = [('A%d' % gate, rand_color)]
    indices_tuple_out = (rowsDict[data_matrix[str(gate)]['Rout']], colsDict[data_matrix[str(gate)]['Cout']])
    if indices_tuple_out in table_cells:
        table_cells[indices_tuple_out].append(('E%d' % gate, rand_color))
    else:
        table_cells[indices_tuple_out] = [('E%d' % gate, rand_color)]
    if 'Rin2' in data_matrix[str(gate)]:
        indices_tuple_rin2 = (rowsDict[data_matrix[str(gate)]['Rin2']], colsDict[data_matrix[str(gate)]['Cin2']])
        if indices_tuple_rin2 in table_cells:
            table_cells[indices_tuple_rin2].append(('B%d' % gate, rand_color))
        else:
            table_cells[indices_tuple_rin2] = [('B%d' % gate, rand_color)]
    if 'Rin3' in data_matrix[str(gate)]:
        indices_tuple_rin3 = (rowsDict[data_matrix[str(gate)]['Rin3']], colsDict[data_matrix[str(gate)]['Cin3']])
        if indices_tuple_rin3 in table_cells:
            table_cells[indices_tuple_rin3].append(('C%d' % gate, rand_color))
        else:
            table_cells[indices_tuple_rin3] = [('C%d' % gate, rand_color)]
for input in inputs:
    color = (0, 0, 0)
    indices_tuple_rin1 = (rowsDict[data_matrix[str(input)]['Rin1']], colsDict[data_matrix[str(input)]['Cin1']])
    if indices_tuple_rin1 in table_cells:
        table_cells[indices_tuple_rin1].append((input, color))
    else:
        table_cells[indices_tuple_rin1] = [(input, color)]

print(bcolors.OKBLUE+"Number of unique rows - " +bcolors.UNDERLINE+ str(len(rows))+bcolors.ENDC+bcolors.ENDC)
print(bcolors.OKBLUE+"Number of unique columns - " +bcolors.UNDERLINE+ str(len(cols))+bcolors.ENDC+bcolors.ENDC)
print(bcolors.OKBLUE+"Number of unique cells - " +bcolors.UNDERLINE+ str(len(memristors))+bcolors.ENDC+bcolors.ENDC)
print(bcolors.OKBLUE+"Number of unique Times - " +bcolors.UNDERLINE+ str(len(Ts))+bcolors.ENDC+bcolors.ENDC)
print(bcolors.OKBLUE+"Number of cycles to write zeros - " +bcolors.UNDERLINE+ str(min(len(zero_rows), len(zero_cols)))+bcolors.ENDC+bcolors.ENDC)

tableWithCirclesFile = "%s_table.png" % args.f.split('.')[0]
legendFile = "%s_legend.png" % args.f.split('.')[0]
plotTableWithCircles.plotTableWithCircles(len(cols), len(rows), table_cells, tableWithCirclesFile)
colorList = [(float(t[2])/255, float(t[1])/255, float(t[0])/255) for t in list(colorDict.values())]
plotLegendTable.plotLegendTable(colorList, legendFile)
