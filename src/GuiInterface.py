import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from src.GuiParameters import Parameters
from src.PoissonReconstruction import run_poisson_reconstruction
from src.ColorToTexture import get_texture_from_vertex_color
import numpy as np


class Settings:

    gen_filename = "generated_input.ply"
    input_file = ""
    output_file = ""

    def __init__(self, main_dir, my_os):
        # Directories
        self.main_dir = main_dir
        self.model_dir = main_dir + "/models/"
        self.out_dir = main_dir + "/out/"

        # Operation system
        self.my_os = my_os


class GUI:
    '''
    Class GUI represents the graphical user interface of the pointcloud2mesh tool. File chooser, Buttons to start
    mesh and UV map calculation are provided as well as graphical elements to adjust how the calculations are performed.
    '''

    actual_geometry = []

    mesh_button_enabled = False
    uvmap_button_enabled = False

    def __init__(self, main_dir, my_os):
        # set settings
        self.settings = Settings(main_dir, my_os)

        # create window
        self.window = gui.Application.instance.create_window("Poisson Surface Reconstruction", 2200, 1400)
        w = self.window  # for more concise code

        # set the window's layout
        w.set_on_layout(self._on_layout)

        # 3D widget
        self.widget = gui.SceneWidget()
        self.widget.scene = rendering.Open3DScene(w.renderer)

        # consistent size across platform
        em = w.theme.font_size
        separation_height = int(round(0.5 * em))

        # ---- Layout panel ----
        self.panel = gui.Vert(0.5 * em, gui.Margins(0.5 * em, 0.25 * em, 0.5 * em, 0.25 * em))

        # Create file-chooser widget
        self._fileedit = gui.TextEdit()
        filedlgbutton = gui.Button("...")
        filedlgbutton.horizontal_padding_em = 0.5
        filedlgbutton.vertical_padding_em = 0
        filedlgbutton.set_on_clicked(self._on_filedlg_button)
        self.panel.add_child(filedlgbutton)

        # horizontal widget
        fileedit_layout = gui.Horiz()
        fileedit_layout.add_child(gui.Label("File"))
        fileedit_layout.add_child(self._fileedit)
        fileedit_layout.add_fixed(0.25 * em)
        fileedit_layout.add_child(filedlgbutton)
        self.panel.add_child(fileedit_layout)

        # Create Label
        self._label = gui.Label("|1| Poisson Surface Reconstruction")
        self._label.text_color = gui.Color(1.0, 0.5, 0.0)
        self.panel.add_fixed(separation_height)
        self.panel.add_child(self._label)

        # create button
        self._mesh_button = gui.Button("Calculate mesh")
        self._mesh_button.set_on_clicked(self.on_calculate_mesh)
        self._mesh_button.enabled = False
        self.panel.add_child(self._mesh_button)

        # Parameters class
        self.param = Parameters()

        # generate Tabs
        tabs = gui.TabControl()
        # tab 1
        self.param.color_value.set_preferred_width(3.5 * em)
        tabs.add_tab(" 1 ", self.param.tab1(em))
        # tab 2
        tabs.add_tab(" 2 ", self.param.tab2(em))
        # tab 3
        self.param.depth_value.set_preferred_width(5.5 * em)
        self.param.iters_value.set_preferred_width(5.5 * em)
        self.param.pointWeight_value.set_preferred_width(5.5 * em)
        tabs.add_tab(" 3 ", self.param.tab3(em))
        # tab 4
        self.param.samplesPerNode_value.set_preferred_width(3 * em)
        self.param.threads_value.set_preferred_width(5.5 * em)
        self.param.degree_value.set_preferred_width(5.5 * em)
        tabs.add_tab(" 4 ", self.param.tab4(em))
        # tab 5
        tabs.add_tab(" 5 ", self.param.tab5(em))

        # add tabs to panel
        self.panel.add_child(tabs)

        # Create Label
        self._label = gui.Label("|2| UV Mapping")
        self._label.text_color = gui.Color(1.0, 0.5, 0.0)
        self.panel.add_child(self._label)

        # create button
        self._uvmap_button = gui.Button("Calculate UV Map")
        self._uvmap_button.set_on_clicked(self._on_calculate_uvmap)
        self.panel.add_child(self._uvmap_button)

        # crate Textfield output name Image
        self._image_label = gui.Label("Image name")
        self.texture_name = gui.TextEdit()
        self.texture_name.Constraints.width = 0.4
        self.texture_name.text_value = "uv_map"
        self.texture_name.placeholder_text = "uv_map"
        # grid layout
        grid = gui.VGrid(1, 0.25 * em)
        h = gui.Horiz(0.25 * em)  # row 1
        h.add_child(self._image_label)
        h.add_child(self.texture_name)
        h.add_stretch()
        grid.add_child(h)
        self.panel.add_child(grid)

        # Create Label 3
        self.panel.add_fixed(separation_height)
        self._label = gui.Label("|3| Texture map")
        self._label.text_color = gui.Color(1.0, 0.5, 0.0)
        self.panel.add_child(self._label)

        # create image
        self._texture_image = gui.ImageWidget(self.settings.model_dir+"placeholder.png")
        self.panel.add_child(self._texture_image)


        # Create Label 4
        self.panel.add_fixed(separation_height)
        self._label = gui.Label("|4| Normal map")
        self._label.text_color = gui.Color(1.0, 0.5, 0.0)
        self.panel.add_child(self._label)

        # create image
        self._normal_image = gui.ImageWidget(self.settings.model_dir+"placeholder.png")
        self.panel.add_child(self._normal_image)

        # ---- add settings panel + widget to window ----
        w.add_child(self.widget)
        w.add_child(self.panel)

        # run apply_settings
        self.apply_settings()

    def apply_settings(self):
        '''
        Method to set all GuiParameters according to the users choice,
        which are then considered for poisson reconstruction.
        '''
        # select parameters
        self.param.out.checked = self.param.out_selected
        self.param.color.checked = self.param.color_selected
        self.param.threads.checked = self.param.threads_selected
        self.param.pointWeight.checked = self.param.pointWeight_selected
        self.param.grid.checked = self.param.grid_selected
        self.param.depth.checked = self.param.depth_selected
        self.param.scale.checked = self.param.scale_selected
        self.param.samplesPerNode.checked = self.param.samplesPerNode_selected
        self.param.iters.checked = self.param.iters_selected
        self.param.density.checked = self.param.density_selected
        self.param.primalVoxel.checked = self.param.primalVoxel_selected
        self.param.confidence.checked = self.param.confidence_selected
        self.param.verbose.checked = self.param.verbose_selected
        self.param.linearFit.checked = self.param.linearFit_selected
        self.param.nWeights.checked = self.param.nWeights_selected
        self.param.degree.checked = self.param.degree_selected

        # enable buttons
        self._mesh_button.enabled = self.mesh_button_enabled
        self._uvmap_button.enabled = self.uvmap_button_enabled

    def _on_layout(self, layout_context):
        '''
        Set up the layout of the window.
        :param layout_context:
        :return: void
        '''
        contentRect = self.window.content_rect
        panel_width = 15 * layout_context.theme.font_size  # 15 ems wide
        self.widget.frame = gui.Rect(contentRect.x, contentRect.y, contentRect.width - panel_width, contentRect.height)
        self.panel.frame = gui.Rect(self.widget.frame.get_right(), contentRect.y, panel_width, contentRect.height)

    '''_________________________________ACTION LISTENER FOR FILE DIALOG_________________________________'''
    def _on_filedlg_button(self):
        '''
        Action listener for the file dialog button:
        creates a file dialog with predefined file filters for point cloud input file selection
        '''
        filedlg = gui.FileDialog(gui.FileDialog.OPEN, "Select input file", self.window.theme)
        filedlg.add_filter(".ply .pcd .xyz .pts ", "Point cloud files (.ply, .pcd, .xyz, .pts)")
        filedlg.add_filter(".ply", "Polygon files (.ply)")
        filedlg.add_filter(".pcd", "Point Cloud Data files (.pcd)")
        filedlg.add_filter(".xyz", "ASCII point cloud files (.xyz)")
        filedlg.add_filter(".pts", "3D Points files (.pts)")
        filedlg.add_filter("", "All files")

        # A file dialog MUST define on_cancel and on_done functions
        filedlg.set_on_cancel(self._on_filedlg_cancel)
        filedlg.set_on_done(self._on_filedlg_done)

        self.window.show_dialog(filedlg)

    def _on_filedlg_cancel(self):
        self.window.close_dialog()

    def _on_filedlg_done(self, path):
        self._fileedit.text_value = path
        self.settings.input_file = path
        self.window.close_dialog()
        self.check_loaded_file(path)
        self.plot_result(shader="defaultUnlit")
        self.load(path)

    def load(self, path):
        '''
        Method is basically from: https://github.com/isl-org/Open3D/blob/master/examples/python/gui/vis-gui.py
        '''
        self.widget.scene.clear_geometry()

        geometry = None
        geometry_type = o3d.io.read_file_geometry_type(path)

        mesh = None
        if geometry_type & o3d.io.CONTAINS_TRIANGLES:
            mesh = o3d.io.read_triangle_mesh(path)
        if mesh is not None:
            if len(mesh.triangles) == 0:
                # Probably always the case for this project
                print(
                    "[INFO] Contains 0 triangles, will read as point cloud")
                mesh = None
            else:
                mesh.compute_vertex_normals()
                if len(mesh.vertex_colors) == 0:
                    mesh.paint_uniform_color([1, 1, 1])
                geometry = mesh
                # Make sure the mesh has texture coordinates
                if not mesh.has_triangle_uvs():
                    uv = np.array([[0.0, 0.0]] * (3 * len(mesh.triangles)))
                    mesh.triangle_uvs = o3d.utility.Vector2dVector(uv)
        else:
            print("[Info]", path, "seems to be a point cloud. :)")

        if geometry is None:
            cloud = o3d.io.read_point_cloud(path)
            if cloud is not None:
                print("[Info] Successfully read", path)
                if not cloud.has_normals():
                    cloud.estimate_normals()
                cloud.normalize_normals()
                geometry = cloud
            else:
                print("[WARNING] Failed to read points", path)

        if geometry is not None:
            try:
                self.widget.scene.add_geometry("__model__", geometry,
                                               self.settings.material)
                bounds = geometry.get_axis_aligned_bounding_box()
                self.widget.setup_camera(60, bounds, bounds.get_center())
            except Exception as e:
                print(e)
        self.plot_result()

    '''
       Men?? bar Quit
    '''
    def _on_menu_quit(self):
        gui.Application.instance.quit()

    '''
     show pointcloud
    '''
    def check_loaded_file(self, path):
        # enable mesh button
        self.mesh_button_enabled = True

        # check if loaded file has normal and color values
        geometry = None
        newfile = False

        if geometry is None:
            cloud = None
            try:
                cloud = o3d.io.read_point_cloud(path, remove_nan_points=False, remove_infinite_points=False)
            except Exception:
                pass
            if cloud is not None:
                if not cloud.has_normals():
                    print("[Info] Missing normals: they are calculated")
                    cloud.estimate_normals()
                    newfile = True
                cloud.normalize_normals()

                if not cloud.has_colors():
                    print("[Info] Missing colors: assign each point uniform colors")
                    cloud.paint_uniform_color([1.0, 0, 0])
                    newfile = True

                if newfile:
                    print("'generated_input.ply' is generated with normals and colors")
                    new_path = self.settings.model_dir+self.settings.gen_filename
                    o3d.io.write_point_cloud(new_path, cloud, write_ascii=True, compressed=False)
                    self._fileedit.text_value = new_path
                    self.settings.input_file = new_path
                self.actual_geometry = cloud
            else:
                print("[WARNING] Failed to read points", path)

        self.apply_settings()

    def plot_result(self, path=None, shader="defaultUnlit"):
        self.widget.scene.clear_geometry()
        if path is not None:
            # path should be set if mesh shall be shown
            self.actual_geometry = o3d.io.read_triangle_mesh(path)

        if not self.actual_geometry.is_empty():
            mat = rendering.Material()
            mat.shader = shader
            self.widget.scene.add_geometry("__model__", self.actual_geometry, mat)
            bounds = self.actual_geometry.get_axis_aligned_bounding_box()
            self.widget.setup_camera(60, bounds, bounds.get_center())

    '''_________________________________ACTION LISTENER FOR BUTTON_________________________________'''
    def on_calculate_mesh(self):
        # enable uvmap button
        self.uvmap_button_enabled = True

        # set outputfile
        # check for empty field and set default
        if self.param.out_name.text_value != "":
            self.settings.output_file = self.settings.out_dir+self.param.out_name.text_value
        else:
            self.settings.output_file = self.settings.out_dir+"mesh"

        # run poisson reconstruction + xatlas
        run_poisson_reconstruction(self, self.settings.input_file, self.settings.output_file)

        # plot new generated mesh
        self.plot_result(self.settings.output_file+".ply", "unlitLine")

        # apply settings
        self.apply_settings()

    def _on_calculate_uvmap(self):
        # output_file is the file where the output from mesh generation was stored
        image_name = str(self.settings.out_dir) + str(self.texture_name.text_value)
        get_texture_from_vertex_color(self.settings.output_file, image_name)

        # show new generated mesh
        normal = o3d.io.read_image(str(image_name) + '_normal.png')

        # show texture
        self._texture_image.update_image(o3d.io.read_image(str(image_name) + '_texture.png'))
        # show normal map
        self._normal_image.update_image(o3d.io.read_image(str(image_name) + '_normal.png'))
        # apply settings2,4615485866666668713
        self.apply_settings()