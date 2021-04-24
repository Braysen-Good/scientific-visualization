from .Parser import Parser
from .interactor2d import Interactor2D
from .interactor3d import Interactor3D

def viewSimulation(outputPath: str, width: int = 500, height: int = 400, force3d: bool = False, force2d: bool = False, **kwargs):
    """
    view the Physicell simulation output stored at the given path.
    
        outputPath: str - the path to the folder containing the simulation output.
        width: int - the width of the canvas to draw the visualization to
        height: int - the height of the canvas to draw the visualization to
        force3d: int - forces a 3d visualization of the simulation
        force2d: int - forces a 2d visualization of the simulation
        **kwargs - named arguments to pass to the visualizations, reference Interactor2D and Interactor3D for possible values.
    
    """
    parser = Parser(outputPath)
    if force2d or (parser.getFrame(parser.getFrameRange()[0]).environment.is2D and not force3d):
        return Interactor2D(parser, width, height, **kwargs)
    return Interactor3D(parser, width, height,**kwargs)