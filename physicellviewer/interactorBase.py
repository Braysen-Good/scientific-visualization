from .Parser import Parser
from .GeneralPlots import GeneralPlot
from .utils import output
from . import constants

from IPython.display import display

import math
from ipycanvas import Canvas
import ipywidgets as widgets
import matplotlib.pyplot as plt

figureNumber = 0

class Interactor:
    """
    Base interactor class. Is an abstract class. Handles shared functionality such as canvases and graphs.
    
    """
    def __init__(self, parser: Parser, width: int, height: int, colorMap, filterFunction, availableActions):
        """
        Setup the interactor variables, should be called first in a sub class.
        
            parser - a simulation output parser
            width - the width of the canvas to draw to
            height - the height of the canvas to draw to
            colorMap - a function resulting in the cell colors (distinct results based on subclass, see subclass documentation for necessary return values)
            filterFunction - a function resulting in an array of the indicies of the cells to draw
            availableActions - a list of all the actions that can be performed on the canvas
        
        """
        self._currentFrame = parser.getFrameRange()[0]
        self._canvas = Canvas(width=width, height=height)
        self._parser = parser
        self._colorMap = colorMap
        self._height = height
        self._width = width
        self._filterFunction = filterFunction
        
        self._cellFigure = None
        self._generalGraph = GeneralPlot(parser)
        
        frame = parser.getFrame(self._currentFrame)
        mesh = frame.environment.mesh
        self._availableEnvironments = [*frame.environment.current.attributes]
        
        self._canvas.on_mouse_down(self._onMouseDown)
        self._canvas.on_mouse_move(self._onMouseMove)
        self._canvas.on_mouse_up(self._onMouseUp)
        self._canvas.on_mouse_out(self._onMouseOut)
        
        self.action = availableActions[0]
        
        self._buttons = widgets.RadioButtons(
            options=availableActions,
            value=self.action,
            description='Mouse Action:',
            disabled=False,
        )
        self._buttons.observe(self.onToolChange, names='value')
        
        self._visible = (constants.VISIBLE_CELL,)
        self._environmentButtons = widgets.SelectMultiple(
            options=[constants.VISIBLE_CELL, *self._availableEnvironments],
            description='Visible:',
            disabled=False,
            value=[constants.VISIBLE_CELL],
        )
        self._environmentButtons.observe(self.onVisibilityChange, names='value')
        
        self._availableAttributes = [*frame.cells.variables.keys()]
        self._selectedAttribute = self._availableAttributes[0]
        self._previousSelectedAttribute = None
        self._previousSelectedAttributeCell = None
        self._attributes = widgets.RadioButtons(
            options=self._availableAttributes,
            value=self._selectedAttribute,
            description='Attribute Graph:\n',
            disabled=False,
        )
        self._attributes.observe(self.onAttriChange, names='value')

        self._frameSelector = widgets.IntSlider(
            value=self._currentFrame,
            min=parser.getFrameRange()[0],
            max=parser.getFrameRange()[1] - 1,
            step=1,
            description='Frame:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='d'
        )
        self._frameSelector.observe(self.onFrameChange, names='value')
        
        self._clicking = False
        self._dragStartX = 0
        self._dragStartY = 0
        self._actionOriginX = 0
        self._actionOriginY = 0
        
        self._selectedCell = None
    
    def setColorMap(self, colorMap):
        """
        Set the cell coloring function.
        
            colorMap: the cell coloring function
        
        """
        self._colorMap = colorMap
        self.update()
    
    def setFilterFunction(self, filterFunction):
        """
        Set the cell filtering function
        
            filterFunction: the filtering function
        
        """
        self._filterFunction = filterFunction
        self.update()
    
    def onToolChange(self, action):
        """
        Handle a user action which changes the canvas tool
        
            action: an ipyWidget radio button selection action
        
        """
        self.action = action.new
    
    @output.capture()
    def onVisibilityChange(self, action):
        """
        Handle a user action which changes the elements which are visibile on the canvas
        
            action: an ipyWidget multi selection action
        
        """
        self._visible = action.new
        self.update()
        
    @output.capture()    
    def onAttriChange(self, action):
        """
        Handle a user action which changes the attribute to display for the selected cell
        
            action: an ipyWidget radio button selection action
        
        """
        self._selectedAttribute = action.new
        self._updateCellPlot()
        
    @output.capture()
    def _updateCellPlot(self):
        """
        Update the plot which shows how the currently selected attribute changes over time for the selected cell
        
        """
        if (self._previousSelectedAttribute == self._selectedAttribute and self._previousSelectedAttributeCell == self._selectedCell) or self._selectedCell is None:
            return
        
        self._previousSelectedAttribute = self._selectedAttribute
        self._previousSelectedAttributeCell = self._selectedCell
        
        data = []
        timestamps = []
        time = 0
        variables = self.getCellVariables()
        for frameNumber in range(*self._parser.getFrameRange()):
            cell = self.getSelectedCell(frameNumber)
            data.append(cell[variables[self._selectedAttribute]])
            timestamps.append(time)
            time += 1
            
        if self._cellFigure is not None:
            plt.figure(self._cellFigure.get_label())
            self._cellAx.clear()
            ln, = self._cellAx.plot(timestamps, data)
            self._cellAx.set_xlabel('time')
            self._cellAx.set_ylabel(self._selectedAttribute)
            self._cellAx.set_title(self._selectedAttribute + " for cell " + str(int(self._selectedCell)))
            ln.set_color('orange')
        
        
    def onFrameChange(self, action):
        """
        Handle a user action which changes the frame to view
        
            action: an ipyWidget slider action
        
        """
        self._currentFrame = action.new
        self.update()
    

    def getCellVariables(self, frame: int = None):
        """
        Get the cell varaibles for the frame
        
            frame: int - the frame number to get the variables from
        
        """
        if frame is None:
            frame = self._currentFrame
        return self._parser.getFrame(frame).cells.variables
    
    def getCell(self, cellId: int, frame: int = None):
        """
        Get the cell from the frame (used current frame if not specified)
        
            cellId: int - the id of the cell to get
            frame: int = currentFrame - the frame number to get the cell from
        
        """
        if frame is None:
            frame = self._currentFrame
        cells = self.getCells(frame)
        variables = self.getCellVariables()
        cellColumn = cells[variables['ID']] == cellId
        return cells[:,cellColumn].reshape(-1)
    
    def getCells(self, frame: int = None):
        """
        Get the cells from the frame (uses the current frame if not specified)
        
            frame: int = currentFrame - the frame number to get the cells from
        
        """
        if frame is None:
            frame = self._currentFrame
        return self._parser.getFrame(frame).cells.data
    
    def getCellsToRender(self, frame: int = None):
        """
        Get the cells to render from the given frame (uses the current frame if not specified). Applies
        the current cell filtering function on the result.
        
            frame: int = currentFrame - the frame number to get the cells from
        
        """
        cells = self.getCells(frame)
        
        if self._filterFunction:
            cellVariables = self.getCellVariables(frame)
            cells = cells[:,self._filterFunction(cells, cellVariables)]
        
        return cells
    
    def getSelectedCell(self, frame: int = None):
        """
        Get the cell data for the cell which is currently selected on the specified frame (uses the current frame if not specified).
        Will be None if no cell is selected.
        
            frame: int = currentFrame - the frame number to get the cells from
        
        """
        if self._selectedCell is None:
            return None
        
        return self.getCell(self._selectedCell, frame)
    
    @output.capture()
    def _onMouseDown(self, x: int, y: int):
        """
        Handle user mouse down action from ipyCanvas canvas
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        self._dragStartX = x
        self._dragStartY = y
        self._actionOriginX = x
        self._actionOriginY = y
        
        self.onMouseDown(x, y)
        
        if self.action == constants.SELECT_ACTION:
            self.selectCell(x, y)
        else:
            self._clicking = True
    
    def selectCell(self, x: int, y: int):
        """
        Select the cell at the given x and y coordinates.
        Abstract function, should be implemented by subclass.
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        pass
    
    def _onMouseUp(self, x: int, y: int):
        """
        Handle user mouse up action from ipyCanvas canvas
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        self._clicking = False
        self.onMouseUp(x, y)
    
    def _onMouseOut(self, x: int, y: int):
        """
        Handle user mouse out (mouse moves off the canvas) action from ipyCanvas canvas
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        self._clicking = False
        self.onMouseOut(x, y)
    
    @output.capture()
    def _onMouseMove(self, x: int, y: int):
        """
        Handle user mouse move action from ipyCanvas canvas
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas. 
                        The current X position of the mouse.
            y: int - the y position the mouse event occured based on the top left corner of the canvas.
                        The current y position of the mouse.
        
        """
        self.onMouseMove(x, y)
    
    def onMouseUp(self, x: int, y: int):
        """
        Handle a mouse up event at the given x and y coordinates.
        Abstract function, can be implemented by subclass.
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        pass

    def onMouseOut(self, x: int, y: int):
        """
        Handle a mouse out event at the given x and y coordinates.
        Abstract function, can be implemented by subclass.
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        pass
    
    def onMouseMove(self, x: int, y: int):
        """
        Handle a mouse move event at the given x and y coordinates.
        Abstract function, can be implemented by subclass.
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        pass
    
    def onMouseDown(self, x: int, y: int):
        """
        Handle a mouse down event at the given x and y coordinates.
        Abstract function, can be implemented by subclass.
        
            x: int - the x position the mouse event occured based on the top left corner of the canvas
            y: int - the y position the mouse event occured based on the top left corner of the canvas
        
        """
        pass
        
    def update(self):
        """
        Update UI, should be called after subclass updates. Puts shared data onto the canas.
        
        """
        canvas = self._canvas
        
        selectedCell = self.getSelectedCell()
        if selectedCell is not None:
            cellVaraibles = self.getCellVariables()
            
            canvas.fill_style = '#A0A0A0'
            canvas.font = '10px serif'
            
            
            identity = selectedCell[cellVaraibles["ID"]]
            volume = selectedCell[cellVaraibles["total_volume"]]
            phase = selectedCell[cellVaraibles["current_phase"]]
            
            canvas.fill_text(f"(ID: {identity}, Volume: {volume}, Phase: {phase})", 10, self._height - 10)
            
        self._updateCellPlot()
    
    def radiusOfCells(self, cells, variables):
        """
        Determines the radius of the cells based on the cell (3D) volume. Results in a numpy array.
        
            cells - the cells to get the radius of
            variables - the variables of the cells
        
        """
        return (cells[variables['total_volume']] * (3 / ( 4 * math.pi))) ** (1 / 3)
    
    def show(self):
        """
        Displays the widgets to the screen
        
        """
        display(self._canvas, self._buttons, self._frameSelector, self._environmentButtons, self._attributes, output)
        if self._cellFigure is None:
            global figureNumber
            fig, ax = plt.subplots()
            self._cellAx = ax
            self._cellFigure = fig
            figureNumber += 1
        plt.figure()
        self._generalGraph.plotPop()