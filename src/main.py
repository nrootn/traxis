from PyQt5 import QtWidgets
from mainGUI import MainGui


class ImageDialog(QtWidgets.QMainWindow):
    """Simple wrapper class that creates a window to display GUI."""

    def __init__(self):
        super(ImageDialog, self).__init__()

        self.ui = MainGui()
        self.ui.setupUi(self)


# Main block that executes the application
if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = ImageDialog()

    window.show()
    sys.exit(app.exec_())
