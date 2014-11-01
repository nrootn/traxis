import sys
from PyQt5.QtWidgets import  QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QDir
from mainUi import Ui_traxis as skeletonGUI

## Inherit from the base Skeleton Gui class and implement the logic here
## makes the code independant from the gui and its changes
class mainGUI(skeletonGUI):
    def __init__(self):
        super(skeletonGUI, self).__init__()

    # Initalization and connection of buttons
    def setupUi(self, traxis):
        skeletonGUI.setupUi(self, traxis)
        
        # display a simple bkg image
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        # load a blank image as a workaround to a bug inside QT
        # It will not load an image if a blank is not loaded
        self.pixmap_item = QGraphicsPixmapItem(QPixmap('bkgPicture.png'), None)
        self.scene.addItem(self.pixmap_item)
        self.scrollArea.setWidget(self.view)
        self.open()

    
    ## TODO:: Chris to comment this
    ## to open the file
    def open(self):
        fileName = QFileDialog.getOpenFileName(self.centralWidget, "Open File", QDir.currentPath())
        if fileName:
            qimage = QImage()
            image = qimage.load(fileName[0])
        if not image:
            QMessageBox.information(self, "Image Viewer", "Cannot load {}.".format(fileName))
            return
	
        self.pixmap_item.setPixmap(QPixmap.fromImage(qimage))
