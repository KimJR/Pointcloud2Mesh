import open3d as o3d
import numpy as np
import os

PATH = str(os.path.abspath(os.getcwd()))
FOLDER = "/src/"

"""
Pointcloud Object
    xyz: list -> x, y, z coordinates
    normals: list -> normals
    rgb: list -> colors
    invariants: list
    confidence: list
    intensity: list
    file: boolean
"""


class Pointcloud:
    PCD = "pcd"
    PLY = "ply"

    XYZ = ["x", "y", "z"]
    NORM_PLY = ["nx", "ny", "nz"]
    CONF = "confidence"
    INT = "intensity"
    NORM_PCD = ["normal_x", "normal_y", "normal_z"]
    RGB = "rgb"
    INV = ["j1", "j2", "j3"]

    def __init__(self, file):
        self.xyz = []  # pdc+ply
        self.normals = []  # pcd+ply
        self.rgb = []  # pcd+ply
        self.invariants = []  # pcd
        self.confidence = []  # ply
        self.intensity = []  # ply
        self.file = file

        self.o3d_obj = self.generate_o3d_obj()

        self.progress()

    def progress(self):

        if self.file.filetype == self.PCD:
            self.set_data_pcd()

        if self.file.filetype == self.PLY:
            self.set_data_ply()

        if self.file.visualize[0]:
            self.visualize_pcd()

    """
    Set data of ply file
      FIELDS x y z (data)
      FIELDS x y z rgb (color)
      FIELDS x y z normal_x normal_y normal_z (normals)
      FIELDS j1 j2 j3 (moment invariants)
    """
    def set_data_ply(self):

        if self.XYZ[0] and self.XYZ[1] and self.XYZ[2] in self.file.datatype:
            idx_x = self.file.datatype.index(self.XYZ[0])
            idx_y = self.file.datatype.index(self.XYZ[1])
            idx_z = self.file.datatype.index(self.XYZ[2])

            for row in self.file.data:
                self.xyz.append([row[idx_x], row[idx_y], row[idx_z]])

        if self.NORM_PLY[0] and self.NORM_PLY[1] and self.NORM_PLY[2] in self.file.datatype:
            idx_nx = self.file.datatype.index(self.NORM_PLY[0])
            idx_ny = self.file.datatype.index(self.NORM_PLY[1])
            idx_nz = self.file.datatype.index(self.NORM_PLY[2])

            for row in self.file.data:
                self.normals.append([row[idx_nx], row[idx_ny], row[idx_nz]])

        else:  # if no normals exist they are calculated
            self.o3d_obj.estimate_normals()
            normals = np.asarray(self.o3d_obj.normals)
            self.normals = normals.tolist()

        if self.CONF in self.file.datatype:
            idx_conf = self.file.datatype.index(self.CONF)
            for row in self.file.data:
                self.confidence.append(row[idx_conf])

        if self.INT in self.file.datatype:
            idx_int = self.file.datatype.index(self.INT)
            for row in self.file.data:
                self.intensity.append(row[idx_int])

    """
    Set data of pcd file
      FIELDS x y z (data)
      FIELDS x y z rgb (color)
      FIELDS x y z normal_x normal_y normal_z (normals)
      FIELDS j1 j2 j3 (moment invariants)
    """
    def set_data_pcd(self):

        if self.XYZ[0] and self.XYZ[1] and self.XYZ[2] in self.file.datatype:
            idx_x = self.file.datatype.index(self.XYZ[0])
            idx_y = self.file.datatype.index(self.XYZ[1])
            idx_z = self.file.datatype.index(self.XYZ[2])
            for row in self.file.data:
                self.xyz.append([row[idx_x], row[idx_y], row[idx_z]])

        if self.RGB in self.file.datatype:
            index = self.file.datatype.index(self.RGB)
            for row in self.file.data:
                self.rgb.append(row[index])

        if self.NORM_PCD[0] and self.NORM_PCD[1] and self.NORM_PCD[2] in self.file.datatype:
            idx_nx = self.file.datatype.index(self.NORM_PCD[0])
            idx_ny = self.file.datatype.index(self.NORM_PCD[1])
            idx_nz = self.file.datatype.index(self.NORM_PCD[2])
            for row in self.file.data:
                self.normals.append([row[idx_nx], row[idx_ny], row[idx_nz]])
        else:  # if no normals exist they are calculated
            self.o3d_obj.estimate_normals()
            normals = np.asarray(self.o3d_obj.normals)
            self.normals = normals.tolist()

        if self.INV[0] and self.INV[1] and self.INV[2] in self.file.datatype:
            idx_j1 = self.file.datatype.index(self.INV[0])
            idx_j2 = self.file.datatype.index(self.INV[1])
            idx_j3 = self.file.datatype.index(self.INV[2])
            for row in self.file.data:
                self.invariants.append([row[idx_j1], row[idx_j2], row[idx_j3]])

    """
    returns x coords
    """
    def get_x(self):
        data = list(map(list, zip(*self.xyz)))
        x = data[0]
        return x

    """
    returns y coords
    """
    def get_y(self):
        data = list(map(list, zip(*self.xyz)))
        y = data[1]
        return y

    """
    returns z coords
    """
    def get_z(self):
        data = list(map(list, zip(*self.xyz)))
        z = data[2]
        return z

    """
    generate open3d object
    """
    def generate_o3d_obj(self):
        o3d_obj = o3d.io.read_point_cloud(self.file.PATH + self.file.filename)
        return o3d_obj

    """
    visualize the pointcloud as o3d object
    """
    def visualize_pcd(self):
        o3d.visualization.draw_geometries([self.o3d_obj], point_show_normal=self.file.visualize[1])
