from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants


class TangentLine(object):

    def __init__(self, scene):

        self.scene = scene
        self.line = None

    def draw(self, qlinef, width):

        if self.line:
            self.scene.removeItem(self.line)

        if width < 1: # set minimum width
            width = 1

        self.line = QtWidgets.QGraphicsLineItem(qlinef)

        linePen = QtGui.QPen(constants.TANGENTLINECOLOR)
        linePen.setWidth(width)
        self.line.setPen(linePen)

        self.scene.addItem(self.line)

    def rescale(self, width):

        if width < 1: # set minimum width
            width = 1

        if self.line:
            newLinePen = self.line.pen()
            newLinePen.setWidth(width)
            self.line.setPen(newLinePen)

    def reset(self):

        if self.line:
            self.scene.removeItem(self.line)

        self.line = None
