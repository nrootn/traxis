from PyQt5 import QtWidgets, QtGui, QtCore


class ReferenceLine(object):

    def __init__(self, scene):

        self.scene = scene
        self.initialPoint = None
        self.finalPoint = None
        self.line = None

    def setInitialPoint(self, x, y, size, width):

        self.reset()

        if size < 1: # set minimum size
            size = 1

        if width < 1: # set minimum width
            width = 1

        initialRect = QtCore.QRectF(x, y, size, size)
        initialRect.moveCenter(QtCore.QPointF(x, y))
        self.initialPoint = QtWidgets.QGraphicsEllipseItem(initialRect)

        initialPen = QtGui.QPen(QtGui.QColor(243, 42, 31))
        initialPen.setWidth(width)
        self.initialPoint.setPen(initialPen)

        self.scene.addItem(self.initialPoint)

    def setFinalPoint(self, x, y, size, width):

        if not self.initialPoint or self.finalPoint:
            return

        if size < 1: # set minimum size
            size = 1

        if width < 1: # set minimum width
            width = 1

        finalRect = QtCore.QRectF(x, y, size, size)
        finalRect.moveCenter(QtCore.QPointF(x, y))
        self.finalPoint = QtWidgets.QGraphicsEllipseItem(finalRect)

        finalPen = QtGui.QPen(QtGui.QColor(243, 42, 31))
        finalPen.setWidth(width)
        self.finalPoint.setPen(finalPen)

        self.scene.addItem(self.finalPoint)

        if self.finalPoint.rect().center() == self.initialPoint.rect().center():
            self.reset()

    def drawLine(self, endX, endY, width):

        if not self.initialPoint or self.finalPoint:
            return

        if self.line:
            self.scene.removeItem(self.line)

        if width < 1: # set minimum width
            width = 1

        startX = self.initialPoint.rect().center().x()
        startY = self.initialPoint.rect().center().y()
        self.line = QtWidgets.QGraphicsLineItem(startX, startY, endX, endY)

        linePen = QtGui.QPen(QtGui.QColor(243, 42, 31))
        linePen.setWidth(width)
        self.line.setPen(linePen)

        self.scene.addItem(self.line)

    def rescale(self, size, width):

        if size < 1: # set minimum size
            size = 1

        if width < 1: # set minimum width
            width = 1

        if self.initialPoint:
            newInitialRect = self.initialPoint.rect()
            newInitialRect.setWidth(size)
            newInitialRect.setHeight(size)
            newInitialRect.moveCenter(self.initialPoint.rect().center())
            self.initialPoint.setRect(newInitialRect)

            newInitialPen = self.initialPoint.pen()
            newInitialPen.setWidth(width)
            self.initialPoint.setPen(newInitialPen)

        if self.finalPoint:
            newFinalRect = self.finalPoint.rect()
            newFinalRect.setWidth(size)
            newFinalRect.setHeight(size)
            newFinalRect.moveCenter(self.finalPoint.rect().center())
            self.finalPoint.setRect(newFinalRect)

            newFinalPen = self.finalPoint.pen()
            newFinalPen.setWidth(width)
            self.finalPoint.setPen(newFinalPen)

        if self.line:
            newLinePen = self.line.pen()
            newLinePen.setWidth(width)
            self.line.setPen(newLinePen)

    def reset(self):

        if self.initialPoint:
            self.scene.removeItem(self.initialPoint)
        if self.finalPoint:
            self.scene.removeItem(self.finalPoint)
        if self.line:
            self.scene.removeItem(self.line)

        self.initialPoint = None
        self.finalPoint = None
        self.line = None
