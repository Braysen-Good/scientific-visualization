import xml.etree.ElementTree as ET
from os import path
import scipy.io

import itertools

from typing import Dict, Callable, Tuple, List

import math

def doesCoordinateVary(coordinateNode):
    return len(coordinateNode.text.split(coordinateNode.attrib['delimiter'])) > 1

class Mesh:
    """
    Mesh - the deminsionalty of the environment
    
    +boundX - the minimum and maximum x bounds of the environment
    +boundy - the minimum and maximum y bounds of the environment
    +boundz - the minimum and maximum z bounds of the environment
    
    +voxels - the voxels which represent the environment
    
    +varaibles - the position of each variable in the voxels
    
    +is2D - true if there are only 2 dimensions which take more than one value
    """
    def __init__(self, filePath: str, meshXMLNode):
        if not ( meshXMLNode.attrib['type'] == 'Cartesian' and meshXMLNode.attrib['uniform'] == 'true'):
            raise ValueError("Only knows how to create environments for uniform cartesian meshes")
            
        bounds = meshXMLNode.find('bounding_box').text.split(" ")
        
        self.boundsX = (float(bounds[0]), float(bounds[3])) 
        self.boundsY = (float(bounds[1]), float(bounds[4]))
        self.boundsZ = (float(bounds[2]), float(bounds[5]))
        
        self.voxels = scipy.io.loadmat(filePath + meshXMLNode.find('voxels/filename').text)['mesh']
        
        self.variables = {
            'x': 0,
            'y': 1,
            'z': 2,
            'volume': 3,
        }
        
        self.is2D = not ( doesCoordinateVary(meshXMLNode.find('x_coordinates')) and doesCoordinateVary(meshXMLNode.find('y_coordinates')) and doesCoordinateVary(meshXMLNode.find('z_coordinates')))

class CurrentEnvironment:
    """
    CurrentEnvironment - the current environment values in the frame
    
    +data - data about each voxel in the current frame
    +variables - a mapping of a cell's attribute name to its position in the data array
    """
    def __init__(self, filePath: str, fileName: str, variablesNode):
        self.file = filePath + fileName
        if not path.isfile(self.file):
            raise Exception(f"environment file '{self.file}' was not found")
        
        self.data = scipy.io.loadmat(self.file)['multiscale_microenvironment']
        
        self.variables = {
            'x': 0,
            'y': 1,
            'z': 2,
            'volume': 3,
        }
        self.attributes = []
        baseOffest = 4 #x, y, z, volume
        for child in variablesNode:
            var = child.attrib
            self.attributes.append(var['name'])
            self.variables[var['name']] = int(var['ID']) + baseOffest
        

class Environment:
    """
    Environment - holds the data of the environment
    
    +mesh - data about the mesh that makes up the enviroment
    +current - data about the current state of the environment
    +is2D - true if it the enviroment is in a 2d plane
    """
    def __init__(self, filePath: str, domainNode):
        self.mesh = Mesh(filePath, domainNode.find('mesh'))
        self.is2D = self.mesh.is2D
        self.current = CurrentEnvironment(filePath, domainNode.find('data/filename').text, domainNode.find('variables'))

class Cells:
    """
    Cells - data about the cells in the current frame
    
    +data - an array representing the cell states in the current frame
    +varaibles - a mapping of cell attribute names to array index
    """
    def __init__(self, filePath: str, cellNode):
        variables = {}
        dimensions = [(0, 'x'), (1, 'y'), (2, 'z')]
        for child in cellNode.find('labels'):
            name = child.text
            size = int(child.attrib['size'])
            index = int(child.attrib['index'])
            if size == len(dimensions):
                for offset, dimension in dimensions:
                    variables[f"{name}.{dimension}"] = index + offset
            elif size > 1:
                for offset in range(size):
                    variables[f"{name}.{str(i)}"] = index + offset
            else:
                variables[name] = index
        
        self.variables = variables
        
        self.data = scipy.io.loadmat(filePath + cellNode.find('filename').text)['cells']
            


class Frame:
    """
    Frame - holds data about each frame
    
    +timestamp - the number of minutes since the begining of the simulation
    +environment - data about the environment at the current frame
    +cells - data about the cell states at the current frame
    """
    def __init__(self, filePath: str, fileName: str, frameNumber: int):
        self.file = filePath + fileName
        
        if not path.isfile(self.file):
            raise Exception(f"file '{self.file}' was not found for frame {str(frameNumber)}")
        
        self.xmlTree = ET.parse(self.file)
        self.xmlRoot = self.xmlTree.getroot()
        
        self.timestamp = float(self.xmlRoot.find('metadata/current_time').text) # minutes in simulation
        
        self.environment = Environment(filePath, self.xmlRoot.find("microenvironment/domain"))
        
        self.cells = Cells(filePath, self.xmlRoot.find("cellular_information/cell_populations/cell_population/custom/simplified_data[@source='PhysiCell']"))
        

class FrameManager:
    """
    FrameManager - manages frame data
    
    +getFrameCount - get the number of frames in the simulation output
    +getFrameRange - get the frameNumber range [min, max)
    +getFrame(frameNumber) - get the frame by the frameNumber
    """
    def __init__(self, outputPath: str, fileFinder: Callable[[int], str] = lambda frameCount: f"output{str(frameCount).rjust(8, '0')}.xml", startingFrame: int = 0):
        self._frames: Dict[int, Frame] = {}
        self._fileFinder: Callable[[int], str] = fileFinder
        self._startingFrame: int = startingFrame # the starting frame number (inclusive)
        
        if len(outputPath) == 0:
            outputPath = path.sep
        elif outputPath[-1] != path.sep:
            outputPath += path.sep
        
        self._path = outputPath
        
        i = 0
        for frame in itertools.count(start=int(startingFrame)):
            if not path.isfile(outputPath + fileFinder(frame)):
                self._endingFrame = frame # the endingFrame number (none-inclusive)
                break
        
        if self._startingFrame == self._endingFrame:
            raise Exception(f"Could not find any output files within the given path {path}")
    
    def getFrameCount(self) -> int:
        return self._endingFrame - self._startingFrame
    
    def getFrameRange(self) -> Tuple[int, int]:
        return (self._startingFrame, self._endingFrame)
    
    def getFrame(self, frameNumber: int):
        frameNumber = int(frameNumber)
        if frameNumber < self._startingFrame or frameNumber >= self._endingFrame:
            raise IndexError(f"could only find frames ${str(self._startingFrame)} (inclusive) to ${str(self._endingFrame)} (exclusive), ${str(frameNumber)} does not exist in that range.")
        if not frameNumber in self._frames:
            self._frames[frameNumber] = Frame(self._path, self._fileFinder(frameNumber), frameNumber)
        
        return self._frames[frameNumber]

def Parser(outputPath: str):
    """
    Parser - get the parser for the given simulation output path
    """
    return FrameManager(outputPath)
