import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from mainGUI import mainGUI



# simple wrapper to display the GUI
class ImageDialog(QMainWindow):
    def __init__(self):
        super(ImageDialog, self).__init__()
        
        self.ui = mainGUI()
        self.ui.setupUi(self)


# to start the app
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageDialog()

    window.show()
    sys.exit(app.exec_())
