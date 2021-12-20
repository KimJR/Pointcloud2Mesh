import os


def run_poisson_reconstruction(self, input_file: str="input.ply", output_file:str="mesh.ply",):
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
    :return: The output file is saved under PoissonRecon/Bin/Linux under the name specified in output_file, default file
             name is "eagle.output.ply"
    '''
    path = ""
    file = ""
    # for windows os
    if self.settings.my_os == 'Windows':
        path = "/ext/PoissonRecon.x64/"
        file = "PoissonRecon.x64.exe"

    # for linux os
    if self.settings.my_os == 'Linux':
        path = "/ext/PoissonRecon/Bin/Linux"
        file = "./PoissonRecon"

    # for macOs
    if self.settings.my_os == 'Darwin':
        path = "/ext/PoissonRecon/Bin/Linux"
        file = "./PoissonRecon"

    # call PoissonRecon to get the output mesh
    if not os.path.exists(self.settings.main_dir + path):
        print(" PoissonRecon could not be found at expectd location: ", path)
        return
    os.chdir(self.settings.main_dir + path)

    # add according parameter if specified in valid form (defaults here are also defaults of PoissonRecon)
    command = "{} --in {} --out {} ".format(file, input_file, output_file)

    if self.param.linearFit_selected:
        command += "--linearFit "
    if self.param.degree_selected:
        command += "--degree {} ".format(self.param.degree_value.int_value)
    if self.param.color_selected:
        command += "--color {} ".format(self.param.color_value.double_value)
    if self.param.voxel_selected:
        command += "--voxel {} ".format(self.param.voxel_name.text_value)
    if self.param.depth_selected:
        command += "--depth {} ".format(self.param.depth_value.int_value)
    if self.param.fullDepth_selected:
        command += "--fullDepth {} ".format(self.param.fullDepth_value.int_value)
    if self.param.voxelDepth_selected:
        command += "--voxelDepth {} ".format(self.param.voxelDepth_value.int_value)
    if self.param.primalVoxel_selected:
        command += "--primalVoxel "
    if self.param.cgDepth_selected:
        command += "--cgDepth {} ".format(self.param.cgDepth_value.int_value)
    if self.param.scale_selected:
        command += "--scale {} ".format(self.param.scale_value.double_value)
    if self.param.samplesPerNode_selected:
        command += "--samplesPerNode {} ".format(self.param.samplesPerNode_value.double_value)
    if self.param.pointWeight_selected:
        command += "--pointWeight {} ".format(self.param.pointWeight_value.int_value)
    if self.param.iters_selected:
        command += "--iters {} ".format(self.param.iters_value.int_value)
    if self.param.threads_selected:
        command += "--threads {} ".format(self.param.threads_value.int_value)
    if self.param.confidence_selected:
        command += "--confidence "
    if self.param.nWeights_selected:
        command += "--nWeights "
    if self.param.polygonMesh_selected:
        command += "--polygonMesh "
    if self.param.density_selected:
        command += "--density "
    if self.param.verbose_selected:
        command += "--verbose "

    print("$ " + command)

    os.system(command)
    os.chdir(self.settings.main_dir)
