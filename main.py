import open3d.visualization.gui as gui
from src.GuiInterface import GUI
import platform
import os




def main():
    '''
    Main method of the Computer Graphics Project Group 'Point cloud to mesh'.
    Start the application to run by creating an instance of our GUIInterface
    :return: None
    '''
    # initalize the application
    gui.Application.instance.initialize()

    main_dir = os.getcwd() # main directory
    my_os = platform.system() #operation system

    w = GUI(main_dir, my_os)

    # Run the event loop.
    gui.Application.instance.run()


if __name__ == "__main__":
    main()