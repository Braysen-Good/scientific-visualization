from .interactorBase import Interactor
from .utils import output, debounce
from .cell2dColorMaps import defaultColorMap
from .environment2dRenderers import defaultRender2DEnvironment
from . import Parser
from . import constants

from ipycanvas import Canvas
import numpy as np


class Interactor2D(Interactor):
    """
    An interactive visualization of a 2D PhysiCell simulation
    
    """
    def __init__(self, parser: Parser, width: int = 500, height: int = 400, colorMap = defaultColorMap, filterFunction = None, backgroundColorRGB = "black", environmentRenderer = defaultRender2DEnvironment):
        """
        Visualize a 2D PhysiCell simulation
        
            parser - a simulation output parser
            width: int = 500 - the width of the canvas to draw to
            height: int = 400 - the height of the canvas to draw to
            colorMap: (cells: numpyArray, variables: Map<string, indicies>, selectedCellID: ?string) => Array<Tuple<fillColor: string, strokeColor: string, cellIndicies: numpyArray>> = defaultColorMap - a function resulting in the cell colors
            filterFunction: (cells: numpyArray, variables: Map<string, indicies>) => numpyArray (boolean/indicies) = None - a function resulting in an array of the indicies of the cells to draw
            backgroundColorRGB: string = "black" - the color to paint the background
            environmentRenderer: (attribute: string, environment: Parser.Environment) => numpyArray<x, y, 1/2/3/4> = defaultRender2DEnvironment - given an environment and the attribute to render, create an image (numpy array) to render (will span the bounds of the attribute)
        
        """
        super().__init__(parser, width, height, colorMap, filterFunction, (constants.MOVE_ACTION, constants.ZOOM_ACTION, constants.SELECT_ACTION))

        frame = parser.getFrame(self._currentFrame)
        mesh = frame.environment.mesh
        self._zoom = max((mesh.boundsX[1] - mesh.boundsX[0]) / width, (mesh.boundsY[1] - mesh.boundsY[0]) / height)
        
        self._xOffset = mesh.boundsX[0]
        self._yOffset = mesh.boundsY[0]
        
        self._environmentRenderer = environmentRenderer
        
        self._buffer = Canvas(width=width, height=height)
        
        self._backgroundColor = backgroundColorRGB
        
        self.update()
    
    @output.capture()
    def drawEnvironment(self, attribute: str):
        """
        draw the environment's attribute to the canvas
        
            attribute: string - the attribute of the environment to draw
        
        """
        if attribute is None:
            return
        canvas = self._canvas
        
        canvas.save()
        
        environment = self._parser.getFrame(self._currentFrame).environment

        xbounds = environment.mesh.boundsX
        ybounds = environment.mesh.boundsY

        image_data = self._environmentRenderer(attribute, environment)
        
        
        xCount, yCount, *_ = image_data.shape

        canvas.save()
        
        scale = (xbounds[1] - xbounds[0]) / ( xCount * self._zoom )
        
        canvas.scale( scale )
        
        x = (xbounds[0] - self._xOffset) / (scale * self._zoom)
        y = (ybounds[0] - self._yOffset) / (scale * self._zoom)

        canvas.put_image_data(image_data, x,  y)

        canvas.restore()
    
    def drawCells(self):
        """
        draw the cells of the current frame to the canvas.
        
        """
        canvas = self._canvas
    
        cells = self.getCellsToRender()
        cellVariables = self.getCellVariables()

        x = (cells[cellVariables['position.x']] - self._xOffset) / self._zoom
        y = (cells[cellVariables['position.y']] - self._yOffset) / self._zoom
        r = self.radiusOfCells(cells, cellVariables) / self._zoom
        
        combined = np.array([x, y, r])
        
        for fill, stroke, indices in self._colorMap(cells, cellVariables, self._selectedCell):
            split = combined[:,indices]
            if split.shape[0] == 0:
                continue
            x, y, r = split
            canvas.fill_style = fill
            canvas.fill_circles(x, y, r)
            canvas.stroke_style = stroke
            canvas.stroke_circles(x, y, r)
        
    
    def update(self):
        """
        Update and draw to the canvas if necessary
        
        """
        actualCanvas = self._canvas
        
        self._canvas = self._buffer
        canvas = self._buffer
        
        canvas.fill_style = self._backgroundColor
        canvas.fill_rect(0, 0, self._width, self._height)
        
        shouldDrawCells = False
        for element in self._visible:
            if element == constants.VISIBLE_CELL:
                shouldDrawCells = True
                continue
            self.drawEnvironment(element)
            
        
        if shouldDrawCells:
            self.drawCells()
        
        super().update()
        
        actualCanvas.draw_image(self._canvas)
        
        self._canvas = actualCanvas
    
        
    def onMouseDown(self, x: int, y: int):
        """
        Handle a mouse down event. Translates the canvas coordinates into the environment coordinate system.
        
        """
        self._envActionOriginX = x * self._zoom + self._xOffset
        self._envActionOriginY = y * self._zoom + self._yOffset
        self._actionOriginZoom = self._zoom
    
    @debounce(0.05)
    def onMouseMove(self, x: int, y: int):
        """
        Handle a mouse move event.
        
        """
        if self._clicking:
            if self.action == constants.MOVE_ACTION:
                self._xOffset -= (x - self._dragStartX) * self._zoom
                self._yOffset -= (y - self._dragStartY) * self._zoom
            elif self.action == constants.ZOOM_ACTION:
                self._zoom = max(self._actionOriginZoom * 2 ** ((self._actionOriginY - y) / 25), 0.0001)
                self._xOffset = self._envActionOriginX - self._actionOriginX * self._zoom
                self._yOffset = self._envActionOriginY - self._actionOriginY * self._zoom
                
            self._dragStartX = x
            self._dragStartY = y
            self.update()
    
    def selectCell(self, x: float, y: float):
        """
        Selects the cell located closest to the given x and y, if x and y fall within the cell.
        
        """
        x = self._envActionOriginX
        y = self._envActionOriginY
        
        frame = self._parser.getFrame(self._currentFrame)
    
        cells = frame.cells.data
        cellVariables = frame.cells.variables
        
        if self._filterFunction:
            cells = cells[:,self._filterFunction(cells, cellVariables)]
        
        distances = np.sqrt(np.square(x - cells[cellVariables['position.x']]) + np.square(y - cells[cellVariables['position.y']])) - self.radiusOfCells(cells, cellVariables)
        minIndex = np.argmin(distances)
        
        if distances[minIndex] <= 0:
            self._selectedCell = cells[cellVariables['ID'], minIndex]
        else:
            self._selectedCell = None
        
        self.update()