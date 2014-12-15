# Copyright (C) 2014 Syed Haider Abidi, Nooruddin Ahmed and Christopher Dydula
#
# This file is part of traxis.
#
# traxis is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# traxis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with traxis.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants


class ReferenceLine(object):

    """Angle reference line class. This class is a container for two
    QGraphicsEllipseItem objects and one QGraphicsLineItem object
    which together form an angle reference. This class implements
    methods for manipulating the graphics items it contains such
    that they function as a unit. A ReferenceLine object is to be
    added to a GUI as one would add a QWidget.
    """

    def __init__(self):
        """Initialize this object's attributes, setting them to None."""

        # the initialPoint attribute is a QGraphicsEllipseItem or None, if no
        # initialPoint has been created
        self.initialPoint = None
        # the finalPoint attribute is a QGraphicsEllipseItem or None, if no
        # finalPoint has been created
        self.finalPoint = None
        # the line attribute is a QGraphicsLineItem or None, if no
        # line has been created
        self.line = None

    def setInitialPoint(self, x, y, size, width, scene):
        """First, reset this reference line object since setting a new initial
        point means that a new reference line is being created. Then create a 
        new ellipse item at position (x, y) with size size and pen width width.
        Set the ellipse as this reference line's initialPoint attribute and add
        the newly created ellipse to scene, a QGraphicsScene.
        """

        # reset this reference line object
        self.reset()

        # set a minimum rect size
        if size < 1:
            size = 1

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a rect for the initial point with the given
        # coordinates and size (set the width and height of the rect to size)
        initialRect = QtCore.QRectF(x, y, size, size)
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        initialRect.moveCenter(QtCore.QPointF(x, y))
        # create a QGraphicsEllipseItem using the rect created above. Set it
        # as the reference line's initialPoint attribute.
        self.initialPoint = QtWidgets.QGraphicsEllipseItem(initialRect)

        # create a pen for the initial point using the reference line colour
        initialPen = QtGui.QPen(constants.REFLINECOLOR)
        # set the width of the pen to width
        initialPen.setWidth(width)
        # set the newly created pen as the inital point's pen
        self.initialPoint.setPen(initialPen)

        # add the initial point to the graphics scene
        scene.addItem(self.initialPoint)

    def setFinalPoint(self, x, y, size, width, scene):
        """Create a new ellipse item at position (x, y) with size size and pen
        width width. Set the ellipse as this reference line's finalPoint
        attribute and add the newly created ellipse to scene, a QGraphicsScene.
        """

        # set a minimum rect size
        if size < 1:
            size = 1

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a rect for the final point with the given
        # coordinates and size (set the width and height of the rect to size)
        finalRect = QtCore.QRectF(x, y, size, size)
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        finalRect.moveCenter(QtCore.QPointF(x, y))
        # create a QGraphicsEllipseItem using the rect created above. Set it
        # as the reference line's finalPoint attribute.
        self.finalPoint = QtWidgets.QGraphicsEllipseItem(finalRect)

        # create a pen for the initial point using the reference line colour
        finalPen = QtGui.QPen(constants.REFLINECOLOR)
        # set the width of the pen to width
        finalPen.setWidth(width)
        # set the newly created pen as the final point's pen
        self.finalPoint.setPen(finalPen)

        # add the final point to the graphics scene
        scene.addItem(self.finalPoint)

        # if the coordinates of the final point are the same as the initial
        # point, reset the reference line altogether
        if self.finalPoint.rect().center() == self.initialPoint.rect().center():
            self.reset()

    def drawLine(self, endX, endY, width, scene):
        """First, remove the existing line item, if any, from the graphics
        scene. Then create a new line item whose start point coordinates are
        the coordinates of initialPoint, whose end point coordinates are
        (endX, endY), and with pen width width. Add the newly created line
        to scene, a QGraphicsScene. 
        """

        # if this reference line already has a line attribute, remove it from
        # the graphics scene
        if self.line:
            scene.removeItem(self.line)

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a QGraphicsLineItem with the appropriate start and end
        # coordinates
        startX = self.initialPoint.rect().center().x()
        startY = self.initialPoint.rect().center().y()
        self.line = QtWidgets.QGraphicsLineItem(startX, startY, endX, endY)

        # create a pen for the line using the reference line colour
        linePen = QtGui.QPen(constants.REFLINECOLOR)
        # set the width of the pen to width
        linePen.setWidth(width)
        # set the newly created pen as the line's pen
        self.line.setPen(linePen)

        # add the line to the graphics scene
        scene.addItem(self.line)

    def rescale(self, size, width):
        """Set the size of the initial and final point to size and set the pen
        width of the initial and final point and line to width.
        """

        # set a minimum rect size
        if size < 1:
            size = 1

        # set a minimum pen width
        if width < 1:
            width = 1

        # if the initialPoint attribute is not None
        if self.initialPoint:
            # create a new rect, starting from the existing rect of the initial
            # point
            newInitialRect = self.initialPoint.rect()
            # set the width and height of the new rect
            newInitialRect.setWidth(size)
            newInitialRect.setHeight(size)
            # move the rect's center to match that of the original rect's (the
            # center gets shifted when resizing)
            newInitialRect.moveCenter(self.initialPoint.rect().center())
            # set the resized rect as the initial point's rect
            self.initialPoint.setRect(newInitialRect)

            # create a new pen, starting from the existing pen of the initial
            # point
            newInitialPen = self.initialPoint.pen()
            # set the width of the new pen
            newInitialPen.setWidth(width)
            # set the resized pen as the initial point's pen
            self.initialPoint.setPen(newInitialPen)

        # if the finalPoint attribute is not None
        if self.finalPoint:
            # create a new rect, starting from the existing rect of the final
            # point
            newFinalRect = self.finalPoint.rect()
            # set the width and height of the new rect
            newFinalRect.setWidth(size)
            newFinalRect.setHeight(size)
            # move the rect's center to match that of the original rect's (the
            # center gets shifted when resizing)
            newFinalRect.moveCenter(self.finalPoint.rect().center())
            # set the resized rect as the final point's rect
            self.finalPoint.setRect(newFinalRect)

            # create a new pen, starting from the existing pen of the final
            # point
            newFinalPen = self.finalPoint.pen()
            # set the width of the new pen
            newFinalPen.setWidth(width)
            # set the resized pen as the final point's pen
            self.finalPoint.setPen(newFinalPen)

        # if the line attribute is not None
        if self.line:
            # create a new pen, starting from the existing pen of the line
            newLinePen = self.line.pen()
            # set the width of the new pen
            newLinePen.setWidth(width)
            # set the resized pen as the line's pen
            self.line.setPen(newLinePen)

    def isBeingDrawn(self):
        """Return True if the ReferenceLine object is in the process of being
        drawn, False otherwise.
        """

        # line is in process of being drawn if the initial point exists but the
        # final point does not
        return self.initialPoint and not self.finalPoint

    def reset(self):
        """Remove the reference line's attributes from their graphics scene and
        reset them to None.
        """

        # if the initial point, final point and/or line exist, remove them from
        # their graphics scene
        if self.initialPoint:
            self.initialPoint.scene().removeItem(self.initialPoint)
        if self.finalPoint:
            self.finalPoint.scene().removeItem(self.finalPoint)
        if self.line:
            self.line.scene().removeItem(self.line)

        # reset the reference line's attributes to None
        self.initialPoint = None
        self.finalPoint = None
        self.line = None
