import matplotlib.pylab as plt
from matplotlib import pyplot

def plotLegendTable(colors, filepath):
    plt.figure()
    plt.axis('off')
    col_labels=['col1','col2','col3']
    row_labels=['row1','row2','row3']
    table_vals=[[i] for i in range(1, len(colors)+1)]


    the_table = plt.table(cellText=table_vals,
                      colWidths = [0.1]*3,
                      rowColours = colors,
                      loc='center')
    plt.text(12,3.4,'Table Title',size=8)

    plt.savefig(filepath)