#!/usr/bin/env python3

from PyQt5 import QtWidgets
from mainGUI import MainGui


class TraxisApplicationWindow(QtWidgets.QMainWindow):

    """Simple wrapper class that creates a window to display GUI."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Traxis")

        self.ui = MainGui(self)


# Main block that executes the application
if __name__ == '__main__':

    import sys
    import ctypes

    # if running on Windows, create an application user model id for this app
    # so that a custom taskbar icon can be used
    if hasattr(ctypes, 'windll'):
        appId = 'traxis.0.2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelId(appId)

    app = QtWidgets.QApplication(sys.argv)
    window = TraxisApplicationWindow()

    window.show()
    sys.exit(app.exec_())
