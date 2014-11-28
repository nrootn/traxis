from PyQt5 import QtWidgets, QtGui, QtCore


class MarkerList(QtWidgets.QListWidget):

    """Track Marker list class."""

    def __init__(self, parent=None):

        super().__init__(parent)

    def addMarker(self, x, y, size, width, scene):

        lastItem = self.item(self.count()-1)
        if lastItem:
            newMarkerId = lastItem.id + 1
        else:
            newMarkerId = 1

        newMarker = TrackMarker(newMarkerId, x, y, size, width, self)

        self.setCurrentItem(newMarker)

        scene.addItem(newMarker.ellipse)

        return newMarker

    def deleteMarker(self, marker):

        marker.ellipse.scene().removeItem(marker.ellipse)

        markerRow = self.row(marker)
        self.takeItem(markerRow)

    def empty(self):

        for row in range(self.count()):
            self.item(row).ellipse.scene().removeItem(self.item(row).ellipse)

        self.clear()

    def setStartPoint(self, marker):
        
        oldStartPoint = self.getStartPoint()
        if oldStartPoint:
            oldStartPoint.setDesignation()

        marker.setDesignation('start')

    def setEndPoint(self, marker):
        
        oldEndPoint = self.getEndPoint()
        if oldEndPoint:
            oldEndPoint.setDesignation()

        marker.setDesignation('end')

    def getStartPoint(self):
        
        for row in range(self.count()):
            if self.item(row).designation == 'start':
                return self.item(row)

        return None

    def getEndPoint(self):
        
        for row in range(self.count()):
            if self.item(row).designation == 'end':
                return self.item(row)

        return None

    def highlightCurrent(self):
        
        for row in range(self.count()):
            self.item(row).recolor()

    def selectNext(self):

        if self.currentRow() == -1 or self.currentRow() == self.count() - 1:
            return
        else:
            self.setCurrentRow(self.currentRow() + 1)

    def selectPrevious(self):

        if self.currentRow() == -1 or self.currentRow() == 0:
            return
        else:
            self.setCurrentRow(self.currentRow() - 1)

class TrackMarker(QtWidgets.QListWidgetItem):

    """Track marker class."""

    def __init__(self, markerId, x, y, size, width, parent=None):

        self.id = markerId

        self.designation = None

        super().__init__("Point {}".format(self.id), parent)

        if size < 2: # set minimum size
            size = 2

        if width < 1: # set minimum width
            width = 1

        ellipseRect = QtCore.QRectF(x, y, size, size)
        ellipseRect.moveCenter(QtCore.QPointF(x, y))
        self.ellipse = QtWidgets.QGraphicsEllipseItem(ellipseRect)

        ellipsePen = QtGui.QPen(QtGui.QColor(176, 30, 125))
        ellipsePen.setWidth(width)
        self.ellipse.setPen(ellipsePen)

    def setDesignation(self, designation=None):

        if designation not in [None, 'start', 'end']:
            return
        self.designation = designation

        if designation == 'start':
            self.setText("s - Point {}".format(self.id))
        elif designation == 'end':
            self.setText("e - Point {}".format(self.id))
        else:
            self.setText("Point {}".format(self.id))

    def recolor(self):

        newPen = self.ellipse.pen()

        if self.isSelected():
            newPen.setColor(QtGui.QColor(235, 233, 0))
        elif self.designation == 'start':
            newPen.setColor(QtGui.QColor(0, 186, 186))
        elif self.designation == 'end':
            newPen.setColor(QtGui.QColor(34, 197, 25))
        else:
            newPen.setColor(QtGui.QColor(176, 30, 125))

        self.ellipse.setPen(newPen)

    def move(self, dx, dy):

        self.ellipse.moveBy(dx, dy)

    def rescale(self, size, width):

        if size < 2: # set minimum size
            size = 2

        if width < 1: # set minimum width
            width = 1

        newRect = self.ellipse.rect()
        newRect.setWidth(size)
        newRect.setHeight(size)
        newRect.moveCenter(self.ellipse.rect().center())
        self.ellipse.setRect(newRect)

        newPen = self.ellipse.pen()
        newPen.setWidth(width)
        self.ellipse.setPen(newPen)
