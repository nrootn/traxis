from PyQt5 import QtWidgets
from mainGUI import MainGui


class TraxisApplicationWindow(QtWidgets.QMainWindow):

    """Simple wrapper class that creates a window to display GUI."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Traxis")

        self.ui = MainGui(self)

        self.showMaximized()


# Main block that executes the application
if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = TraxisApplicationWindow()

    window.show()
    sys.exit(app.exec_())
