import pymesh
import vectormath


def get_texture_from_vertex_color(input_file:str):
    '''
    Generate the texture from colors of vertices.
    :param input_file: the name of the input file, must not be None or empty.
           The object file includes an array of all faces (triangles). Each triangle includes an array of 3 vertices
    :return: the texture
    '''


    #vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)

    #xatlas.export(str(input_file)+".obj", mesh.vertices[vmapping], indices, uvs)

    if not input_file.endswith(".obj", -5, -1):#
        print(".obj-File was expected for texture generation")
        return

    mesh = pymesh.load_mesh(input_file)
    color_map = pymesh.texture # the texture to which the color will be mapped
    normal_map = pymesh.texture # the texture to which the normal color will be mapped
    position_map = pymesh.texture # the texture to which the position of the vertices will be mapped

    for t in mesh.faces:
        v0 = t.vertex[0]
        v1 = t.vertex[1]
        v2 = t.vertex[2]

        # get vertex UVs
        x1 = v0.u
        y1 = v0.v
        x2 = v1.u
        y2 = v1.v
        x3 = v2.u
        y3 = v2.v

        # get smallest square of pixels that includes all three vertex uv positions
        sqxStart = min(x1, x2, x3)
        sqxEnd = max(x1, x2, x3)
        sqyStart = min(y1, y2, y3)
        sqyEnd = max(y1, y2, y3)
        width = color_map.width
        # cycle through each pixel within the square to see if the pixel is within the triangle
        for y in range(int(sqyStart * width), int(sqxEnd * width)):
            for x in range(int(sqxStart * width), int(sqyEnd * width)):

                xNorm = x/width # x normalized to value between 0 and 1 (easier to calculate)
                yNorm = y/width # y normalized to value between 0 and 1 (easier to calculate)

                #get factors a, b, c such that
                #x = a * x1 + b * x2  + c * x3
                #y = a * y1 + b * y2 + c * y3
                #a + b + c = 1
                a = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
                b = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / ((y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3))
                c = 1 - a - b

                # check if point is within triangle
                if 0 <= a & a <= 1 & 0 <= b & b <= 1 & 0 <= c & c <= 1:
                    # color the pixel depending on the lerp between the three pixels
                    pixelColor = a * v0.color + b * v1.color + c * v2.color
                    color_map.SetPixel(x, y, pixelColor)

                    pixelNormalColor = (a * v0.normal + b * v1.normal + c * v2.normal)/2 + vectormath.Vector3(0.5, 0.5, 0.5)
                    normal_map.SetPixel(x, y, pixelNormalColor)

                    pixelPositionColor = (a * v0.position + b * v1.position + c * v2.position)
                    position_map.SetPixel(x, y, pixelPositionColor)