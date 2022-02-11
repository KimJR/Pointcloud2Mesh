import os.path
#import numba
#from numba import jit, njit, prange
import numpy as np
import vectormath
import trimesh
from trimesh import visual
from trimesh import base
import xatlas
from PIL import Image


def get_texture_from_vertex_color(input_file: str, textureWidth: int = 1024):
    '''
    Generate the texture from colors of vertices.
    :param input_file: the name of the input file, must not be None or empty. Should not include the file type '.obj'
           The object file includes an array of all faces (triangles). Each triangle includes an array of 3 vertices
    :return: the texture
    '''

    mesh = trimesh.load(input_file + ".ply")
    print("starting xatlas unwrap!")
    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
    print("Finished xatlas unwrap!")

    # accessing vertex and face information from original file:
    vertices = mesh.vertices
    vertex_colors = mesh.visual.vertex_colors # contains the color per vertex before xatlas conversion
    vertex_normals = mesh.vertex_normals  # contains normal vertices

    new_vertices = [0]*len(uvs) # vertices after xatlas conversion
    new_colors = [0]*len(uvs) # contains the color of each vertex after xatlas conversion (after generating UVs)
    new_normals = [0]*len(uvs) # contains the normals of each vertex after xatlas conversion (after generating UVs)
    for i in range(0, len(uvs)):
        new_vertices[i] = vertices[vmapping[i]]
        new_colors[i] = vertex_colors[vmapping[i]]
        new_normals[i] = vertex_normals[vmapping[i]]

    ### UV COORDINATES (of Vertices)
    pixel_color_array = create_texture(new_vertices, indices, textureWidth, uvs, new_colors, new_normals)

#@jit(nopython=True, cache=True, parallel=True)
def create_texture(new_vertices, faces, textureWidth, uv_coordinates, new_colors, new_normals):
    ### INIT storing arrays
    textureShape = (textureWidth, textureWidth, 3)
    pixel_color_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the color will be mapped
    pixel_normal_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the normal color will be mapped
    pixel_position_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the position of the vertices will be mapped

    position_color_range = 100 # TODO this should be 255 divided by the highest length of the mesh's bounding box. 

    # process faces
    for i in range(0, len(faces)):
        face = faces[i]
        # get indices of vertices 0, 1 and 2 which are defining the face
        v0 = face[0]
        v1 = face[1]
        v2 = face[2]

        x1 = uv_coordinates[v0, 0]  # possibly several u values --> TODO how would this look like then?
        y1 = uv_coordinates[v0, 1]
        x2 = uv_coordinates[v1, 0]
        y2 = uv_coordinates[v1, 1]
        x3 = uv_coordinates[v2, 0]
        y3 = uv_coordinates[v2, 1]

        # get smallest square of pixels that includes all three vertex positions
        sqxStart = int(min(x1, x2, x3) * textureWidth)
        sqxEnd = int(max(x1, x2, x3) * textureWidth)
        sqyStart = int(min(y1, y2, y3) * textureWidth)
        sqyEnd = int(max(y1, y2, y3) * textureWidth)

        # TODO  parallelize: buffer texture -> join those
        # cycle through each pixel within the square to see if the pixel is within the triangle
        for y in range(sqyStart, sqyEnd):
            for x in range(sqxStart, sqxEnd):
                #print("POINT: ", x, " ", y)

                xNorm = x / textureWidth  # x normalized to value between 0 and 1 (easier to calculate)
                yNorm = y / textureWidth  # y normalized to value between 0 and 1 (easier to calculate)

                # get factors a, b, c such that
                # x = a * x1 + b * x2  + c * x3 --> x - c*x3 - b*x2 = a*x1 --> (x - c*x3 - b*x2)/x1 = a
                # y = a * y1 + b * y2 + c * y3 --> (y - c*y3 - a*y1)/y2 = b
                #                              --> ((x - c*x3 - ((y - c*y3 - a*y1)/y2)*x2)/x1 = a
                # a + b + c = 1
                a = ((y2 - y3) * (xNorm - x3) + (x3 - x2) * (yNorm - y3)) / (
                           (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
                b = ((y3 - y1) * (xNorm - x3) + (x1 - x3) * (yNorm - y3)) / (
                           (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
                #a = ((x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)) # https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
                #b = ((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1))
                c = 1 - a - b

                #print(a, " ", b, " ", c)
                # check if point is within triangle
                if 0 <= a and 0 <= b and 0 <= c and (a + b + c) <= 1:
                    # color the pixel depending on the lerp between the three pixels
                    # new_colors might has shape of (lenOfVertices, 4) if it stores RGBA values --> only use RGB
                    pixel_color = a * new_colors[v0][:3] + b * new_colors[v1][:3] + c * new_colors[v2][:3]
                    # print("pixel_color= ", pixel_color)
                    pixel_color_array[x, y] = pixel_color
                    #  TODO write in hdr,
                    normal_color = (a * new_normals[v0] + b * new_normals[v1] + c * new_normals[v2])/2
                    pixel_normal_color = [int(255*(normal_color[0] + 0.5)), int(255*(normal_color[1] + 0.5)), int(255*(normal_color[2] + 0.5))]
                    pixel_normal_array[x_i, y_i] = pixel_normal_color

                    pixel_position_color = position_color_range * a * new_vertices[v0] + position_color_range * b * new_vertices[v1] + position_color_range * c * new_vertices[v2]
                    pixel_position_array[x, y] = pixel_position_color
        print(str(i) + ") - uvs: " + str([x1, y1]) + ", color: " + str(pixel_color) + ", pixel: (" + str(x) + ", " + str(y) + ")")
    # TODO store as png with numpy, imageIo
    im = Image.fromarray(pixel_color_array)
    im.save(os.getcwd() + "\\VertexColorToTexture\\texture\\texture_map.png")

    im_n = Image.fromarray(pixel_normal_array)
    im_n.save(os.getcwd() + "\\VertexColorToTexture\\texture\\normal_map.png")

    im_p = Image.fromarray(pixel_position_array)
    im_p.save(os.getcwd() + "\\VertexColorToTexture\\texture\\position_map.png")
    
    return pixel_color_array

#get_texture_from_vertex_color("C:\\Users\\Alexander\\Documents\\GitHub\\Pointcloud2Mesh\\models\\color_to_uv_index_testfiles\\meshAfterPoisson")

if __name__ == "__main__":
    get_texture_from_vertex_color(os.getcwd() + "/models/mesh")
