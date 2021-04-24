from . import constants
import numpy as np

def noFilter(cells, variables):
    """
    does not filer any cells out.
    
    """
    return np.full(cells.shape[1], True)

def onlyLiving(cells, variables):
    """
    only show living cells
    
    """
    return cells[variables['cycle_model']] < constants.apoptosis_death_model

def onlyDead(cells, variables):
    """
    only show dead cells

    """
    return cells[variables['cycle_model']] >= constants.apoptosis_death_model
