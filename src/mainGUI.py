import sys
from PyQt5.QtWidgets import  QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPen, QPolygonF
from PyQt5.QtCore import QDir, Qt, QRectF, QPointF
from skeleton import Ui_skeleton as skeletonGUI

## Inherit from the base Skeleton Gui class and implement the logic here
## makes the code independant from the gui and its changes
class mainGUI(skeletonGUI):
	def __init__(self):
		super(skeletonGUI, self).__init__()

	# Initalization and connection of buttons
	def setupUi(self, skeleton):
		skeletonGUI.setupUi(self, skeleton)

		# display a simple bkg image
		self.scene = QGraphicsScene()
		self.view = QGraphicsView(self.scene)

		# load a blank image as a workaround to a bug inside QT
		# It will not load an image if a blank is not loaded
		self.pixmap_item = QGraphicsPixmapItem(QPixmap('bkgPicture.png'), None)
		self.scene.addItem(self.pixmap_item)
		self.scrollArea.setWidget(self.view)

		# connect open button
		self.btn_openImage.clicked.connect(self.openImage)

		# Connect the zoom button		 
		self.btn_ZoomIn.clicked.connect(self.zoomIn)
		self.btn_ZoomOut.clicked.connect(self.zoomOut)

		# Connecting the drawing of points
		self.sizeOfEllipse = 10
		self.nEllipseDrawn = 0
		self.mapNametoPoint = {}
		self.pixmap_item.mousePressEvent = self.pixelSelect

		# connect the list widgest 
		self.listWidget_points.keyPressEvent = self.testkeyPressEvent

		# Connect the reset button
		self.btn_reset.clicked.connect(self.resetImage)
 
		# For debugging
		self.nUserClickOnPicture = 0
		
	# This functions draws the ellipse
	def pixelSelect(self, event):
		# Place an event only if place button is checked
		if not self.btn_placeMar.isChecked():
			# count the number of times user has click on the picture
			# if more than 5 times, display a help message
			self.nUserClickOnPicture += 1
			if self.nUserClickOnPicture == 5:
				self.nUserClickOnPicture = 0;
				self.textBrowser_consoleOutput.append("HELP - To place track marker, first select Place Track Marker button")  
			return

		# select the colour of ellipse draw
		pen = QPen(Qt.red)
		# size of ellipse drawn
		size = self.sizeOfEllipse 
		
		# add the ellipse
		# this contains the drawing rectangle
		drawRec = QRectF(event.pos().x(), event.pos().y(), size, size)
		# translate it such that center of the box matches the position clicked
		drawRec.moveCenter(QPointF(event.pos().x(), event.pos().y()))
		self.scene.addEllipse(drawRec, pen)

		# update the widget
		self.nEllipseDrawn += 1
		self.listWidget_points.addItem('Point %s' % self.nEllipseDrawn)

		# add the drawn point to the map
		itemList = self.scene.items()
		# the most current draw item is on the top of the list		  
		self.mapNametoPoint['Point '+str(self.nEllipseDrawn)] = itemList[0]

	def testkeyPressEvent(self, event):
		dx = 0
		dy = 0
		if event.key() == Qt.Key_W:
			dy = -1
		elif event.key() == Qt.Key_S:
			dy = 1
		elif event.key() == Qt.Key_D:
			dx = 1	
		elif event.key() == Qt.Key_A:
			dx = -1
		print(self.listWidget_points.currentItem().text())
		self.mapNametoPoint[self.listWidget_points.currentItem().text()].moveBy(dx, dy)

	## TODO:: Chris to comment this
	## to open the file
	def openImage(self):
		fileName = QFileDialog.getOpenFileName(self.centralWidget, "Open File", QDir.currentPath())
		if fileName:
			qimage = QImage()
			image = qimage.load(fileName[0])
		if not image:
			QMessageBox.information(self, "Image Viewer", "Cannot load {}.".format(fileName))
			return
		self.pixmap_item.setPixmap(QPixmap.fromImage(qimage))
		
		# reset everything when a new image is loaded
		self.resetImage()


	## to reset the image
	def resetImage(self):
		# to reset any transformation on the image		  
		self.view.resetTransform()
		
		# remove any drawn image
		itemList = self.scene.items()
		for i in itemList:
			# don't remove the actual image
			if(i.__class__.__name__ == 'QGraphicsPixmapItem'):
				continue
			self.scene.removeItem(i)

		# reset any text on the console
		self.textBrowser_consoleOutput.clear()

		# reset the number of points drawn
		self.nEllipseDrawn = 0

		# clear the list of points
		self.listWidget_points.clear()
		

	# Action button for Zoom in
	def zoomIn(self):
		self.scaleImage(1.25)
	
	# Action button for Zoom out
	def zoomOut(self):
		self.scaleImage(0.8)

	# Functions that scales the image
	def scaleImage(self, factor):
		self.view.scale(factor,factor)
		self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
		self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

	# to change the scroll bar size
	def adjustScrollBar(self, scrollBar, factor):
		scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2))) 

