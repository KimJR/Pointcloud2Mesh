import open3d as o3d
import open3d.visualization.gui as gui
import os
import trimesh
import xatlas


def run_xatlas(self, input_file):
    # v <float X> <float Y> <float Z> [ <float W> ] Beschreibung eines Eckpunktes (engl. vertex).
    #  v 1.000000 1.000000 -0.999999
    # vt <float X> <float Y> Beschreibung eines Texturkoordinatenpunktes.
    # vt 0.500000 0.500000
    # f <integer A_V> / <integer A_VT> <integer B_V> / ...
    # Beschreibung einer Fläche. (Möglichkeit 2 – anhand von Eckpunkten und Texturkoordinaten)
    # f 2 / 1 3 / 1 4 / 1

    mesh = trimesh.load_mesh(str(input_file)+".ply")

    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

    xatlas.export(str(input_file)+".obj", mesh.vertices[vmapping], indices, uvs)