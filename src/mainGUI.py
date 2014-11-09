# -*- coding: utf-8 -*-
__author__ = "Syed Haider Abidi,  Nooruddin Ahmed and Christopher Dydula"

from PyQt5 import QtWidgets, QtGui, QtCore

# External methods
from skeleton import GuiSkeleton
from optDensity import calcOptDensity
from circleFit import circleFit
from angleCalc import angleCalc
import math


class MainGui(GuiSkeleton):

    """Main GUI class that inherits from base skeleton GUI class and implements
    logic that connects buttons and functions together. Defines internal
    methods to carry out various UI actions (zoom, opening images, etc.)
    and calls external functions that have been imported below.
    """

    def __init__(self, mainWindow):
        """Initialize gui skeleton and connect buttons to internal and
        external methods.
        """

        super().__init__(mainWindow)

        # number of messages printed to the console
        self.num_messages = 0

        # Set up button to load images.
        self.openImageButton.clicked.connect(self.openImage)

        # Set up button to zoom in/out on image.
        self.zoomFactor = 1
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)

        # Set up point drawing at mousepress on image.
        self.sizeOfEllipse = 10
        self.widthOfEllipse = 2.5
        self.widthOfCircle = 2.5
        self.sizeAngleRef = 10
        self.widthAngleRef = 2.5
        self.nEllipseDrawn = 0
        self.mapNametoPoint = {}
        self.hasTrackMomentumCalc = False
        self.hasDrawndLCurves = False
        self.initialAnglePointDrawn = False
        self.finalAnglePointDrawn = False
        self.lineAnglePointDrawn = False
        self.startPointName = ""
        self.endPointName = ""
        self.pixmapItem.mousePressEvent = self.pixelSelect
        self.pixmapItem.mouseReleaseEvent = self.angleSelect
        self.pixmapItem.mouseMoveEvent = self.pixelSelectMouseEvent

        # Set up shortCuts
        self.centralWidget.keyPressEvent = self.keyPressEvent

        # Set up button to reset the tool.
        self.resetButton.clicked.connect(self.resetImage)

        # Set up button to calculate track momentum.
        self.calcMomentumButton.clicked.connect(self.calcTrackMom)

        # Set up button to calculate optical density.
        self.calcDensityButton.clicked.connect(self.calcOptDen)
        
        # Set up button to calculate angle.
        self.calcAngleButton.clicked.connect(self.calcAngle)
        
        # Set up text field that specifies dL (user-specified width).
        self.dlLineEdit.textEdited.connect(self.changedLCircles)

        # Mode bottons
        self.placeMarkerButton.clicked.connect(self.placeMarkerButtonFunc)
        self.drawRefButton.clicked.connect(self.drawRefButtonFunc)

        # Used for debugging purposes.
        self.nUserClickOnPicture = 0

        self.centralWidget.resizeEvent = self.resizeEvent

    ###########################
    # Drawing Functions
    ###########################
    def pixelSelect(self, event):
        """The following function draws a point (ellipse) when called with
        a mousePressEvent at specified event location. Or if the Angle draw
        mode is selected, it will send the drawing to the respective function"""

        if self.drawRefButton.isChecked():
            self.angleSelect(event)
            return
        # Place an event only if 'place marker' button has been pressed.
        if not self.placeMarkerButton.isChecked():
            # Count the number of times user has clicked on the picture.
            # If more than 3 times, display a help message.
            self.nUserClickOnPicture += 1
            if self.nUserClickOnPicture == 3:
                self.nUserClickOnPicture = 0
                self.displayMessage(
                    "HELP - To place track marker, first select 'Place Track Marker' button")
                self.displayMessage(
                    "HELP - To draw angle reference, first select 'Draw Angle Reference' button")
            return

        self.nEllipseDrawn += 1

        pen, size = self.getPointPenSize()
        # Create a drawing rectangle for the ellipse.
        drawRec = QtCore.QRectF(event.pos().x(), event.pos().y(), size, size)
        # Translate top left corner of rectangle to match the clicked position.
        drawRec.moveCenter(QtCore.QPointF(event.pos().x(), event.pos().y()))
        # Draw ellipse with specified colour.
        self.mapNametoPoint[
            'Point ' + str(self.nEllipseDrawn)] = self.scene.addEllipse(drawRec, pen)

        # Update the widget containing the list of points.
        self.pointListWidget.addItem('Point %s' % self.nEllipseDrawn)
        self.pointListWidget.setCurrentRow(
            self.pointListWidget.count() - 1)


    def angleSelect(self, event):
        """The following function draws the intial and final points for the
        angle reference. It is also connected to the mouse release event signal
        as well"""

        # if the draw angle reference buttons is not checked,
        # just simply return. This occurs if mode is unselected or
        # track marker mode is selected
        if not self.drawRefButton.isChecked():
            return

        # if both intial and final point drawn, not need to draw another one
        if self.initialAnglePointDrawn and self.finalAnglePointDrawn:
            return

        pen, size = self.getAnglePenSize()
        # Create a drawing rectangle for the ellipse.
        drawRec = QtCore.QRectF(event.pos().x(), event.pos().y(), size, size)
        # Translate top left corner of rectangle to match the clicked position.
        drawRec.moveCenter(QtCore.QPointF(event.pos().x(), event.pos().y()))
        # Draw ellipse with specified colour.

        if not self.initialAnglePointDrawn:
            self.initialAnglePointDrawn = True
            self.initialAnglePoint = self.scene.addEllipse(drawRec, pen)
        else:
            self.finalAnglePointDrawn = True
            self.finalAnglePoint = self.scene.addEllipse(drawRec, pen)


    def pixelSelectMouseEvent(self, event):
        """The following function draws a line between the intial point and the current
        mouse position. It is connected to mouse drag signal"""

        # if the intial point doesn't existed, return
        if not self.initialAnglePointDrawn:
            return

        # if the final point has been draw, just return
        if self.finalAnglePointDrawn:
            return

        # if a line has been previously draw, just return
        if self.lineAnglePointDrawn:
            self.scene.removeItem(self.lineAnglePoint)

        pen, size = self.getAnglePenSize()
        self.lineAnglePoint = self.scene.addLine(self.initialAnglePoint.rect().center().x(),
                           self.initialAnglePoint.rect().center().y(),
                           event.pos().x(), event.pos().y(),
                           pen)

        # for latter keeping
        self.lineAnglePointDrawn = True

        return

    ###########################
    # Drawing Helper Functions
    ###########################
    def getPointPenSize(self, pointName = ""):
        """The following function moves gets the size and pen for the track markers"""
        # Set colour of ellipse to be drawn.
        pen = QtGui.QPen(self.getPointColor(pointName))
        pen.setWidth(self.widthOfEllipse)
        # set a mimimum width
        if(self.widthOfEllipse < 1):
            pen.setWidth(1)

        # Set size of ellipse to be drawn.
        size = self.sizeOfEllipse
        # set a mimimum size
        if(size < 2):
            size = 2

        return pen, size

    def getPointColor(self, pointName = ""):
        """The following function moves gets the colour for the track markers
        based on the designation of the point"""
        if 's - ' in pointName:
            return QtGui.QColor(0, 186, 186)
        elif 'e - ' in pointName:
            return QtGui.QColor(34, 197, 25)
        else:
            return QtGui.QColor(176, 30, 125)

    def getCirclePen(self, colour):
        """The following function moves gets the size and pen for the fitted circle"""
        # Set colour of ellipse to be drawn.
        if colour is 'red':
            pen = QtGui.QPen(QtCore.Qt.red)
        elif colour is 'blue':
            pen = QtGui.QPen()
        elif colour is 'yellow':
            pen = QtGui.QPen(QtCore.Qt.yellow)
        else:
            pen = QtGui.QPen(QtGui.QColor(33, 95, 147))
        pen.setWidth(self.widthOfCircle)
        # set a mimimum width
        if(self.widthOfCircle < 1):
            pen.setWidth(1)

        return pen

    def getAnglePenSize(self):
        """The following function moves gets the size and pen for the angle markers"""
        # Set colour of ellipse to be drawn.
        pen = QtGui.QPen(QtGui.QColor(243, 42, 31))
        pen.setWidth(self.widthAngleRef)
        # set a mimimum width
        if(self.widthAngleRef < 1):
            pen.setWidth(1)

        # Set size of ellipse to be drawn.
        size = self.sizeAngleRef
        # set a mimimum size
        if(size < 1):
            size = 1

        return pen, size

    ##############################
    # Point Manipulation Methods
    ##############################
    def keyPressEvent(self, event):
        """The following function handles keypressEvents used to select and
        manipulate points in the QListWidget."""

        # WASD to move individual points around.
        dx = 0
        dy = 0
        if event.key() == QtCore.Qt.Key_W:
            dy = -1
        elif event.key() == QtCore.Qt.Key_S:
            dy = 1
        elif event.key() == QtCore.Qt.Key_D:
            dx = 1
        elif event.key() == QtCore.Qt.Key_A:
            dx = -1

        # F/V to select points in list.
        elif event.key() == QtCore.Qt.Key_V:
            current_row = self.pointListWidget.currentRow()
            num_rows = self.pointListWidget.count()
            if current_row == -1 or current_row == num_rows - 1:
                return
            else:
                self.pointListWidget.setCurrentRow(current_row + 1)
        elif event.key() == QtCore.Qt.Key_F:
            current_row = self.pointListWidget.currentRow()
            if current_row == -1 or current_row == 0:
                return
            else:
                self.pointListWidget.setCurrentRow(current_row - 1)

        # G/H key for setting start and end point
        elif event.key() == QtCore.Qt.Key_G:
            listPoint = self.pointListWidget.findItems(
                    's - '+self.startPointName, QtCore.Qt.MatchExactly)
            for p in listPoint:
                p.setText(p.text().replace('s - ', ''))
                # just to redraw the point in the different colour
                self.movePoint(p.text(), 0, 0)

            if(self.pointListWidget.currentItem()):
                p = self.pointListWidget.currentItem()
                if('e - ' in p.text()):
                    p.setText(p.text().replace('e - ', ''))
                self.startPointName = p.text()
                p.setText('s - '+p.text())
                self.movePoint(p.text(), 0, 0)
                
        elif event.key() == QtCore.Qt.Key_H:
            listPoint = self.pointListWidget.findItems(
                    'e - '+self.endPointName, QtCore.Qt.MatchExactly)

            for p in listPoint:
                p.setText(p.text().replace('e - ', ''))
                self.movePoint(p.text(), 0, 0)

            if(self.pointListWidget.currentItem()):
                p = self.pointListWidget.currentItem()
                if('s - ' in p.text()):
                    p.setText(p.text().replace('s - ', ''))
                self.endPointName = p.text()
                p.setText('e - '+p.text())
                self.movePoint(p.text(), 0, 0)

        # Z/X for zoom in/zoom out.
        elif event.key() == QtCore.Qt.Key_Z:
            self.zoomIn()
        elif event.key() == QtCore.Qt.Key_X:
            self.zoomOut()

        # R for reset
        elif event.key() == QtCore.Qt.Key_R:
            self.resetImage()

        # M, N, B for calculate functions
        elif event.key() == QtCore.Qt.Key_M:
            self.calcTrackMom()
        elif event.key() == QtCore.Qt.Key_N:
            self.calcOptDen()
        elif event.key() == QtCore.Qt.Key_B:  # calculate angle
            pass

        # O for open image
        elif event.key() == QtCore.Qt.Key_O:
            self.openImage()

        # P and L for mode switching
        elif event.key() == QtCore.Qt.Key_P:
            if self.placeMarkerButton.isChecked():
                self.placeMarkerButton.setChecked(False)
            else:
                self.placeMarkerButton.setChecked(True)
            self.placeMarkerButtonFunc()
        elif event.key() == QtCore.Qt.Key_L:
            if self.drawRefButton.isChecked():
                self.drawRefButton.setChecked(False)
            else:
                self.drawRefButton.setChecked(True)
            self.drawRefButtonFunc()

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            self.deletePoint(self.pointListWidget.currentItem().text())
            self.pointListWidget.takeItem(
                self.pointListWidget.currentRow())
            return

        # Update point location
        if(self.pointListWidget.currentItem()):
            self.movePoint(
                self.pointListWidget.currentItem().text(), dx, dy)

    def movePoint(self, pointName, dx, dy):
        """The following function moves given point by [dx,dy]"""
        pen, size = self.getPointPenSize(pointName)
        pointName = pointName.replace('s - ', '')
        pointName = pointName.replace('e - ', '')
        value = self.mapNametoPoint[pointName]
        drawRec = QtCore.QRectF(
            value.rect().x(), value.rect().y(), size, size)
        drawRec.moveCenter(
            QtCore.QPointF(value.rect().center().x() + dx, value.rect().center().y() + dy))
        self.mapNametoPoint[pointName].setRect(drawRec)
        self.mapNametoPoint[pointName].setPen(pen)

        self.scene.update()

    def deletePoint(self, pointName):
        """The following function deletes given point"""
        itemList = self.scene.items()
        pointName = pointName.replace('s - ', '')
        pointName = pointName.replace('e - ', '')
        for i in itemList:
            if(i == self.mapNametoPoint[pointName]):
                self.scene.removeItem(i)
        del self.mapNametoPoint[pointName]

    ##############################
    # Open Image Method
    ##############################
    def openImage(self):
        """The following function opens a file dialog and then loads
        user-specified image."""

        # Load image through FileDialog
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            self.centralWidget, "Open File", QtCore.QDir.currentPath())
        if fileName:
            self.qimage = QtGui.QImage()
            image = self.qimage.load(fileName[0])
        if not image:
            self.displayMessage("Cannot load {}.".format(fileName))
            return

        # resize the graphics scene to the loaded image
        self.scene.setSceneRect(0, 0, self.qimage.width(), self.qimage.height())

        # Create a pixmap from the loaded image.
        self.pixmapItem.setPixmap(QtGui.QPixmap.fromImage(self.qimage))

        # set keyboard focus to the graphics view
        self.view.setFocus()

        # Reset any image transformations.
        self.resetImage()


    ##############################
    # Zoom and Helper Functions
    ##############################
    def zoomIn(self):
        """The following function zooms image by 125% when called."""
        self.scaleImage(1.25)

    def zoomOut(self):
        """The following function zooms image by 80% when called."""
        self.scaleImage(0.8)

    def scaleImage(self, factor):
        """The following helper function scales images and points."""
        self.zoomFactor = self.zoomFactor * factor
        self.view.scale(factor, factor)
        self.adjustScrollBar(
            self.sceneScrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.sceneScrollArea.verticalScrollBar(), factor)

        # Scale the drawn points when zooming.
        self.sizeOfEllipse /= factor
        self.widthOfEllipse /= factor
        self.widthOfCircle /= factor
        self.sizeAngleRef /= factor
        self.widthAngleRef /= factor
        pen, size = self.getPointPenSize()

        # Recale the points.
        for key, value in self.mapNametoPoint.items():
            self.updateDrawCircleZoom(value, size, pen)

        # rescale the end and start point
        if len(self.startPointName) > 0:
            pen, size = self.getPointPenSize('s - '+self.startPointName)
            self.updateDrawCircleZoom(self.mapNametoPoint[self.startPointName], size, pen)
        if len(self.endPointName) > 0:
            pen, size = self.getPointPenSize('e - '+self.endPointName)
            self.updateDrawCircleZoom(self.mapNametoPoint[self.endPointName], size, pen)
      
        pen = self.getCirclePen('green')
        if self.hasTrackMomentumCalc:
            self.updateDrawCircleZoom(
                self.nominalFittedCenter, self.nominalFittedCenter.rect().width(), pen)

        pen.setStyle(QtCore.Qt.DashDotLine)
        if self.hasDrawndLCurves:
            self.updateDrawCircleZoom(
                self.innerFittedCenter, self.innerFittedCenter.rect().width(), pen)
            self.updateDrawCircleZoom(
                self.outerFittedCenter, self.outerFittedCenter.rect().width(), pen)

        pen, size = self.getAnglePenSize()
        if self.initialAnglePointDrawn:
            self.updateDrawCircleZoom(self.initialAnglePoint, size, pen)
        if self.finalAnglePointDrawn:
            self.updateDrawCircleZoom(self.finalAnglePoint, size, pen)
        if self.lineAnglePointDrawn:
            self.lineAnglePoint.setPen(pen)

        self.scene.update()

    def updateDrawCircleZoom(self, circle, size, pen):
        """The following helper function scales circles."""
        drawRec = QtCore.QRectF(
            circle.rect().x(), circle.rect().y(), size, size)
        drawRec.moveCenter(
            QtCore.QPointF(circle.rect().center().x(), circle.rect().center().y()))
        circle.setRect(drawRec)
        circle.setPen(pen)

    def adjustScrollBar(self, scrollBar, factor):
        """The following helper function adjusts size of scrollbar."""
        scrollBar.setValue(
            int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2)))

    ##############################
    # Console Methods
    ##############################
    def displayMessage(self, msg):
        """The following function is used to write messages to console."""

        self.num_messages += 1
        msg = "[{}]  {}".format(self.num_messages, msg)
        self.consoleTextBrowser.append(msg)

    ##############################
    # Main Calculation Methods
    ##############################
    def calcTrackMom(self):
        """The following function is used to calculate track momentum of
        drawn points on image and then draw a fitted circle to them."""

        # Need a minimum of 3 points to fit a circle.
        if len(self.mapNametoPoint) < 3:
            self.displayMessage("ERROR: Less than 3 points to fit.")
            return

        # Return if track momentum has already been calculated.
        if self.hasTrackMomentumCalc:
            self.scene.removeItem(self.nominalFittedCenter)

        if self.hasDrawndLCurves:
            self.scene.removeItem(self.innerFittedCenter)
            self.scene.removeItem(self.outerFittedCenter)

        if self.placeMarkerButton.isChecked():
            self.placeMarkerButton.setChecked(False)

        pointList = []
        for key, value in self.mapNametoPoint.items():
            pointList.append(value)
            # print('x: ', value.rect().center().x(),
            #      ' y: ', value.rect().center().y())

        # Fit a circle to selected points.
        fitted_circle = circleFit(pointList)
        self.fittedX0 = fitted_circle[0][0]
        self.fittedY0 = fitted_circle[1][0]
        self.fittedR0 = fitted_circle[2][0]

        self.circleInfo = fitted_circle

        self.displayMessage(
            str("Fitted x_o:\t %f +/- %f" % (fitted_circle[0][0], fitted_circle[0][1])))
        self.displayMessage(
            str("Fitted y_o:\t %f +/- %f" % (fitted_circle[1][0], fitted_circle[1][1])))
        self.displayMessage(
            str("Fitted R_o:\t %f +/- %f" % (fitted_circle[2][0], fitted_circle[2][1])))
        # Set colour of circle to be drawn.
        pen = self.getCirclePen('green')
        # Create a drawing rectangle for the circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * self.fittedR0, 2 * self.fittedR0)
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        # Draw circle with specified colour.
        self.nominalFittedCenter = self.scene.addEllipse(drawRec, pen)

        self.drawdlCurves()
        self.hasTrackMomentumCalc = True

    def drawdlCurves(self):
        """The following helper function draws the dL curves."""
        # Draw dL curves if dL is specified.
        try:
            self.dL = float(self.dlLineEdit.text())
        except ValueError:
            self.displayMessage("ERROR: dL is not a float")
            return

        pen = self.getCirclePen('green')
        pen.setStyle(QtCore.Qt.DashDotLine)
        # Define outer circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * (self.fittedR0 + self.dL), 2 * (self.fittedR0 + self.dL))
        # Draw a dotted line.
        pen.setStyle(QtCore.Qt.DashDotLine)
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.outerFittedCenter = self.scene.addEllipse(drawRec, pen)

        # Deine inner circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0,  2 * (self.fittedR0 - self.dL), 2 * (self.fittedR0 - self.dL))
        # Draw a dotted line.
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.innerFittedCenter = self.scene.addEllipse(drawRec, pen)

        # Used for debugging purposes.
        self.hasDrawndLCurves = True

    def calcOptDen(self):
        """The following function is used to calculate optical density of
        drawn points on image with a specified dL."""

        # Need a minimum of 3 points to fit a circle.
        if len(self.mapNametoPoint) < 3:
            self.displayMessage("ERROR: Less than 3 points to fit.")
            return

        # Return if track momentum has NOT been calculated.
        if self.hasTrackMomentumCalc is False:
            self.displayMessage(
                "ERROR: Track momentum has not been calculated yet.")
            return

        # Return if track momentum has NOT been calculated.
        if self.dL <= 0:
            self.displayMessage(
                "ERROR: Positive non-zero value for dL was not specified.")
            return

        pointList = []
        for key, value in self.mapNametoPoint.items():
            pointList.append(value)

        # Create a circle to pass to optical density function.
        self.tmp_circle = [self.fittedX0, self.fittedY0, self.fittedR0]

        # Draw dL curves if dL is specified.
        try:
            self.dL = float(self.dlLineEdit.text())
        except ValueError:
            self.displayMessage("ERROR: dL is not a float")
            return

        # Call function to compute optical density.
        self.optDens, self.errOptDens = calcOptDensity(
            self, self.pixmapItem, pointList, self.tmp_circle, self.dL)
        # Used for debugging.
        self.displayMessage(str("%f %f" % (self.optDens, self.errOptDens)))

    def calcAngle(self):
        """The following function is used to calculate the angle between
        intial tangent and specified references"""

        if self.hasTrackMomentumCalc is False:
            self.displayMessage(
                "ERROR: Track momentum has not been calculated yet.")
            return
        
        if len(self.startPointName) == 0:
            self.displayMessage(
                "ERROR: Intial Point has not been defined yet.")
            return

        if self.lineAnglePointDrawn is False:
            self.displayMessage(
                "ERROR: Angle Line reference not drawn.")
            return


        angleInfo = angleCalc(self, self.circleInfo, 
                self.mapNametoPoint[self.startPointName],
                self.lineAnglePoint )
        
        self.displayMessage(str("opening Angle %f +/- %f" % (angleInfo[0], angleInfo[1])))


    ##############################
    # Connection to Other Buttons
    ##############################
    def changedLCircles(self, value):
        """The following helper function changes the diameter of dL curves.
        Connected to changing values on the dL field"""

        if len(value) is 0:
            return

        try:
            self.dL = float(value)
        except ValueError:
            self.displayMessage("ERROR: dL is not a float")
            return

        # Return if track momentum has already been calculated.
        if not self.hasTrackMomentumCalc:
            return

        # If original dL curves have not been drawn, create them.
        if not self.hasDrawndLCurves:
            self.drawdlCurves()

        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0,  2 * (self.fittedR0 + self.dL), 2 * (self.fittedR0 + self.dL))
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.outerFittedCenter.setRect(drawRec)

        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * (self.fittedR0 - self.dL), 2 * (self.fittedR0 - self.dL))
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))

        self.innerFittedCenter.setRect(drawRec)

        self.scene.update()

    def placeMarkerButtonFunc(self):
        """The following helper function creates the changes when the
        place track marker mode button is toggled"""
        self.drawRefButton.setChecked(False)

    def drawRefButtonFunc(self):
        """The following helper function creates the changes when the
        draw angle reference mode button is toggled. Resets the drawn
        angle reference as well"""

        self.placeMarkerButton.setChecked(False)
        if self.drawRefButton.isChecked():
            # reset if check in
            if self.lineAnglePointDrawn:
                self.scene.removeItem(self.lineAnglePoint)
            if self.finalAnglePointDrawn:
                self.scene.removeItem(self.finalAnglePoint)
            if self.initialAnglePointDrawn:
                self.scene.removeItem(self.initialAnglePoint)

            self.initialAnglePointDrawn = False
            self.finalAnglePointDrawn = False
            self.lineAnglePointDrawn = False

            pass

    ##############################
    # Resize Function
    ##############################
    def resizeEvent(self, event):
        self.sceneScrollArea.setMinimumSize(
            QtCore.QSize(0, self.centralWidget.size().height() / 1.6))

    ##############################
    # Reset
    ##############################
    def resetImage(self):
        """The following function resets image transformations,
        and clears point list and console output."""

        # Clear drawn points.
        itemList = self.scene.items()
        for i in itemList:
            if(i.__class__.__name__ == 'QGraphicsPixmapItem'):
                continue
            self.scene.removeItem(i)

        # Clear console output.
        self.consoleTextBrowser.clear()

        # Reset the number of points.
        self.nEllipseDrawn = 0
        self.mapNametoPoint = {}
        self.hasTrackMomentumCalc = False
        self.hasDrawndLCurves = False
        self.initialAnglePointDrawn = False
        self.finalAnglePointDrawn = False
        self.lineAnglePointDrawn = False
        self.startPointName = ""
        self.endPointName = ""

        # reset view scale and fit image in view
        self.scaleImage(1/self.zoomFactor)


        self.sizeOfEllipse *= self.zoomFactor
        self.widthOfEllipse *= self.zoomFactor
        self.widthOfCircle *= self.zoomFactor
        self.sizeAngleRef *= self.zoomFactor
        self.widthAngleRef *= self.zoomFactor

        scaleFactor = 1

        height_ratio = self.view.height() / self.qimage.height()
        width_ratio = self.view.width() / self.qimage.width()

        if height_ratio < width_ratio:
            if height_ratio < 1:
                scaleFactor = 0.8**math.ceil(math.log(height_ratio, 0.8))
        else:
            if width_ratio < 1:
                scaleFactor = 0.8**math.ceil(math.log(width_ratio, 0.8))

        self.scaleImage(scaleFactor)

        # Clear the list of points.
        self.pointListWidget.clear()

        self.nUserClickOnPicture = 0

        self.mapNametoPoint = {}
        # reset count of messages printed to console
        self.num_messages = 0
