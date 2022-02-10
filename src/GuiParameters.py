import open3d as o3d
import open3d.visualization.gui as gui


class Parameters:
    # first tab
    out_selected = True             # name of output file (default: mesh)
    color_selected = True           # color value (default 16)
    confidence_selected = False

    # second tab
    density_selected = False
    verbose_selected = False
    linearFit_selected = False
    primalVoxel_selected = False
    nWeights_selected = False
    polygonMesh_selected = False

    # third tab
    fullDepth_selected = False
    voxelDepth_selected = False
    cgDepth_selected = False

    # fourth tab
    depth_selected = False          # maximal depth of tree for surface reconstruction (default 8)
    iters_selected = False          # number of gauss-seidel relaxation at each iteration (default 8)
    degree_selected = False         # degree of B-spline: larger degree = higher order (default 2)

    # fifth tab
    threads_selected = False        # number of threads used for parallelization for reconstruntion (default 0)
    pointWeight_selected = False    # importance for interpolation of point samples (default 4)
    samplesPerNode_selected = False  # min number of samples per node in octry; adapted to density (default 1.000)

    scale_selected = False          # ratio of cube diameter for reconstruction and those for bounding (default 1.100)
    voxel_selected = False          # name of file to which the sampled implicit function is written

    def __init__(self):
        # 1 --out <name>
        self.out = gui.Checkbox("--out")
        self.out.tooltip = "Name of the file to which the triangle mesh will be written (.ply)"
        # self.out.set_on_checked(self.on_out)
        self.out_name = gui.TextEdit()
        self.out_name.Constraints.width=0.4
        self.out_name.text_value = "mesh"
        self.out_name.placeholder_text = "mesh"


        # 2 --color <pull factor>
        self.color = gui.Checkbox("--colors")
        self.color.tooltip = "Extrapolate the color values to the vertices of the mesh\nValue = relative importance of finer color estimates over lower ones"
        self.color.set_on_checked(self.on_color)
        self.color_value = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.color_value.set_value(16.0)


        # 3 --threads <number of processing threads>
        self.threads = gui.Checkbox("--threads")
        self.threads.tooltip = "Number of threads across which the reconstruction algorithm should be parallelized\nDefault: numer of (virtual) processors on the executing machine"
        self.threads.set_on_checked(self.on_threads)
        self.threads_value = gui.NumberEdit(gui.NumberEdit.INT)

        # 4 --pointWeight <interpolation weight>"
        self.pointWeight = gui.Checkbox("--pointWeight")
        self.pointWeight.tooltip = "Specifies the importants that interpolation of the point samples is given in the formulation of the screened Poisson equation.\n0 = original (unscreened) Poisson Reconstruction"
        self.pointWeight.set_on_checked(self.on_pointWeigt)
        self.pointWeight_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.pointWeight_value.set_value(4)

        # 5 --voxel <output voxel grid>
        self.voxel = gui.Checkbox("--voxel")
        self.voxel.tooltip = "Name of the file to which the sampled implicit function will be written (binary)"
        self.voxel.set_on_checked(self.on_voxel)
        self.voxel_name = gui.TextEdit()
        self.voxel_name.text_value = "voxel_out"
        self.voxel_name.placeholder_text = "voxel_out"

        # 6 --depth <reconstruction depth>
        self.depth = gui.Checkbox("--depth")
        self.depth.tooltip = "Maximum depth of the tree that will be used for surface reconstruction"
        self.depth.set_on_checked(self.on_depth)
        self.depth_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.depth_value.set_value(8)

        # 7 --fullDepth <adaptive octree depth>
        self.fullDepth = gui.Checkbox("--fullDepth")
        self.fullDepth.tooltip = "Specifies the depth beyond depth the octree will be adapted"
        self.fullDepth.set_on_checked(self.on_fullDepth)
        self.fullDepth_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.fullDepth_value.set_value(5)

        # 8 --voxelDepth <voxel sampling depth>
        self.voxelDepth = gui.Checkbox("--voxelDepth")
        self.voxelDepth.tooltip = "Specifies the depth beyond depth the octree will be adapted"
        self.voxelDepth.set_on_checked(self.on_voxelDepth)
        self.voxelDepth_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.voxelDepth_value.set_value(8)

        # 9 --cgDepth <conjugate gradients solver depth>
        self.cgDepth = gui.Checkbox("--cgDepth")
        self.cgDepth.tooltip = "Depth up to which a conjugate-gradients solver will be used to solve the linear system.\nBeyond this depth Gauss-Seidel relaxation will be used"
        self.cgDepth.set_on_checked(self.on_cgDepth)
        self.cgDepth_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.cgDepth_value.set_value(0)

        # 10 --scale <scale factor>
        self.scale = gui.Checkbox("--scale")
        self.scale.tooltip = "Specifies the ratio between the diameter of the cube used for reconstruction and the diameter of the samples' bounding cube"
        self.scale.set_on_checked(self.on_scale)
        self.scale_value = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.scale_value.set_value(1.1)

        # 11 --samplesPerNode <minimum number of samples>
        self.samplesPerNode = gui.Checkbox("--samplesPerNode")
        self.samplesPerNode.tooltip = "Specifies the minimum number of sample points that should fall within an octree node as the octree construction is adapted to sampling density.\nnoise-free samples: [1.0 - 5.0], noisy samples: [15.0 - 20.0]"
        self.samplesPerNode.set_on_checked(self.on_samplesPerNode)
        self.samplesPerNode_value = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.samplesPerNode_value.set_value(1.0)

        # 12 --iters <GS iters>
        self.iters = gui.Checkbox("--iters")
        self.iters.tooltip = "Specifies the number of Gauss-Seidel relaxations to be performed at each level of the hierarchy"
        self.iters.set_on_checked(self.on_iters)
        self.iters_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.iters_value.set_value(8)

        # 13 --polygonMesh
        self.polygonMesh = gui.Checkbox("--polygonMesh")
        self.polygonMesh.tooltip = "Output a polygon mesh (rather than triangulating the results of Marching Cubes)"
        self.polygonMesh.set_on_checked(self.on_polygonMesh)

        # 14 --density
        self.density = gui.Checkbox("--density")
        self.density.tooltip = "Output the estimated depth values of the iso-surface vertices"
        self.density.set_on_checked(self.on_density)

        # 15 --primalVoxel
        self.primalVoxel = gui.Checkbox("--primalVoxel")
        self.primalVoxel.tooltip = "Outputing to a voxel file has the reconstructor sample the implicit function at the corners of the grid, rather than the centers of the cells"
        self.primalVoxel.set_on_checked(self.on_primalVoxel)

        # 16 --confidence
        self.confidence = gui.Checkbox("--confidence")
        self.confidence.tooltip = "Use the size of the normals as confidence information.\n When the flag is not enabled, all normals are normalized to have unit-length prior to reconstruction "
        self.confidence.set_on_checked(self.on_cinfidence)

        # 17 --verbose
        self.verbose = gui.Checkbox("--verbose")
        self.verbose.tooltip = "Verbose description of the running times and memory usages of individual components"
        self.verbose.set_on_checked(self.on_verbose)

        # 18 --linearFit
        self.linearFit = gui.Checkbox("--linearFit")
        self.linearFit.tooltip = "Use linear interpolation to estimate the positions of iso-vertices"
        self.linearFit.set_on_checked(self.on_linearFit)

        # 19 --nWeights
        self.nWeights = gui.Checkbox("--nWeights")
        self.nWeights.tooltip = "Use the size of the normals to modulate the interpolation weights.\nWhen the flag is not enabled, all points are given the same weight"
        self.nWeights.set_on_checked(self.on_nWeights)

        # 20 --degree <B-spline degree>
        self.degree = gui.Checkbox("--degree")
        self.degree.tooltip = "Specifies the degree of the B-spline that is to be used to define the finite elements system\nLarger degrees support higher order approximations, but come at the cost of denser system matrices"
        self.degree.set_on_checked(self.on_degree)
        self.degree_value = gui.NumberEdit(gui.NumberEdit.INT)
        self.degree_value.set_value(2)

    '''
        tabs for grid
    '''
    def tab1(self, em):
        grid = gui.VGrid(1, 0.25 * em)

        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self.out)
        h.add_child(self.out_name)
        h.add_stretch()
        grid.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 2
        h.add_child(self.color)
        h.add_child(self.color_value)
        h.add_stretch()
        grid.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 3
        h.add_child(self.confidence)
        h.add_stretch()
        grid.add_child(h)

        return grid

    def tab2(self, em):
        grid = gui.VGrid(2, 0.25 * em)
        grid.add_child(self.density)
        grid.add_child(self.primalVoxel)
        grid.add_child(self.verbose)
        grid.add_child(self.nWeights)
        grid.add_child(self.linearFit)
        grid.add_child(self.polygonMesh)

        return grid

    def tab3(self, em):
        grid = gui.VGrid(1, 0.25 * em)

        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self.fullDepth)
        h.add_stretch()
        h.add_child(self.fullDepth_value)
        grid.add_child(h)
        h = gui.Horiz(0.25 * em)  # row 2
        h.add_child(self.cgDepth)
        h.add_stretch()
        h.add_child(self.cgDepth_value)
        grid.add_child(h)
        h = gui.Horiz(0.25 * em)  # row 3
        h.add_child(self.voxelDepth)
        h.add_stretch()
        h.add_child(self.voxelDepth_value)

        grid.add_child(h)

        return grid

    def tab4(self, em):
        grid = gui.VGrid(1, 0.25 * em)

        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self.depth)
        h.add_stretch()
        h.add_child(self.depth_value)
        grid.add_child(h)
        h = gui.Horiz(0.25 * em)  # row 2
        h.add_child(self.iters)
        h.add_stretch()
        h.add_child(self.iters_value)
        grid.add_child(h)
        h = gui.Horiz(0.25 * em)  # row 3
        h.add_child(self.degree)
        h.add_stretch()
        h.add_child(self.degree_value)

        grid.add_child(h)
        return grid

    def tab5(self, em):
        grid = gui.VGrid(1, 0.25 * em)

        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self.threads)
        h.add_stretch()
        h.add_child(self.threads_value)
        grid.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 2
        h.add_child(self.pointWeight)
        h.add_stretch()
        h.add_child(self.pointWeight_value)
        grid.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 3
        h.add_child(self.samplesPerNode)
        h.add_stretch()
        h.add_child(self.samplesPerNode_value)

        grid.add_child(h)
        return grid

    def tab6(self, em):
        grid = gui.VGrid(1, 0.25 * em)

        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self.scale)
        h.add_child(self.scale_value)
        h.add_stretch()
        grid.add_child(h)

        h = gui.Horiz(0.25 * em)  # row 2
        h.add_child(self.voxel)
        h.add_child(self.voxel_name)
        h.add_stretch()
        grid.add_child(h)
        return grid
    '''
        set on checked boxes
    '''
    def on_out(self, selected):
        self.out_selected = selected
        self.out_name = str(self.out_name)
        print(self.out_name.text_value)

    def on_color(self, selected):
        self.color_selected = selected

    def on_threads(self, selected):
        self.threads_selected = selected

    def on_pointWeigt(self, selected):
        self.pointWeight_selected = selected

    def on_voxel(self, selected):
        self.voxel_selected = selected

    def on_depth(self, selected):
        self.depth_selected = selected

    def on_fullDepth(self, selected):
        self.fullDepth_selected = selected

    def on_voxelDepth(self, selected):
        self.voxelDepth_selected = selected

    def on_cgDepth(self, selected):
        self.cgDepth_selected = selected

    def on_scale(self, selected):
        self.scale_selected = selected

    def on_samplesPerNode(self, selected):
        self.samplesPerNode_selected = selected

    def on_iters(self, selected):
        self.iters_selected = selected

    def on_polygonMesh(self, selected):
        self.polygonMesh_selected = selected

    def on_density(self, selected):
        self.density_selected = selected

    def on_primalVoxel(self, selected):
        self.primalVoxel_selected = selected

    def on_cinfidence(self, selected):
        self.confidence_selected = selected

    def on_verbose(self, selected):
        self.verbose_selected = selected

    def on_linearFit(self, selected):
        self.linearFit_selected = selected

    def on_nWeights(self, selected):
        self.nWeights_selected = selected

    def on_degree(self, selected):
        self.degree_selected = selected

