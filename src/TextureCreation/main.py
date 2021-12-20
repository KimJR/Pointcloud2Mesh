import pathlib
import trimesh
import xatlas
import os


# TODO later: open UI to select local file (input file) and specify output file
def poisson_reconstruction(input_file: str="eagle.points.ply", output_file:str="eagle.output.ply", depth:int=8, pointWeight:int=0, color:bool=False):
    '''
    Method to call the PoissonRecon tool (see https://github.com/mkazhdan/PoissonRecon) with the provided parameters in
    order to obtain the according mesh.
    :param input_file: name of the input file containing specifications of the point cloud for which the mesh shall be
           generated.
    :param output_file: name of the output file in which the result is stored.
    :param depth: maximum depth of the tree that will be used for surface reconstruction, default value is 8.
    :param pointWeight: specifies the importance that interpolation of the point samples is given in the formulation of
           the screened Poisson equation. Results of the original (unscreened) Poisson Reconstruction can be obtained by
           setting this value to 0
    :param color: boolean value defines if color values should be output with the vertices of the reconstructed surface.
           If True, the input file must contain the according color specification.
    :return: The output file is saved under PoissonRecon/Bin/Linux under the name specified in output_file, default file
             name is "eagle.output.ply"
    '''
    path = "../PoissonRecon/Bin/Linux"
    file = "../PoissonRecon"
    if input_file is not None and len(input_file) < 2:
        print("Input file name is invalid. Default file is used.")
        input_file = "eagle.points.ply"
    if output_file is not None and len(output_file) < 2:
        print("Output file name is invalid. Output file will be stored in default output file.")
        output_file = "eagle.output.ply"

    # call PoissonRecon to get the output mesh
    if not os.path.exists(path):
        print(" PoissonRecon could not be found at expectd location: ", path)
        return
    os.chdir(path)
    command = "sudo {} --in {} --out {} ".format(file, input_file, output_file)
    # add according parameter if specified in valid form (defaults here are also defaults of PoissonRecon)
    if depth:
        command += "--depth {}".format(depth)
    if pointWeight:
        command += "--pointWeight {}".format(pointWeight)
    if color:
        command += " --color "
    os.system(command)

def main():
    previous_dir = os.getcwd()
    poisson_reconstruction()

    os.chdir(previous_dir)

    mesh = trimesh.load_mesh("../PoissonRecon/Bin/Linux/eagle.output.ply")
    print(mesh)
    print("Vertices: ", mesh.vertices)
    print("Faces: ", mesh.faces)
    vmapping, indices, uvs = xatlas.parametrize(mesh.vertices, mesh.faces)
    print(uvs)


if __name__ == '__main__':
    main()

