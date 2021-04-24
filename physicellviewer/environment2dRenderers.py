import numpy as np

def defaultRender2DEnvironment(attribute, environment, rRange=(0,255), gRange=(0,255), bRange=(0,255), aRange=(0, 255)):
    """
    Default 3d environment renderer. White is the highest value in the frame and black is the lowest value.
    """
    xCount = np.unique(environment.mesh.voxels[environment.mesh.variables['x']]).shape[0]
    yCount = np.unique(environment.mesh.voxels[environment.mesh.variables['y']]).shape[0]
    
    data = environment.current.data[environment.current.variables[attribute]]

    minimum = np.min(data)
    maximum = np.max(data)

    if maximum != 0:
        data = data / maximum

    shapedData = np.reshape(data, (xCount, yCount))

    image_data = np.stack((shapedData * (rRange[1] - rRange[0]) + rRange[0], shapedData * (gRange[1] - gRange[0]) + gRange[0], shapedData * (bRange[1] - bRange[0]) + bRange[0], shapedData * (aRange[1] - aRange[0]) + aRange[0]), axis=2)
    image_data = image_data.astype(dtype=np.int32)
    
    return image_data