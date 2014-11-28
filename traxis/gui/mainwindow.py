import sys
import os
from PyQt5 import QtWidgets, QtGui
from traxis.gui import maingui


class TraxisApplicationWindow(QtWidgets.QMainWindow):

    """Simple wrapper class that creates a window to display GUI."""

    def __init__(self):
        super().__init__()

        # set window title
        self.setWindowTitle("Traxis")

        # set the window's icon
        icon = QtGui.QIcon()
        basePath = sys.path[0]
        icon.addPixmap(QtGui.QPixmap(os.path.join(basePath, "traxis.png")))
        self.setWindowIcon(icon)

        # set the window's UI
        self.ui = maingui.MainGui()

        # set the window's central widget
        self.setCentralWidget(self.ui.baseWidget)

        # set keyboard focus to the graphics view by default
        self.ui.sceneView.setFocus()
