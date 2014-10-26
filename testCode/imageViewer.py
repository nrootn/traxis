from PyQt5 import QtCore, QtWidgets, QtGui

class ImageViewer(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(ImageViewer, self).__init__(parent)

		self.scaleFactor = 1.0
                
		self.scene = QtWidgets.QGraphicsScene()
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.pixmap_item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap('/home/chris/Pictures/electrode.png'), None)
		self.scene.addItem(self.pixmap_item)
		self.pixmap_item.mousePressEvent = self.pixelSelect
		self.click_positions = []

		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollArea.setWidget(self.view)

		self.openButton = QtWidgets.QPushButton('Open Image', self)
		self.openButton.clicked.connect(self.open)

		self.zoomInButton = QtWidgets.QPushButton('Zoom In', self)
		self.zoomInButton.clicked.connect(self.zoomIn)
		self.zoomOutButton = QtWidgets.QPushButton('Zoom Out', self)
		self.zoomOutButton.clicked.connect(self.zoomOut)

		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(self.scrollArea)
		layout.addWidget(self.openButton)
		layout.addWidget(self.zoomInButton)
		layout.addWidget(self.zoomOutButton)

		self.setLayout(layout)

	def pixelSelect(self, event):
		self.click_positions.append(event.pos())
		if len(self.click_positions) < 4:
			return
		pen = QtGui.QPen(QtCore.Qt.red)
		self.scene.addPolygon(QtGui.QPolygonF(self.click_positions), pen)
		for point in self.click_positions:
			self.scene.addEllipse(point.x(), point.y(), 2, 2, pen)
		self.click_positions = []

	def open(self):
		fileName = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", QtCore.QDir.currentPath())
		if fileName:
			qimage = QtGui.QImage()
			image = qimage.load(fileName[0])
			if not image:
				QtWidgets.QMessageBox.information(self, "Image Viewer", "Cannot load {}.".format(fileName))
				return
			self.pixmap_item.setPixmap(QtGui.QPixmap.fromImage(qimage))



	def zoomIn(self):
		self.scaleImage(1.25)

	def zoomOut(self):
		self.scaleImage(0.8)

	def scaleImage(self, factor):
		self.scaleFactor *= factor
		
		self.view.scale(factor,factor)
		self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
		self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)


	def adjustScrollBar(self, scrollBar, factor):
		scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))
		
if __name__ == '__main__':
	import sys

	app = QtWidgets.QApplication(sys.argv)
	imageViewer = ImageViewer()
	imageViewer.show()
	sys.exit(app.exec_())
