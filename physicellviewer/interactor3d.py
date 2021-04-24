from .interactorBase import Interactor
from .Parser import Parser
from .cell3dColorMaps import defaultColorMap3d
from .environment3dRenderers import defaultEnvironment
from .utils import debounce, output
from ipywidgets import Image
from . import constants

import math
import numpy as np
import vtk

class Interactor3D(Interactor):
    def __init__(self, parser: Parser, width: int = 500, height: int = 400, colorMap = defaultColorMap3d, filterFunction = None, environmentRenderer = defaultEnvironment):
        """
        Visualize a 3D PhysiCell simulation
        
            parser: Parser - a simulation output parser
            width: int = 500 - the width of the canvas to draw to
            height: int = 400 - the height of the canvas to draw to
            colorMap: (cells: numpyArray, variables: Map<string, indicies>, selectedCellID: ?string) => Tuple<vtkFloatArray, vtkColorTransferFunction> = defaultColorMap3d - a function resulting in the cell colors
            filterFunction: (cells: numpyArray, variables: Map<string, indicies>) => numpyArray (boolean/indicies) = None - a function resulting in an array of the indicies of the cells to draw
            environmentRenderer: (attribute: string, environment: Parser.Environment) => vtkVolume = defaultEnvironment - given an environment and the attribute to render, create an image (numpy array) to render (will span the bounds of the attribute)
        
        """
        super().__init__(parser, width, height, colorMap, filterFunction, (constants.MOVE_ACTION, constants.ZOOM_ACTION, constants.ROTATE_ACTION, constants.SELECT_ACTION))
        
        self._previousFrameNumber = None
        self._previouslySelectedCell = None
        self._environmentRenderer = environmentRenderer
        self._colorMap = colorMap
        
        self.renderer = vtk.vtkRenderer()
        
        self.create(self._currentFrame)
        
        renderWindow = vtk.vtkRenderWindow()
        renderWindow.SetOffScreenRendering(1)
        renderWindow.AddRenderer(self.renderer)
        renderWindow.SetSize(width, height)
        renderWindow.Render()
        
        self.renderWindow = renderWindow
        
        self.update()
    
    def drawCells(self, frame=None):
        """
        Adds the cells to the renderer to draw
        
            frame - the frame (Frame) to draw the cells for
        """
        cells = self.getCellsToRender(frame.frameNumber)
        variables = self.getCellVariables(frame.frameNumber)
        
        x = variables["position.x"]
        y = variables["position.y"]
        z = variables["position.z"]
        r = self.radiusOfCells(cells, variables)
        
        data = vtk.vtkPolyData()
        points = vtk.vtkPoints()
        radii = vtk.vtkFloatArray()
        radii.SetName("radius")
        
        colors, lookupTable = self._colorMap(cells, variables, self._selectedCell)
        colors.SetName("color")
        
        for cell in range(cells.shape[1]):
            points.InsertNextPoint(cells[x,cell], cells[y, cell], cells[z, cell])
            radii.InsertNextValue(float(r[cell]))
        
        data.SetPoints(points)
        data.GetPointData().AddArray(radii)
        data.GetPointData().AddArray(colors)
        data.GetPointData().SetActiveScalars("color")
        
        # Source - ball
        ball = vtk.vtkSphereSource()
        ball.SetRadius(1)
        ball.SetThetaResolution(8)
        ball.SetPhiResolution(8)
        
        # Glyph - ball
        ballGlyph = vtk.vtkGlyph3D()
        ballGlyph.SetInputData(data)
        ballGlyph.SetScaleFactor(1)
        ballGlyph.ClampingOff()
        ballGlyph.SetColorModeToColorByScalar()
        ballGlyph.SetSourceConnection(ball.GetOutputPort())
        ballGlyph.SetInputArrayToProcess(0,0,0,0,'radius')
        ballGlyph.SetInputArrayToProcess(3,0,0,0,'color')
        
        # Mapper - ball
        ballMapper = vtk.vtkPolyDataMapper()
        ballMapper.SetInputData(data)
        ballMapper.SetInputConnection(ballGlyph.GetOutputPort())
        ballMapper.ScalarVisibilityOn()
        ballMapper.SetScalarModeToUsePointData()
        ballMapper.SelectColorArray("color")
        ballMapper.SetLookupTable(lookupTable)
        
        # Actor - ball
        ballActor = vtk.vtkActor()
        ballActor.SetMapper(ballMapper)
        
        self.renderer.AddActor(ballActor)
        
    
    def create(self, frameNumber: int):
        """
        Create and add the actors to the renderer to render the given frame. Will do nothing if nothing has changed.
        
            frameNumber - the frame to render
        """
        if frameNumber == self._previousFrameNumber and self._selectedCell == self._previouslySelectedCell and self._previousFilterFunction == self._filterFunction and self._previouslyVisible == self._visible:
            return
        
        self._previouslySelectedCell = self._selectedCell
        self._previousFrameNumber = frameNumber
        self._previousFilterFunction = self._filterFunction
        self._previouslyVisible = self._visible
        
        frame = self._parser.getFrame(frameNumber)
        
        self.renderer.RemoveAllViewProps()
        
        shouldDrawCells = False
        for element in self._visible:
            if element == constants.VISIBLE_CELL:
                shouldDrawCells = True
                continue
            self.renderer.AddVolume(self._environmentRenderer(frame.environment, element))
        
        if shouldDrawCells:
            self.drawCells(frame)
        
        self.renderer.ResetCameraClippingRange()
        
        
        
    def update(self):
        """
        Update the canvas with a new image.
        """
        canvas = self._canvas
        
        self.create(self._currentFrame)
        
        self.renderWindow.Render()
        
        windowToImageFilter = vtk.vtkWindowToImageFilter()
        windowToImageFilter.SetInput(self.renderWindow)
        windowToImageFilter.Update()

        writer = vtk.vtkPNGWriter()
        writer.SetWriteToMemory(1)
        writer.SetInputConnection(windowToImageFilter.GetOutputPort())
        writer.Write()
        
        data = memoryview(writer.GetResult()).tobytes()
        
        image = Image(value=data)
        
        canvas.draw_image(image)
        
        super().update()
        
        
    
    @output.capture()
    @debounce(0.1)
    def onMouseMove(self, x: int, y: int):
        """
        Handle a mouse move event.
        
        """
        if self._clicking:
            if self.action == constants.MOVE_ACTION:
                self.pan(x, y)
            elif self.action == constants.ZOOM_ACTION:
                self.renderer.GetActiveCamera().Zoom(1 + (self._actionOriginY - y) / 100)
            elif self.action == constants.ROTATE_ACTION:
                self.rotate(x, y)
                
            self._dragStartX = x
            self._dragStartY = y
            self.update()
    
    def pan(self, x: float, y: float):
        """
        Handle a pan action. Pans from the mouse down event to the current x, y coordinates.
        Addapted from:
        
           https://compucell3d.org/BinDoc/cc3d_binaries/dependencies/windows/MinGW/dependencies_qt_4.8.4_pyqt_4.9.6_vtk_5.10.1_python27/Player/vtk/wx/wxVTKRenderWindow.py 
        
        """
        renderer = self.renderer
        camera = renderer.GetActiveCamera()
        (pPoint0,pPoint1,pPoint2) = camera.GetPosition()
        (fPoint0,fPoint1,fPoint2) = camera.GetFocalPoint()

        renderer.SetWorldPoint(fPoint0,fPoint1,fPoint2,1.0)
        renderer.WorldToDisplay()
        # Convert world point coordinates to display coordinates
        dPoint = renderer.GetDisplayPoint()
        focalDepth = dPoint[2]

        aPoint0 = self._width / 2 + (x - self._dragStartX)
        aPoint1 = self._height / 2 - (y - self._dragStartY)

        renderer.SetDisplayPoint(aPoint0,aPoint1,focalDepth)
        renderer.DisplayToWorld()

        (rPoint0,rPoint1,rPoint2,rPoint3) = renderer.GetWorldPoint()
        if (rPoint3 != 0.0):
            rPoint0 = rPoint0/rPoint3
            rPoint1 = rPoint1/rPoint3
            rPoint2 = rPoint2/rPoint3

        camera.SetFocalPoint((fPoint0 - rPoint0) + fPoint0,
                             (fPoint1 - rPoint1) + fPoint1,
                             (fPoint2 - rPoint2) + fPoint2)

        camera.SetPosition((fPoint0 - rPoint0) + pPoint0,
                           (fPoint1 - rPoint1) + pPoint1,
                           (fPoint2 - rPoint2) + pPoint2)
        
    def rotate(self, x: float, y: float):
        """
        Handle a rotate action. Rotates from the mouse down event to the current x, y coordinates.
        Addapted from:
        
           https://compucell3d.org/BinDoc/cc3d_binaries/dependencies/windows/MinGW/dependencies_qt_4.8.4_pyqt_4.9.6_vtk_5.10.1_python27/Player/vtk/wx/wxVTKRenderWindow.py 
        
        """
        renderer = self.renderer
        camera = renderer.GetActiveCamera()
        camera.Azimuth(self._dragStartX - x)
        camera.Elevation(y - self._dragStartY)
        camera.OrthogonalizeViewUp()

        renderer.ResetCameraClippingRange()
    
    def zoom(self, x: float, y: float):
        """
        Handle a zoom action. Zooms from the mouse down event to the current x, y coordinates.
        Addapted from:
        
           https://compucell3d.org/BinDoc/cc3d_binaries/dependencies/windows/MinGW/dependencies_qt_4.8.4_pyqt_4.9.6_vtk_5.10.1_python27/Player/vtk/wx/wxVTKRenderWindow.py 
        
        """
        
        renderer = self.renderer
        camera = renderer.GetActiveCamera()

        zoomFactor = math.pow(1.02,(0.5*(self._dragStartY - y)))
        self._CurrentZoom = self._CurrentZoom * zoomFactor

        if camera.GetParallelProjection():
            parallelScale = camera.GetParallelScale()/zoomFactor
            camera.SetParallelScale(parallelScale)
        else:
            camera.Dolly(zoomFactor)
            renderer.ResetCameraClippingRange()

        self._dragStartX = x
        self._dragStartY = y

        self.Render()
    
    @output.capture()
    def selectCell(self, x: float, y: float):
        """
        Select a cell based on the x, y position clicked on the canvas.
        
        """
        picker = vtk.vtkPropPicker()
        picker.Pick(x, self._height - y, 0, self.renderer)

        # get the new
        self.NewPickedActor = picker.GetActor()
        
        position = picker.GetPickPosition()
        
        if not picker.GetActor():
            self._selectedCell = None
            self.update()
            return
        
        x, y, z = picker.GetPickPosition()
            
        cells = self.getCellsToRender()
        cellVariables = self.getCellVariables()
        
        distances = np.sqrt(np.square(x - cells[cellVariables['position.x']]) + np.square(y - cells[cellVariables['position.y']]) + np.square(z - cells[cellVariables['position.z']])) - self.radiusOfCells(cells, cellVariables)
        minIndex = np.argmin(distances)
        
        if distances[minIndex] <= 0:
            self._selectedCell = cells[cellVariables['ID'], minIndex]
            
        self.update()