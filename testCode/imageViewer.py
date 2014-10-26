from PyQt5 import QtCore, QtWidgets, QtGui

class ImageViewer(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(ImageViewer, self).__init__(parent)

		self.scaleFactor = 1.0

		self.imageLabel = QtWidgets.QLabel()
		self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
		self.imageLabel.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
		self.imageLabel.setScaledContents(True)
		self.imageLabel.setPixmap(QtGui.QPixmap('/home/chris/Pictures/electrode.png'))

		self.scrollArea = QtWidgets.QScrollArea()
		self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
		self.scrollArea.setWidget(self.imageLabel)

		self.zoomInButton = QtWidgets.QPushButton('Zoom In', self)
		self.zoomInButton.clicked.connect(self.zoomIn)
		self.zoomOutButton = QtWidgets.QPushButton('Zoom Out', self)
		self.zoomOutButton.clicked.connect(self.zoomOut)

		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(self.scrollArea)
		layout.addWidget(self.zoomInButton)
		layout.addWidget(self.zoomOutButton)

		self.setLayout(layout)

	def zoomIn(self):
		self.scaleImage(1.25)

	def zoomOut(self):
		self.scaleImage(0.8)

	#def normalSize(self):
	#	self.imageLabel.adjustSize()
	#	self.scaleFactor = 1.0

	def scaleImage(self, factor):
		self.scaleFactor *= factor
		self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

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
