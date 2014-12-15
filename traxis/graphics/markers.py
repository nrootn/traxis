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


class MarkerList(QtWidgets.QListWidget):

    """Track Marker list class. Instantiate by optionally passing a parent
    widget. This class subclasses QListWidget and is intended to contain
    TrackMarker objects (as opposed to regular QListWidgetItem objects).
    This class implements a number of methods to work with the extra
    features that TrackMarker adds to QListWidgetItem.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

    def addMarker(self, x, y, size, width, scene):
        """Create a new TrackMarker object at position (x, y) with size size
        and pen width width. Set this MarkerList as the new marker's parent,
        set the new marker as this list's current item and add the new marker's
        ellipse to scene, a QGraphicsScene. Return the TrackMarker object.
        """

        # get the last item in the marker list. The last item will always have
        # the largest id number so incrementing its id will give a unique id
        # for the new marker
        lastItem = self.item(self.count()-1)
        # if the list isn't empty...
        if lastItem:
            newMarkerId = lastItem.id + 1
        # otherwise if it is empty, set the new marker's id to 1
        else:
            newMarkerId = 1

        # create the new TrackMarker object, passing this list widget as the
        # parent
        newMarker = TrackMarker(newMarkerId, x, y, size, width, self)

        # set the newly created marker as the current item for this list
        self.setCurrentItem(newMarker)

        # add the new marker's ellipse to the graphics scene
        scene.addItem(newMarker.ellipse)

        # return the new TrackMarker object
        return newMarker

    def deleteMarker(self, marker):
        """Remove the TrackMarker object marker from this marker list."""

        # remove the marker's ellipse from its graphics scene
        marker.ellipse.scene().removeItem(marker.ellipse)

        # get the row number of marker within this list and then pass it to
        # the takeItem method to remove marker from this list
        markerRow = self.row(marker)
        self.takeItem(markerRow)

    def empty(self):
        """Remove all TrackMarker objects from this marker list."""

        # loop over all the markers in this list and remove each marker's
        # ellipse from the graphics scene
        for row in range(self.count()):
            marker = self.item(row)
            marker.ellipse.scene().removeItem(marker.ellipse)

        # remove all markers from this list
        self.clear()

    def rescale(self, size, width):
        """Set the size of each marker's ellipse in this list to size and the
        pen width of each marker's ellipse to width.
        """

        # loop over all the markers in this list and rescale them one by one
        for row in range(self.count()):
            marker = self.item(row)
            marker.rescale(size, width)

    def setStartPoint(self, marker):
        """Designate marker as the start point for this list of markers."""
        
        # get the marker currently designated as the start point (if there is
        # one)
        oldStartPoint = self.getStartPoint()
        # if there currently is a start point, reset its designation and
        # update its colour to the default
        if oldStartPoint:
            oldStartPoint.setDesignation()
            oldStartPoint.recolor()

        # designate marker as the new start point
        marker.setDesignation('start')

    def setEndPoint(self, marker):
        """Designate marker as the end point for this list of markers."""
        
        # get the marker currently designated as the end point (if there is
        # one)
        oldEndPoint = self.getEndPoint()
        # if there currently is an end point, reset its designation and
        # update its colour to the default
        if oldEndPoint:
            oldEndPoint.setDesignation()
            oldEndPoint.recolor()

        # designate marker as the new start point
        marker.setDesignation('end')

    def getStartPoint(self):
        """Return the TrackMarker object designated as the start point for this
        list of markers or None if no marker has been designated as the start
        point.
        """
        
        # loop over all the markers in this list and return the first one found
        # to have the designation 'start' (since there should only be one)
        for row in range(self.count()):
            marker = self.item(row)
            if marker.designation == 'start':
                return marker

        # if no marker in this list was found to have the designation 'start',
        # return None
        return None

    def getEndPoint(self):
        """Return the TrackMarker object designated as the end point for this
        list of markers or None if no marker has been designated as the end
        point.
        """
        
        # loop over all the markers in this list and return the first one found
        # to have the designation 'end' (since there should only be one)
        for row in range(self.count()):
            marker = self.item(row)
            if marker.designation == 'end':
                return marker

        # if no marker in this list was found to have the designation 'end',
        # return None
        return None

    def highlightCurrent(self):
        """Change the colour of the currently selected marker to the
        highlighted colour and change the colour of the rest of the
        markers to their appropriate non-highlighted colours (default colour,
        start colour, or end colour).
        """
        
        # simply loop over all the markers in this list and call their recolor
        # method, which will appropriately recolor the marker based on its
        # designation or whether it is the currently selected marker.
        for row in range(self.count()):
            marker = self.item(row)
            marker.recolor()

    def selectNext(self):
        """Set the currently selected marker to the next marker in the list."""

        # if there are no markers selected (currentRow() == -1) or if the
        # currently selected marker is the last one in the list, return
        if self.currentRow() == -1 or self.currentRow() == self.count() - 1:
            return
        # otherwise set the current selection to the next marker in the list
        else:
            self.setCurrentRow(self.currentRow() + 1)

    def selectPrevious(self):
        """Set the currently selected marker to the previous marker in the
        list.
        """

        # if there are no markers selected (currentRow() == -1) or if the
        # currently selected marker is the first one in the list, return
        if self.currentRow() == -1 or self.currentRow() == 0:
            return
        # otherwise set the current selection to the previous marker in the
        # list
        else:
            self.setCurrentRow(self.currentRow() - 1)

class TrackMarker(QtWidgets.QListWidgetItem):

    """Track marker class. Instantiate by passing a markerId (an int), a unique
    identifier for the marker, x and y (floats), the coordinates of the marker,
    size (float), the size of the marker, width (float), the width of the
    pen used to draw the marker, and optionally parent, a MarkerList object to
    which the marker will be added. This class subclasses QListWidgetItem,
    adding three attributes (id, designation and a QGraphicsEllipseItem) along
    with methods for manipulating these attributes."""

    def __init__(self, markerId, x, y, size, width, parent=None):

        # the id attribute is a unique identifier for the marker. It is up to
        # the code that creates the marker to ensure it is passing a unique id.
        # The main purpose of the id is its use in creating a unique name for
        # for the marker in the point list.
        self.id = markerId

        # the designation attribute indicates whether the marker is a start
        # point, an end point or neither. By default, a newly created marker
        # is neither a start nor end point. Valid values for this attribute are
        # 'start', 'end' or None. This attribute is to be set by calling the
        # setDesignation() method, which takes care of changing the name of
        # a point. It is up to the code that calls setDesignation() to ensure
        # that there is only one start point and only one end point.
        self.designation = None

        # create a unique name for the marker using its id
        markerName = "Point {}".format(self.id)

        # call the __init__ method of the QListWidgetItem superclass, passing
        # the point's name and the marker's parent widget.
        super().__init__(markerName, parent)

        # set a minimum rect size
        if size < 2:
            size = 2

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a rect for the marker's ellipse with the given coordinates
        # and size (set the width and height of the rect to size)
        ellipseRect = QtCore.QRectF(x, y, size, size)
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        ellipseRect.moveCenter(QtCore.QPointF(x, y))
        # create a QGraphicsEllipseItem using the rect created above. Set it
        # as the marker's ellipse attribute.
        self.ellipse = QtWidgets.QGraphicsEllipseItem(ellipseRect)

        # create a pen for the ellipse using the base marker colour
        ellipsePen = QtGui.QPen(constants.DEFAULTMARKERCOLOR)
        # set the width of the pen to width
        ellipsePen.setWidth(width)
        # set the newly created pen as the ellipse's pen
        self.ellipse.setPen(ellipsePen)

    def setDesignation(self, designation=None):
        """Indicate the marker as a Start Point, an End Point or neither, as
        specified by designation (a string).
        """

        # the only valid values for designation are 'start', 'end', or None
        # if some other value was given, don't change the current designation
        if designation not in [None, 'start', 'end']:
            return

        # set the designation
        self.designation = designation

        # if the new designation is 'start', prepend an "s - " to the marker's
        # text/name
        if designation == 'start':
            self.setText("s - Point {}".format(self.id))
        # if the new designation is 'end', prepend an "e - " to the marker's
        # text/name
        elif designation == 'end':
            self.setText("e - Point {}".format(self.id))
        # otherwise remove any extra characters from the marker text
        else:
            self.setText("Point {}".format(self.id))

    def recolor(self):
        """Update the colour of the marker based on its designation or whether
        it is currently selected.
        """

        # create a new pen, starting from the existing pen of the marker's
        # ellipse
        newPen = self.ellipse.pen()

        # if the marker is currently selected, set pen colour to highlighted
        # marker colour
        if self.isSelected():
            newPen.setColor(constants.HIGHLIGHTMARKERCOLOR)
        # if the marker is the start point, set pen colour to start colour
        elif self.designation == 'start':
            newPen.setColor(constants.STARTMARKERCOLOR)
        # if the marker is the end point, set pen colour to end colour
        elif self.designation == 'end':
            newPen.setColor(constants.ENDMARKERCOLOR)
        # otherwise set pen colour to default marker colour
        else:
            newPen.setColor(constants.DEFAULTMARKERCOLOR)

        # set the recoloured pen as the marker's ellipse's pen
        self.ellipse.setPen(newPen)

    def move(self, dx, dy):
        """Move the marker from its current position (x, y) to (x+dx, y+dy).
        dx and dy are floats.
        """

        # create a new rect, starting from the existing rect of the marker's
        # ellipse
        newRect = self.ellipse.rect()
        # translate the rect by (dx, dy)
        newRect.translate(dx, dy)
        # set the translated rect as the marker's ellipse's rect
        self.ellipse.setRect(newRect)

    def getAngle(self, origin, referenceMarker=None):
        """Given an origin - a tuple whose first element is an x-coordinate and
        whose second element is a y-coordinate (both floats)- , return the
        marker's angular coordinate in degrees (a float), where origin is the
        pole in the polar coordinate system. If referenceMarker - a TrackMarker
        object - is given, return the angle between the line joining the origin
        to the marker and the line joining the origin to the referenceMarker.
        """

        # define the marker vector, a QLineF object joining the origin to the
        # center of the marker's ellipse
        markerX = self.ellipse.rect().center().x()
        markerY = self.ellipse.rect().center().y()
        markerVector = QtCore.QLineF(origin[0], origin[1], markerX, markerY)

        # define the reference vector (the vector with respect to which the
        # angle of the marker vector is to be determined)
        # if a referenceMarker was given, the reference vector is the line
        # joining the origin to the center of the reference marker' ellipse
        if referenceMarker:
            referenceX = referenceMarker.ellipse.rect().center().x()
            referenceY = referenceMarker.ellipse.rect().center().y()
        # otherwise the reference vector is the polar axis (a horizontal line
        # terminated at the left by the pole)
        else:
            referenceX = origin[0] + 1
            referenceY = origin[1]
        referenceVector = QtCore.QLineF(origin[0], origin[1], referenceX, referenceY)

        # compute the angular coordinate of the marker
        angle = referenceVector.angleTo(markerVector)

        return angle

    def rescale(self, size, width):
        """Set the width and height of the marker's ellipse's rect to size (a
        float) and set the width of the marker's ellipse's pen to width (a
        float).
        """

        # set a minimum rect size
        if size < 2:
            size = 2

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a new rect, starting from the existing rect of the marker's
        # ellipse
        newRect = self.ellipse.rect()
        # set the width and height of the new rect
        newRect.setWidth(size)
        newRect.setHeight(size)
        # move the rect's center to match that of the original rect's (the
        # center gets shifted when resizing)
        newRect.moveCenter(self.ellipse.rect().center())
        # set the resized rect as the marker's ellipse's rect
        self.ellipse.setRect(newRect)

        # create a new pen, starting from the existing pen of the marker's
        # ellipse
        newPen = self.ellipse.pen()
        # set the width of the new pen
        newPen.setWidth(width)
        # set the resized pen as the marker's ellipse's pen
        self.ellipse.setPen(newPen)
