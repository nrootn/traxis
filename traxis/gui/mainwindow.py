import sys
import os
from PyQt5 import QtWidgets, QtGui
from traxis.gui import maingui


class TraxisApplicationWindow(QtWidgets.QMainWindow):

    """Subclass of QMainWindow, which sets the window's title and icon, and
    instantiates the MainWidget, setting it as the window's central widget.
    """

    def __init__(self):

        super().__init__()

        # set window title
        self.setWindowTitle("Traxis")

        # set the window's icon (it is kept in the root traxis directory)
        # note: this icon won't get displayed on a Mac
        icon = QtGui.QIcon()
        basePath = sys.path[0]
        icon.addPixmap(QtGui.QPixmap(os.path.join(basePath, "traxis.png")))
        self.setWindowIcon(icon)

        # initialize MainWidget and set it as the window's central widget
        self.setCentralWidget(maingui.MainWidget())
