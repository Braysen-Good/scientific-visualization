import numpy as np
from . import constants

def defaultColorMap(cells, variables, selectedCell):
    """
    default 2d cell coloring function. Colors by cycle_model:
    
        live: green
        apoptosis_death: blue
        necrosis_death: red
        autophagy_death: orange
        
        selected_cell: white
    
    """
    selectedCellIndex = cells[variables['ID']] == selectedCell
    notSelectedCellIndex = np.invert(selectedCellIndex)
    cycles = cells[variables['cycle_model']]
    return [
        ('#004400', 'green', np.logical_and(cycles < constants.apoptosis_death_model, notSelectedCellIndex)),
        ('#000099', '#0000CC', np.logical_and(cycles == constants.apoptosis_death_model, notSelectedCellIndex)),
        ('#440000', 'red', np.logical_and(cycles == constants.necrosis_death_model, notSelectedCellIndex)),
        ('#CC8500', '#FFA500', np.logical_and(cycles == constants.autophagy_death_model, notSelectedCellIndex)),
        ('#AAAAAA', 'white', selectedCellIndex)
    ]