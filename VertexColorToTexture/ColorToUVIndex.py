import trimesh

uv_input_file = str("C:\\Users\\Alexander\\Documents\\GitHub\\Pointcloud2Mesh\\models\\color_to_uv_index_testfiles\\meshAfterXatlas")
color_input_file = str("C:\\Users\\Alexander\\Documents\\GitHub\\Pointcloud2Mesh\\models\\color_to_uv_index_testfiles\\meshAfterPoisson")

def get_distance(first_vertex: list, second_vertex: list):
    distance = abs(float(first_vertex[0]) - float(second_vertex[0])) + abs(float(first_vertex[1]) - float(second_vertex[1])) + abs(float(first_vertex[2]) - float(second_vertex[2]))
    return distance

def get_colors_for_uv_index(color_input_file: str, uv_input_file: str):

    color_mesh = trimesh.load_mesh(color_input_file + ".ply") #file after poisson reconstruction, but before Xatlas
    uv_mesh = trimesh.load_mesh(uv_input_file + ".obj") #file after Xatlas

    color_vertices = color_mesh.vertices
    uv_vertices = uv_mesh.vertices

    color_v = trimesh.visual.color.ColorVisuals(color_mesh)
    colors = color_v.vertex_colors

    uv_adjusted_colors = [0] * len(uv_vertices) #the array that will be filled with color values for each uv value
    combined_color_vertices = [0] * len(color_vertices)

    #merges vertex positions and color values so that each vertex retains its color information even after sorting
    for i in range(0, len(color_vertices)):
        combined_color_vertices[i] = [color_vertices[i][0], color_vertices[i][1], color_vertices[i][2], colors[i][0], colors[i][1], colors[i][2], colors[i][3]]    

    #sorts the vertices (including their color information) based on the values of x-, y- and z-position
    color_sorted_vertices = sorted(combined_color_vertices, key=lambda tup: (tup[0],tup[1],tup[2]))

    #Adds the original vertex index to the vertex position to allow reconstruction of original sorting order
    indexed_uv_vertices = [0]*len(uv_vertices)
    for i in range(0, len(uv_vertices)):
        indexed_uv_vertices[i] = [uv_vertices[i][0],uv_vertices[i][1],uv_vertices[i][2],i]

    #sort the vertices based on the value of x, then y, then z
    uv_sorted_vertices = sorted(indexed_uv_vertices, key=lambda tup: (tup[0],tup[1],tup[2]))

    c = 0 #value to count the current index within the sorted second_vertex list
    artifact_count = 0 #counts the number of vertices for which a match with another vertex had to be forced

    for i in range(0, len(uv_vertices)):        
        n = 0
        match_found = 0
        minimal_distance = [0,100]

        #Search for matching vertex position between the current .obj-vertex (uv) and another .ply-vertex (color)
        while match_found == 0 and n<50:
            max_limit_counter = min(c+n, len(color_sorted_vertices)-1)
            if get_distance(uv_sorted_vertices[i], color_sorted_vertices[max_limit_counter]) < 0.001:
                uv_adjusted_colors[uv_sorted_vertices[i][3]] = [color_sorted_vertices[max_limit_counter][3], color_sorted_vertices[max_limit_counter][4], color_sorted_vertices[max_limit_counter][5], 255]
                c = max_limit_counter
                match_found = 1
            else:
                #In case no match is found before the max search distance is reached, the .obj vertex will be matched with the closest .ply vertex within the search distance. May lead to artifacts.
                current_vertex_distance = get_distance(uv_sorted_vertices[i], color_sorted_vertices[max_limit_counter])
                if current_vertex_distance < minimal_distance[1]:
                    minimal_distance = [max_limit_counter, current_vertex_distance]
                #Loop through the search distance starting from the most likely point to find a match, then going outwards in both positive and negative direction
                if n > 0:
                    n *= -1
                else:
                    n *= -1
                    n += 1
            #If search distance is reached without match, force match with closest vertex (see above)
            if n == 49:
                uv_adjusted_colors[uv_sorted_vertices[i][3]] = [color_sorted_vertices[minimal_distance[0]][3], color_sorted_vertices[minimal_distance[0]][4], color_sorted_vertices[minimal_distance[0]][5], 255]
                artifact_count += 1
    
    #relevant outputs - for texture generation, use "uv_coordinates[i]" and "uv_adjusted_colors[i]"
    print("Finished matching " + str(len(uv_sorted_vertices)) + " vertices. Matches had to be forced for " + str(artifact_count) + " vertices. \nUse the array 'indexed_colors' in which colors are sorted by the index of the vertices in the .obj file.")
    return uv_adjusted_colors

indexed_colors = get_colors_for_uv_index(color_input_file, uv_input_file)

for i in range(0, 90000, 1000):
    print(str(i) + ") " + " " + str(indexed_colors[i]))