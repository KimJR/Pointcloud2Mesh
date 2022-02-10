import os.path
from numba import jit, njit, prange
import numpy as np
import vectormath
import trimesh
from trimesh import visual
import xatlas
from PIL import Image

import ColorToUVIndex # VertexColorToTexture.ColorToUVIndex as


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
    vertices = mesh.vertices[vmapping]
    vertex_colors = mesh.visual.vertex_colors[vmapping]     # get the color per vertex after xatlas conversion
    vertex_normals = mesh.vertex_normals[vmapping]          # contains normal vertices after xatlas conversion

    # compute the maximum range of vertices for each dimension of the texture box
    min_positions = np.argmin(vertices, axis=0)  # find the minimum for each column
    max_positions = np.argmax(vertices, axis=0)  # find the maximum for each column

    # calculate the ranges per axis
    x_range = vertices[max_positions[0], 0] - vertices[min_positions[0], 0]
    y_range = vertices[max_positions[1], 1] - vertices[min_positions[1], 1]
    z_range = vertices[max_positions[2], 2] - vertices[min_positions[2], 2]
    ranges = [x_range, y_range, z_range]
    color_range = ranges[np.argmax(ranges)]  # np.argmax returns position of max value --> in ranges to get value

    # UV COORDINATES (of Vertices)
    pixel_position_array = create_texture(vertices, indices, textureWidth, uvs, vertex_colors, vertex_normals, color_range)

    cv = trimesh.visual.color.ColorVisuals(mesh, None, pixel_position_array)
    im = Image.fromarray(pixel_position_array)
    im.save("./VertexColorToTexture/texture/texture_map.png")


@jit(nopython=True, cache=True, parallel=True)
def create_texture(vertices, faces, textureWidth, uv_coordinates, colors, normals, color_range):
    ### INIT storing arrays
    textureShape = (textureWidth, textureWidth, 3)
    pixel_color_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the color will be mapped
    pixel_normal_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the normal color will be mapped
    pixel_position_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the position of the vertices will be mapped

    position_color_range = 255/color_range

    # process faces
    for i in range(0, len(faces)):
        face = faces[i]
        # get indices of vertices 0, 1 and 2 which are defining the face
        v0 = face[0]
        v1 = face[1]
        v2 = face[2]

        x1 = uv_coordinates[v0, 0]
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
                xNorm = x / textureWidth  # x normalized to value between 0 and 1 (easier to calculate)
                yNorm = y / textureWidth  # y normalized to value between 0 and 1 (easier to calculate)

                # get factors a, b, c such that
                # x = a * x1 + b * x2  + c * x3 --> x - c*x3 - b*x2 = a*x1 --> (x - c*x3 - b*x2)/x1 = a
                # y = a * y1 + b * y2 + c * y3 --> (y - c*y3 - a*y1)/y2 = b
                #                              --> ((x - c*x3 - ((y - c*y3 - a*y1)/y2)*x2)/x1 = a
                # a + b + c = 1
                a = ((x1 - x3) * (y - y3) - (y1 - y3) * (x - x3)) # https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
                b = ((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1))
                c = 1 - a - b

                #print(a, " ", b, " ", c)
                # check if point is within triangle
                if 0 <= a and 0 <= b and 0 <= c and (a + b + c) <= 1:
                    # color the pixel depending on the lerp between the three pixels
                    # new_colors might has shape of (lenOfVertices, 4) if it stores RGBA values --> only use RGB
                    pixel_color = a * colors[v0, :3] + b * colors[v1, :3] + c * colors[v2, :3]
                    # print("pixel_color= ", pixel_color)
                    x_i = x - sqxStart
                    y_i = y - sqyStart
                    pixel_color_array[x_i, y_i] = pixel_color
                    #  TODO write in hdr,
                    pColor = (a * normals[v0] + b * normals[v1] + c * normals[v2]) / 2
                    pixel_normal_color = [255*(pColor[0] + 0.5), 255*(pColor[1] + 0.5), 255*(pColor[2] + 0.5)]
                    pixel_normal_array[x_i, y_i] = pixel_normal_color

                    pixel_position_color = position_color_range * a * vertices[v0] + position_color_range *b * vertices[v1] + position_color_range * (c * vertices[v2])
                    pixel_position_array[x_i, y_i] = pixel_position_color
        #print(str(i) + " from " + str(len(faces)))
    return pixel_position_array


if __name__ == "__main__":
    get_texture_from_vertex_color(os.getcwd() + "/models/color_to_uv_index_testfiles/meshAfterPoisson", 1024)
