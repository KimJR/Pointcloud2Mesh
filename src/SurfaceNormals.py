# Estimate the surface normals of PointCloud (Surface Normals)
# There are 3 ways
#  1. K-nearest neighbor calculation normal vector
#  2. Radius neighbor calculation normal vector
#  3. Integral image for normal estimation (Normal Estimation Using Integral Images) to calculate the normal vecto

import pyvista as pv


# FROM PyVista
original_point_cloud = pv.read("../pcd/StanfordBunny.ply")
print(original_point_cloud.active_normals)
print(original_point_cloud.plot)

# def get_normals(path):
#
#     cloud = pcl.load(path)
#     feature = cloud.make_NormalEstimation #pcl.features.NormalEstimation
#     feature.set_Radiussearch(0.1)
#     feature.set_KSearch(3)
#     normals = feature.compute()
#
#     return normals
#
# normals = get_normals("/pcd/test.pcd")





#
#
# def compute_normals(cloud,
#                     radius=None,
#                     k=None,
#                     indices=None,
#                     num_threads=1,
#                     output_cloud=None,
#                     search_surface=None,
# ):
#     """
#     Compute normals for a point cloud
#     :param cloud: input point cloud
#     :param radius: radius search distance
#     :param k: use k nearest neighbors
#     :param indices: optional indices of the input cloud to use
#     :param num_threads: number of threads to do the computation
#     :param output_cloud: optional point cloud to compute the normals into
#     :param search_surface: optional point cloud search surface
#     :return: a point cloud with normals
#     """
#     if num_threads == 1:
#         normals_estimation = getattr(pcl.features.NormalEstimation, pc_type)()
#     else:
#         normals_estimation = getattr(pcl.features.NormalEstimationOMP, pc_type)(num_threads)
#     normals_estimation.setInputCloud(cloud)
#     if radius is not None:
#         normals_estimation.setRadiusSearch(radius)
#     if k is not None:
#         normals_estimation.setKSearch(k)
#     if indices is not None:
#         normals_estimation.setIndices(indices)
#     if search_surface is not None:
#         normals_estimation.setSearchSurface(search_surface)
#
#     normals_estimation.compute(output_cloud)
#     return output_cloud