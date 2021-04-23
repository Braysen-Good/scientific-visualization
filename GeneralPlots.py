from Parser import Parser

import numpy as np
import matplotlib.pyplot as plt
class GeneralPlot:

    def __init__(self, fm: Parser):
        
        self.framecount = fm.getFrameCount()
        self.totalPop = np.zeros((self.framecount))
        self.healthyCount = np.zeros((self.framecount))
        self.starvedCount = np.zeros((self.framecount))
        self.deadCount = np.zeros((self.framecount))
        
        for i in range(self.framecount):
            cellCollection = fm.getFrame(i).cells
            variables = cellCollection.variables
            cells = cellCollection.data
            self.totalPop[i]=cells[0].size
            self.healthyCount[i]=np.count_nonzero(cells[variables['cycle_model']] == 5)
            self.starvedCount[i]=np.count_nonzero(cells[variables['cycle_model']] == 101)
            self.deadCount[i]=np.count_nonzero(cells[variables['cycle_model']] == 100)
            
    def plotPop(self):
        plt.plot(self.totalPop, color = "c", label='total population')
        plt.plot(self.healthyCount,color = "b", label='healthy cells')
        plt.plot(self.starvedCount,color = "r",  label='starved cells')
        plt.plot(self.deadCount,color = "k", label='dead cells')
        plt.ylabel('# of cells')
        plt.xlabel('frame number')
        plt.legend()
        plt.show()
        

