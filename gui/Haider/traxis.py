import sys
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from traxisui import Ui_traxis


class ImageDialog(QMainWindow):
    def __init__(self):
        super(ImageDialog, self).__init__()
        
        # Set up the user interface from Designer.
        self.ui = Ui_traxis()
        self.ui.setupUi(self)
        
        # Make some local modifications.
        #self.ui.colorDepthCombo.addItem("2 colors (1 bit per pixel)")
        
        # Connect up the buttons.
        #self.ui.okButton.clicked.connect(self.accept)
        #self.ui.cancelButton.clicked.connect(self.reject)


app = QApplication(sys.argv)
window = ImageDialog()

window.show()
sys.exit(app.exec_())
