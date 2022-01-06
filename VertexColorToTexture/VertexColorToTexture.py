import os.path

import numpy as np
import vectormath
import pymesh
from numba import njit, prange
from PIL import Image


def get_texture_from_vertex_color(input_file: str, textureWidth: int = 1024):
    '''
    Generate the texture from colors of vertices.
    :param input_file: the name of the input file, must not be None or empty.
           The object file includes an array of all faces (triangles). Each triangle includes an array of 3 vertices
    :return: the texture
    '''

    # vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
    # xatlas.export(str(input_file)+".obj", mesh.vertices[vmapping], indices, uvs)

    filename, filetype = os.path.splitext(input_file)
    if not filetype.lower() == ".obj":
        print(".obj-File was expected for texture generation")
        return
    mesh = pymesh.load_mesh(input_file)
    mesh, info = pymesh.remove_isolated_vertices(mesh)  # remove vertices that are not part of any face or voxel
    vertices = mesh.vertices
    number_of_vertices = len(vertices)

    # accessing vertex and face information:
    ### COLOR
    mesh.add_attribute("vertex_color")
    color_map = mesh.get_vertex_attribute("vertex_color")    # contains the color per vertex
    if color_map.size == 0:
        color_map = np.zeros([number_of_vertices, 3], dtype=int)  # because its read only.
        # fill with random color:
        for i in range(number_of_vertices):
            color_map[i] = np.random.choice(256, size=3)

    ### NORMAL
    mesh.add_attribute("vertex_normal")
    normal_map = mesh.get_vertex_attribute("vertex_normal")  # contains normal vertices

    ### UV COORDINATES (of Vertices)
    uv_coordinates = get_uv_coordinates(input_file, number_of_vertices)

    # process faces
    faces = mesh.faces
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
        sqxStart = int(min(x1, x2, x3)*textureWidth)
        sqxEnd = int(max(x1, x2, x3)*textureWidth)
        sqyStart = int(min(y1, y2, y3)*textureWidth)
        sqyEnd = int(max(y1, y2, y3)*textureWidth)

        xDim = range(sqxStart, sqxEnd)
        yDim = range(sqyStart, sqyEnd)
        sqrShape = (len(xDim), len(yDim), 3)  # last dimension is for color channels
        print(sqrShape)
        ### INIT storing arrays
        pixel_colors = np.zeros(sqrShape, dtype=np.uint8)         # the texture to which the color will be mapped
        normal_pixel_colors = np.zeros(sqrShape, dtype=np.uint8)  # the texture to which the normal color will be mapped
        position_map = np.zeros(sqrShape, dtype=np.uint8)         # the texture to which the position of the vertices will be mapped


        # TODO  parallelize: buffer texture -> join those
        # cycle through each pixel within the square to see if the pixel is within the triangle
        for y in yDim:
            for x in xDim:
                print("POINT: ", x, " ", y)

                xNorm = x / textureWidth  # x normalized to value between 0 and 1 (easier to calculate)
                yNorm = y / textureWidth  # y normalized to value between 0 and 1 (easier to calculate)

                # get factors a, b, c such that
                # x = a * x1 + b * x2  + c * x3 --> x - c*x3 - b*x2 = a*x1 --> (x - c*x3 - b*x2)/x1 = a
                # y = a * y1 + b * y2 + c * y3 --> (y - c*y3 - a*y1)/y2 = b
                #                              --> ((x - c*x3 - ((y - c*y3 - a*y1)/y2)*x2)/x1 = a
                # a + b + c = 1
                a = ((y2 - y3) * (xNorm - x3) + (x3 - x2) * (yNorm - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
                b = ((y3 - y1) * (xNorm - x3) + (x1 - x3) * (yNorm - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
                #a = ((x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)) # https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
                #b = ((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1))
                c = 1 - a - b

                print(a, " ", b, " ", c)
                # check if point is within triangle
                if 0 <= a and 0 <= b and 0 <= c and (a + b + c) <= 1:
                    print("yes, pixel is inside mesh", color_map[v0], " ", color_map[v1], " ", color_map[v2])
                    # color the pixel depending on the lerp between the three pixels
                    pixelColor = a * color_map[v0] + b * color_map[v1] + c * color_map[v2]
                    print("pixelColor= ", pixelColor, " size=", len(pixelColor), " shape pixel_Colors: ", pixel_colors.shape, x - sqxStart, y - sqyStart)
                    x_i = x - sqxStart
                    y_i = y - sqyStart

                    pixel_colors[x_i, y_i] = pixelColor
                    #  TODO write in hdr,
                    pixelNormalColor = (a * normal_map[v0] + b * normal_map[v1] + c * normal_map[v2]) / 2 + vectormath.Vector3(0.5,
                                                                                                                0.5,
                                                                                                                0.5)
                    normal_pixel_colors[x_i, y_i] = pixelNormalColor

                    pixelPositionColor = (a * vertices[v0] + b * vertices[v1] + c * vertices[v2])
                    position_map[x_i, y_i] = pixelPositionColor
                    # TODO store as png with numpy, imageIo
                    im = Image.fromarray(position_map)
                    print(im)
                    im.save("./VertexColorToTexture/texture/texture_map-face{}.png".format(i))


def get_uv_coordinates(filepath, number_of_vertices):
    '''
    Parse the provided obj. file at location filepath to derive the uv coordinates.
    :param filepath: the path where the obj file to be parsed is stored
    :param number_of_vertices: the number of vertices specified in the file and therefore
           the number of u,v pairs to be returned
    :return: a matrix of [shape number_of_vertices, 2] or [number_of_vertices, 3]
             depending on whether only u and v or also w values are specified in the given file.
    '''

    filename, filetype = os.path.splitext(filepath)
    if not filetype.lower() == ".obj":
        print(".obj-File was expected for texture generation")
        return

    # init
    uv_coordinates = None
    position = 0
    values_per_vertex = 0

    # reading the file
    obj_file = open(filepath, "r")
    nextline = obj_file.readline()
    # print("start reading file..")
    while nextline:
        if nextline.startswith("vt"):
            # this is a line describing vertex texture --> uv coordinates
            coords = nextline.split(" ", 4)  # expect 3 parts: vt <u-value> <v-value> but w value could also exist
            number_of_uv_values = len(coords) - 1
            if number_of_uv_values is not values_per_vertex:
                if values_per_vertex == 0:
                    values_per_vertex = number_of_uv_values
                    uv_coordinates = np.zeros([number_of_vertices, values_per_vertex])
                else:
                    print("File ", filepath, " seems to specify uv coordinates of different length...")
                    print("Previous length was ", values_per_vertex,
                          ", now {} values were detected.".format(number_of_uv_values))
                    return

            for c_part in coords:
                try:
                    uv_value = float(c_part)
                    uv_coordinates.put(position, uv_value)
                    position += 1
                except:
                    # c_part was "vt" part
                    continue
        nextline = obj_file.readline()
    return uv_coordinates


if __name__ == "__main__":
    get_texture_from_vertex_color(os.getcwd() + "/models/mesh.obj")
