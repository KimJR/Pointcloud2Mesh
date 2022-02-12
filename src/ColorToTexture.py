import os.path
from numba import jit, njit, prange
import numpy as np
import trimesh
from trimesh import visual
import xatlas
from PIL import Image


def get_texture_from_vertex_color(input_file: str, image_name:str, textureWidth: int = 1024):
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
    (pixel_position_array, pixel_normal_array) = create_texture(vertices, indices, textureWidth, uvs, vertex_colors, vertex_normals, color_range, image_name)

    cv = trimesh.visual.color.ColorVisuals(mesh, None, pixel_position_array)

    # save texture map
    im = Image.fromarray(pixel_position_array)
    im.save(str(image_name) + '_texture.png')

    # save normal map
    im_n = Image.fromarray(pixel_normal_array)
    im_n.save(str(image_name) + '_normal.png')

@jit(nopython=True, cache=True, parallel=True)
def create_texture(vertices, faces, textureWidth, uv_coordinates, colors, normals, color_range, image_name):
    ### INIT storing arrays
    textureShape = (textureWidth, textureWidth, 3)
    pixel_color_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the color will be mapped
    pixel_normal_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the normal color will be mapped
    pixel_position_array = np.zeros(textureShape, dtype=np.uint8)  # the texture to which the position of the vertices will be mapped

    position_color_range = 255/color_range

    # process faces
    for i in prange(0, len(faces)):
        face = faces[i]
        # get indices of vertices 0, 1 and 2 which are defining the face
        iVertex0 = face[0]
        iVertex1 = face[1]
        iVertex2 = face[2]

        u1 = uv_coordinates[iVertex0, 0]
        v1 = uv_coordinates[iVertex0, 1]
        u2 = uv_coordinates[iVertex1, 0]
        v2 = uv_coordinates[iVertex1, 1]
        u3 = uv_coordinates[iVertex2, 0]
        v3 = uv_coordinates[iVertex2, 1]
        # precompute for plane with P_Vertex1_Vertex2
        v2v3 = v2-v3
        u2u3 = u2-u3
        # precompute for plane with P_Vertex2_Vertex0
        v3v1 = v3-v1
        u3u1 = u3-u1

        # get smallest square of pixels that includes all three vertex positions
        sqr_start_u = int(min(u1, u2, u3) * textureWidth)
        sqr_end_u = int(max(u1, u2, u3) * textureWidth)
        sqr_start_v = int(min(v1, v2, v3) * textureWidth)
        sqr_end_v = int(max(v1, v2, v3) * textureWidth)

        # cycle through each pixel within the square to see if the pixel is within the triangle
        for y in prange(sqr_start_v, sqr_end_v):
            for x in prange(sqr_start_u, sqr_end_u):
                xNorm = x / textureWidth  # x normalized to value between 0 and 1 (easier to calculate)
                yNorm = y / textureWidth  # y normalized to value between 0 and 1 (easier to calculate)

                # see https://ceng2.ktu.edu.tr/~cakir/files/grafikler/Texture_Mapping.pdf
                a = (xNorm - u2)*v2v3 - u2u3*(yNorm - v2)  # compute area between pixel, v2 and v3
                b = (xNorm - u3)*v3v1 - u3u1*(yNorm - v3)  # compute area between pixel, v3 and v1
                c = 1 - a - b

                # check if point is within triangle
                if 0 <= a and 0 <= b and 0 <= c and (a + b + c) <= 1:
                    # color the pixel depending on the lerp between the three pixels
                    # colors might have shape of (lenOfVertices, 4) if it stores RGBA values --> only use RGB
                    pixel_color = a * colors[iVertex0, :3] + b * colors[iVertex1, :3] + c * colors[iVertex2, :3]

                    pixel_color_array[x, y] = pixel_color
                    pColor = (a * normals[iVertex0] + b * normals[iVertex1] + c * normals[iVertex2]) # / 2
                    pixel_normal_color = [255*(pColor[0] + 0.5), 255*(pColor[1] + 0.5), 255*(pColor[2] + 0.5)]
                    pixel_normal_array[x, y] = pixel_normal_color

                    pixel_position_color = position_color_range * a * vertices[iVertex0] + position_color_range *b * vertices[iVertex1] + position_color_range * (c * vertices[iVertex2])
                    pixel_position_array[x, y] = pixel_position_color
    return (pixel_position_array, pixel_normal_array)