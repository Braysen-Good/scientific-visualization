from .Parser import Parser 
from . import constants

import numpy as np
import matplotlib.pyplot as plt

class GeneralPlot:

    def __init__(self, fm: Parser):
        
        self.framecount = fm.getFrameCount()
        self.totalPop = np.zeros((self.framecount))
        self.healthyCount = np.zeros((self.framecount))
        self.starvedCount = np.zeros((self.framecount))
        self.deadCount = np.zeros((self.framecount))
        self.apoptoticDeathCount = np.zeros((self.framecount))
        
        for i in range(self.framecount):
            cellCollection = fm.getFrame(i).cells
            variables = cellCollection.variables
            cells = cellCollection.data
            self.totalPop[i] = cells[0].size
            cellModel = cells[variables['cycle_model']]
            self.healthyCount[i] = np.count_nonzero(cellModel < constants.apoptosis_death_model)
            self.starvedCount[i] = np.count_nonzero(cellModel > constants.apoptosis_death_model)
            self.apoptoticDeathCount[i] = np.count_nonzero(cellModel == constants.apoptosis_death_model)
            self.deadCount[i] = np.count_nonzero(cellModel >= constants.apoptosis_death_model)
            
    def plotPop(self):
        plt.plot(self.totalPop, color = "c", label = 'total population')
        plt.plot(self.healthyCount, color = "g", label = 'healthy cells')
        plt.plot(self.starvedCount, color = "r",  label = 'starved cells (dead)')
        plt.plot(self.apoptoticDeathCount, color = "tab:orange", label='apoptotic cells (dead)')
        plt.plot(self.deadCount, color = "k", label = 'dead cells (total)')
        plt.ylabel('# of cells')
        plt.xlabel('frame number')
        plt.legend()
        plt.show()
        

