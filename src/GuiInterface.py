import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering
from src.GuiParameters import Parameters
from src.PoissonReconstruction import run_poisson_reconstruction
from src.ColorToTexture import get_texture_from_vertex_color


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

    actual_geometry = []

    mesh_button_enabled = False
    uvmap_button_enabled = False

    def __init__(self, main_dir, my_os):
        # set settings
        self.settings = Settings(main_dir, my_os)

        # create window
        self.window = gui.Application.instance.create_window("Poisson Surface Reconstruction", 1000, 700)
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
        self.param.fullDepth_value.set_preferred_width(5.5 * em)
        self.param.cgDepth_value.set_preferred_width(5.5 * em)
        self.param.voxelDepth_value.set_preferred_width(5.5 * em)
        tabs.add_tab(" 3 ", self.param.tab3(em))
        # tab 4
        self.param.depth_value.set_preferred_width(5.5 * em)
        self.param.iters_value.set_preferred_width(5.5 * em)
        self.param.pointWeight_value.set_preferred_width(5.5 * em)
        tabs.add_tab(" 4 ", self.param.tab4(em))
        # tab 5
        self.param.samplesPerNode_value.set_preferred_width(3 * em)
        self.param.threads_value.set_preferred_width(5.5 * em)
        self.param.degree_value.set_preferred_width(5.5 * em)
        tabs.add_tab(" 5 ", self.param.tab5(em))
        # tab 6
        tabs.add_tab(" 6 ", self.param.tab6(em))

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
        self.texture_name.text_value = "texture_map"
        self.texture_name.placeholder_text = "texture_map"
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
        self._image_field = gui.ImageWidget(self.settings.model_dir+"dummy_texture.jpeg")
        self.panel.add_child(self._image_field)

        # ---- add settings panel + widget to window ----
        w.add_child(self.widget)
        w.add_child(self.panel)

        # run apply_settings
        self.apply_settings()

    def apply_settings(self):

        # select parameters
        self.param.out.checked = self.param.out_selected
        self.param.color.checked = self.param.color_selected
        self.param.threads.checked = self.param.threads_selected
        self.param.pointWeight.checked = self.param.pointWeight_selected
        self.param.voxel.checked = self.param.voxel_selected
        self.param.depth.checked = self.param.depth_selected
        self.param.fullDepth.checked = self.param.fullDepth_selected
        self.param.voxelDepth.checked = self.param.voxelDepth_selected
        self.param.cgDepth.checked = self.param.cgDepth_selected
        self.param.scale.checked = self.param.scale_selected
        self.param.samplesPerNode.checked = self.param.samplesPerNode_selected
        self.param.iters.checked = self.param.iters_selected
        self.param.polygonMesh.checked = self.param.polygonMesh_selected
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
        contentRect = self.window.content_rect
        panel_width = 15 * layout_context.theme.font_size  # 15 ems wide
        self.widget.frame = gui.Rect(contentRect.x, contentRect.y, contentRect.width - panel_width, contentRect.height)
        self.panel.frame = gui.Rect(self.widget.frame.get_right(), contentRect.y, panel_width, contentRect.height)
    '''
       Input file
    '''
    def _on_filedlg_button(self):
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
        self.plot_pointcloud()

    '''
       Menü bar Quit
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
                cloud = o3d.io.read_point_cloud(path, remove_nan_points=False, remove_infinite_points=False, print_progress=True)
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
                    o3d.io.write_point_cloud(new_path, cloud, write_ascii=True, compressed=False, print_progress=False)
                    self._fileedit.text_value = new_path
                    self.settings.input_file = new_path
                self.actual_geometry = cloud
            else:
                print("[WARNING] Failed to read points", path)

        self.apply_settings()

    def plot_pointcloud(self):
        self.widget.scene.clear_geometry()

        if not self.actual_geometry.is_empty():
            mat = rendering.MaterialRecord()
            mat.shader = "defaultUnlit"
            self.widget.scene.add_geometry("__model__", self.actual_geometry, mat)
            bounds = self.actual_geometry.get_axis_aligned_bounding_box()
            self.widget.setup_camera(60, bounds, bounds.get_center())

    def plot_mesh(self):
        self.widget.scene.clear_geometry()
        path = self.settings.output_file+".ply"
        self.actual_geometry = o3d.io.read_triangle_mesh(path)
        print("Generated "+str(self.actual_geometry))

        if not self.actual_geometry.is_empty():
            mat = rendering.MaterialRecord()
            mat.shader = "unlitLine"
            self.widget.scene.add_geometry("__model__", self.actual_geometry, mat)
            bounds = self.actual_geometry.get_axis_aligned_bounding_box()
            self.widget.setup_camera(60, bounds, bounds.get_center())


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
        self.plot_mesh()

        # apply settings
        self.apply_settings()

    def _on_calculate_uvmap(self):
        image_name = str(self.settings.out_dir)+str(self.texture_name.text_value)
        # run xatlas
        get_texture_from_vertex_color(self.settings.output_file, image_name)

        # update texture image
        img = o3d.io.read_image(str(image_name)+'_texture_map.png')
        self._image_field.update_image(img)

        # apply settings2,4615485866666668713
        self.apply_settings()