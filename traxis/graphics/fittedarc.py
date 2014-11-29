from PyQt5 import QtGui, QtCore, QtWidgets

class ArcItem(QtWidgets.QGraphicsEllipseItem):

    def paint(self, painter, option, widget=0):
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())

class MomentumArc(object):

    def __init__(self, scene):

        self.scene = scene
        self.centralArc = None
        self.outerArc = None
        self.innerArc = None

    def draw(self, centerX, centerY, radius, startAngle, spanAngle, dl, width):

        self.reset()

        if width < 1: # set minimum width
            width = 1

        momentumPen = QtGui.QPen(QtGui.QColor(33, 95, 147))
        momentumPen.setWidth(width)

        centralRect = QtCore.QRectF(centerX, centerY, 2 * radius, 2 * radius)
        centralRect.moveCenter(QtCore.QPointF(centerX, centerY))
        self.centralArc = ArcItem(centralRect)
        self.centralArc.setStartAngle(16 * startAngle)
        self.centralArc.setSpanAngle(16 * spanAngle)
        self.centralArc.setPen(momentumPen)

        momentumPen.setStyle(QtCore.Qt.DashDotLine)

        outerRect = QtCore.QRectF(
            centerX, centerY, 2 * (radius + dl), 2 * (radius + dl))
        outerRect.moveCenter(QtCore.QPointF(centerX, centerY))
        self.outerArc = ArcItem(outerRect)
        self.outerArc.setStartAngle(16 * startAngle)
        self.outerArc.setSpanAngle(16 * spanAngle)
        self.outerArc.setPen(momentumPen)

        innerRect = QtCore.QRectF(
            centerX, centerY, 2 * (radius - dl), 2 * (radius - dl))
        innerRect.moveCenter(QtCore.QPointF(centerX, centerY))
        self.innerArc = ArcItem(innerRect)
        self.innerArc.setStartAngle(16 * startAngle)
        self.innerArc.setSpanAngle(16 * spanAngle)
        self.innerArc.setPen(momentumPen)

        self.scene.addItem(self.centralArc)
        self.scene.addItem(self.outerArc)
        self.scene.addItem(self.innerArc)

    def updateArcs(self, dl):

        if not self.centralArc:
            return

        centralWidth = self.centralArc.rect().width()

        newOuterRect = self.outerArc.rect()
        newOuterRect.setWidth(centralWidth + 2 * dl)
        newOuterRect.setHeight(centralWidth + 2 * dl)
        newOuterRect.moveCenter(self.outerArc.rect().center())
        self.outerArc.setRect(newOuterRect)

        newInnerRect = self.innerArc.rect()
        newInnerRect.setWidth(centralWidth - 2 * dl)
        newInnerRect.setHeight(centralWidth - 2 * dl)
        newInnerRect.moveCenter(self.innerArc.rect().center())
        self.innerArc.setRect(newInnerRect)

    def rescale(self, width):

        if width < 1: # set minimum width
            width = 1

        if not self.centralArc:
            return

        newPen = self.centralArc.pen()
        newPen.setWidth(width)
        self.centralArc.setPen(newPen)

        newPen.setStyle(QtCore.Qt.DashDotLine)
        self.outerArc.setPen(newPen)
        self.innerArc.setPen(newPen)

    def reset(self):

        if self.centralArc:
            self.scene.removeItem(self.centralArc)
        if self.outerArc:
            self.scene.removeItem(self.outerArc)
        if self.innerArc:
            self.scene.removeItem(self.innerArc)

        self.centralArc = None
        self.outerArc = None
        self.innerArc = None
