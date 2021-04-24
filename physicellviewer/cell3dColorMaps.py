import vtk
from . import constants
import numpy as np

def defaultColorMap3d(cells, variables, selectedCellId):
    """
    default 3d cell coloring function. Colors by cycle_model:
    
        live: green
        apoptosis_death: blue
        necrosis_death: red
        autophagy_death: orange
        
        selected_cell: white
    """
    tags = vtk.vtkFloatArray()
    cycleModels = cells[variables['cycle_model']]
    colors = np.zeros(cells.shape[1]) + (cycleModels < constants.apoptosis_death_model) + 2 * (cycleModels == constants.apoptosis_death_model) + 3 * (cycleModels == constants.necrosis_death_model) + 4 * (cycleModels == constants.autophagy_death_model)
    if selectedCellId is not None:
        colors[cells[variables['ID']] == selectedCellId] = 5
    for cell in colors:
        tags.InsertNextValue(float(cell))
    
    
    colorTransferFunction = vtk.vtkColorTransferFunction()
    colorTransferFunction.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(1.0, 0.0, 1.0, 0.0)
    colorTransferFunction.AddRGBPoint(2.0, 0.2, 0.2, 6.0)
    colorTransferFunction.AddRGBPoint(3.0, 1.0, 0.0, 0.0)
    colorTransferFunction.AddRGBPoint(4.0, 1.0, 6.0, 1.0)
    colorTransferFunction.AddRGBPoint(5.0, 1.0, 1.0, 1.0)
    
    return tags, colorTransferFunction