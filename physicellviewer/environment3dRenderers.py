import vtk
import numpy as np
from vtk.util import numpy_support

def defaultEnvironment(environment, attribute):
    """
    Default 3d environment renderer. White is the highest value in the frame and black is the lowest value.
    """
    xbounds = environment.mesh.boundsX
    ybounds = environment.mesh.boundsY
    zbounds = environment.mesh.boundsZ

    attributeIndex = environment.current.variables[attribute]

    positions = environment.mesh.voxels
    data = environment.current.data[attributeIndex]

    xCount = np.unique(environment.mesh.voxels[environment.mesh.variables['x']]).shape[0]
    yCount = np.unique(environment.mesh.voxels[environment.mesh.variables['y']]).shape[0]
    zCount = np.unique(environment.mesh.voxels[environment.mesh.variables['z']]).shape[0]

    minimum = np.min(data)
    maximum = np.max(data)
    
    if not maximum == 0:
        data = data / maximum

    data = np.reshape(data, (xCount, yCount, zCount))

    imdata = vtk.vtkImageData()
    depthArray = numpy_support.numpy_to_vtk(data.ravel(), deep=True, array_type=vtk.VTK_DOUBLE)

    imdata.SetDimensions(data.shape)
    imdata.SetSpacing([(xbounds[1] - xbounds[0]) / xCount, (ybounds[1] - ybounds[0]) / yCount, (zbounds[1] - zbounds[0]) / zCount])
    imdata.SetOrigin([xbounds[0], ybounds[0], zbounds[0]])
    imdata.GetPointData().SetScalars(depthArray)

    colorFunc = vtk.vtkColorTransferFunction()
    colorFunc.AddRGBPoint(0.0, 0.0, 0.0, 0.0)
    colorFunc.AddRGBPoint(1.0, 1.0, 1.0, 1.0)

    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(0.0, 0.0)
    opacity.AddPoint(1, 0.8)

    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorFunc)
    volumeProperty.SetScalarOpacity(opacity)
    volumeProperty.SetInterpolationTypeToLinear()
    volumeProperty.SetIndependentComponents(2)

    volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
    volumeMapper.SetInputData(imdata)
    volumeMapper.SetBlendModeToMaximumIntensity()


    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)
    
    return volume