from src.InputParser import *
from src.PointCloud import *

# Ply files
BUNNY = "StanfordBunny.ply"
SKELETON = "SkeletonHand.ply"
BUDDHA = "HappyBuddha.ply"
DRAGON = "Dragon.ply"
# pcd files
BUNNY2 = "bunny.pcd"

# Visualization
SHOW_NORMAL = True
VISUALIZE = [True, SHOW_NORMAL]


if __name__ == '__main__':

    # |1| Parser: import ply/pcd file

    file = InputParser(BUNNY2, VISUALIZE)
    print('FILE INFO %*s: %*s' % (10, file.filename, 10, file.datatype))

    #     Initialize Pointcloud Obj.
    pcd = Pointcloud(file)





















