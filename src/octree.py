from pyoctree import pyoctree as ot
import numpy as np

"""
1. Creating the octree representation of a 3D triangular mesh model
- pointCoords is a Nx3 numpy array of floats(dtype=float) representing the 3D coordinates of the mesh 
- points connectivity is a Nx3 numpy array of integers(dtype=np.int32) representing the point connectivity of each tri element in the mesh
"""
pointCoords = np.array([[0.2, 0.3, 0.5], [0.2, 0.3, 0.5], [0.2, 0.3, 0.5]])
connectivity = np.array([[1, 2, 3], [1, 2, 3], [1, 2, 3]])

tree = ot.PyOctree(pointCoords, connectivity)

"""
2. Finding intersection between mesh object and ray
"""
startPoint = [0.0, 0.0, 0.0]
endPoint = [0.0, 0.0, 1.0]
rayList = np.array([[startPoint, endPoint]], dtype=np.float32)
intersectionFound = tree.rayIntersection(rayList)

print(intersectionFound)