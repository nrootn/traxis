import sys

from PyQt5.QtWidgets import QApplication, QMainWindow
from mainGUI import mainGUI


# Simple wrapper class that creates window to display GUI
class ImageDialog(QMainWindow):

    def __init__(self):
        super(ImageDialog, self).__init__()

        self.ui = mainGUI()
        self.ui.setupUi(self)


# Main block that executes the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageDialog()

    window.show()
    sys.exit(app.exec_())
