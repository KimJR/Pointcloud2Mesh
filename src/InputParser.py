from plyfile import PlyData
import os


class InputParser:

    PCD = ".pcd"
    PLY = ".ply"
    FOLDER = "/pcd/"
    PATH = str(os.path.abspath(os.getcwd()))+FOLDER

    def __init__(self, filename, visualize):
        self.filename = filename
        self.visualize = visualize

        self.filetype = self.check_file_type()
        self.datatype = []
        self.data = []

        self.progress()

    def progress(self):
        print('Read file %*s ' % (10, self.filename))

        if self.filetype == "pcd":
            lst = self.file_to_list()
            self.check_header_pcd(lst)

        if self.filetype == "ply":
            self.read_ply()



    """
    check if file is pcd/ply file
    """
    def check_file_type(self):
        if self.PCD in self.filename:
            return "pcd"
        if self.PLY in self.filename:
            return "ply"
        else:
            print("no pcd or ply file found")

    # PLY FILES

    """
    check header variables of ply file
    """
    def read_ply(self):

        plydata = PlyData.read(self.PATH+self.filename)
        self.data = plydata.elements[0].data.tolist()

        for row in plydata.elements[0].properties:
            self.datatype.append(str(row).split(" ")[2])



    # PCD FILES

    """
    read pcd file
    """
    def file_to_list(self):
        pcd_list = []
        with open(self.PATH+self.filename) as file:
            lines = file.readlines()
            for line in lines:
                l = line.strip()
                pcd_list.append(l.split(" "))
        lst = [ele for ele in pcd_list if ele != []]
        return lst

    """
    check header variables of pcd file
    """
    def check_header_pcd(self, lst):
        DATA = False

        for row in lst:

            if DATA:
                self.data.append(list(map(float, row)))

            if "FIELDS" in row:
                self.datatype = row
                self.datatype.remove("FIELDS")

            if "DATA" in row:
                DATA = True

