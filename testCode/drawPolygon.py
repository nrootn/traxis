#!/usr/bin/env python
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from PyQt5 import QtGui

class MainWidget(QWidget):
    def __init__(self, parent=None):
        #QtWidgets.__init__(self)
        super(MainWidget, self).__init__(parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.pixmap_item = QGraphicsPixmapItem(QtGui.QPixmap('/Users/Haider/untitled/img017b.png'), None)
        self.scene.addItem(self.pixmap_item)
        self.pixmap_item.mousePressEvent = self.pixelSelect
        self.click_positions = []

    def pixelSelect(self, event):
        self.click_positions.append(event.pos())
        if len(self.click_positions) < 4:
            return
        pen = QtGui.QPen(Qt.red)
        self.scene.addPolygon(QtGui.QPolygonF(self.click_positions), pen)
        for point in self.click_positions:
            self.scene.addEllipse(point.x(), point.y(), 2, 2, pen)
        self.click_positions = []


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWidget()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())
