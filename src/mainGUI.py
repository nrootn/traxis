# -*- coding: utf-8 -*-
__author__ = "Syed Haider Abidi,  Nooruddin Ahmed and Christopher Dydula"

from PyQt5 import QtWidgets, QtGui, QtCore

# External methods
from skeleton import GuiSkeleton
from optDensity import calcOptDensity
from circleFit import circleFit
from angleCalc import angleCalc
import math
import json


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

        # Calibration
        self.nomCalcmPerPix = 0.01188
        self.errCalcmPerPix = 0.00090

        # number of messages printed to the console
        self.num_messages = 0

        # Set up button to open images.
        self.openImageButton.clicked.connect(self.openImage)

        # Set up buttons to save and load analysis sessions
        self.saveSessionButton.clicked.connect(self.saveSession)
        self.loadSessionButton.clicked.connect(self.loadSession)

        # Set up button for taking a screenshot of the scroll area
        self.screenshotButton.clicked.connect(self.saveScreenshot)

        # Set up buttons to zoom in/out on image.
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
        self.imageFileName = None
        self.scenePixmap.mousePressEvent = self.pixelSelect
        self.scenePixmap.mouseReleaseEvent = self.angleSelect
        self.scenePixmap.mouseMoveEvent = self.pixelSelectMouseEvent

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

        self.pointListWidget.itemSelectionChanged.connect(self.recolourPoint)

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
        self.lineAnglePoint = self.scene.addLine(
            self.initialAnglePoint.rect().center().x(),
            self.initialAnglePoint.rect().center().y(),
            event.pos().x(), event.pos().y(), pen)

        # for latter keeping
        self.lineAnglePointDrawn = True

        return

    ###########################
    # Drawing Helper Functions
    ###########################
    def getPointPenSize(self, pointName="", color=None):
        """The following function moves gets the size and pen for the track markers"""
        # Set colour of ellipse to be drawn.
        if not color:
            pen = QtGui.QPen(self.getPointColor(pointName))
        else:
            pen = QtGui.QPen(color)
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

    def getPointColor(self, pointName=""):
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

        # if shift was pressed 10x the movement
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            # multiple the movement by the circle radius
            pen, size = self.getPointPenSize()
            dx *= size/2
            dy *= size/2
        
        # F/V to select points in list.
        if event.key() == QtCore.Qt.Key_V:
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
                's - ' + self.startPointName, QtCore.Qt.MatchExactly)
            for p in listPoint:
                p.setText(p.text().replace('s - ', ''))

            if(self.pointListWidget.currentItem()):
                p = self.pointListWidget.currentItem()
                if('e - ' in p.text()):
                    p.setText(p.text().replace('e - ', ''))
                self.startPointName = p.text()
                p.setText('s - ' + p.text())
            self.recolourPoint()

        elif event.key() == QtCore.Qt.Key_H:
            listPoint = self.pointListWidget.findItems(
                'e - ' + self.endPointName, QtCore.Qt.MatchExactly)

            for p in listPoint:
                p.setText(p.text().replace('e - ', ''))

            if(self.pointListWidget.currentItem()):
                p = self.pointListWidget.currentItem()
                if('s - ' in p.text()):
                    p.setText(p.text().replace('s - ', ''))
                self.endPointName = p.text()
                p.setText('e - ' + p.text())
            self.recolourPoint()

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
            self.calcAngle()

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
            #print(vars(self))
        elif event.key() == QtCore.Qt.Key_L:
            if self.drawRefButton.isChecked():
                self.drawRefButton.setChecked(False)
            else:
                self.drawRefButton.setChecked(True)
            self.drawRefButtonFunc()

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            if self.pointListWidget.count() > 0:
                deletedItem = self.pointListWidget.takeItem(
                    self.pointListWidget.currentRow())
                self.deletePoint(deletedItem.text())
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
        #pen.setColor(self.mapNametoPoint[pointName].pen().color())
        #self.mapNametoPoint[pointName].setPen(pen)

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

        print(pointName, self.startPointName, self.endPointName)

        if pointName in self.startPointName:
            self.startPointName = ''
        if pointName in self.endPointName:
            self.endPointName = ''

        print(pointName, self.startPointName, self.endPointName)

    def recolourPoint(self):
        for row in range(self.pointListWidget.count()):
            point = self.pointListWidget.item(row)
            strippedPointName = point.text().replace('s - ', '')
            strippedPointName = strippedPointName.replace('e - ', '')
            self.mapNametoPoint[strippedPointName].setPen(self.getPointPenSize(point.text())[0])
        if self.pointListWidget.currentItem():
            currentPoint = self.pointListWidget.currentItem().text()
            if currentPoint.startswith('s - ') or currentPoint.startswith('e - '):
                currentPoint = currentPoint[4:]
            self.mapNametoPoint[currentPoint].setPen(self.getPointPenSize(currentPoint, QtGui.QColor(235, 233, 0))[0])
        self.scene.update()

    ##############################
    # Open Image Method
    ##############################
    def openImage(self, fileName=None):
        """The following function opens a file dialog and then loads
        user-specified image."""

        if not fileName:
            # open file dialog to obtain image file name
            self.imageFileName = QtWidgets.QFileDialog.getOpenFileName(
                self.centralWidget, "Open File", QtCore.QDir.currentPath(),
                "Images (*.png *.jpg);;All Files (*)")[0]
        else:
            self.imageFileName = fileName

        # load the image into sceneImage
        if not self.imageFileName:
            return False # image not loaded successfully
        else:
            image = self.sceneImage.load(self.imageFileName)
        if not image:
            self.displayMessage(
                "Cannot load {}.".format(self.imageFileName))
            return False # image not loaded successfully

        # resize the graphics scene to the loaded image
        self.scene.setSceneRect(
            0, 0, self.sceneImage.width(), self.sceneImage.height())

        # Create a pixmap from the loaded image.
        self.scenePixmap.setPixmap(QtGui.QPixmap.fromImage(self.sceneImage))

        # set keyboard focus to the graphics view
        self.sceneView.setFocus()

        # Reset any image transformations.
        self.resetImage()

        # an image was successfully opened
        return True

    def saveSession(self):
        """Save analysis session to a .json file."""

        if not self.imageFileName:
            self.displayMessage("Nothing to save.")
            return

        # open file dialog for selecting a file to save to
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            self.centralWidget, "Save Session", "./untitled.json",
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        if not fileName:
            return
        else:
            # create a dictionary with the data we want to save
            saveData = {}
            saveData['imageFileName'] = self.imageFileName

            if self.pointListWidget.count() > 0:
                points = []
                for row in range(self.pointListWidget.count()):
                    point = self.pointListWidget.item(row)
                    pointDict = {}
                    pointDict['name'] = point.text()
                    strippedName = point.text().replace('s - ', '')
                    strippedName = strippedName.replace('e - ', '')
                    pointEllipse = self.mapNametoPoint[strippedName]
                    pointDict['x'] = pointEllipse.rect().center().x()
                    pointDict['y'] = pointEllipse.rect().center().y()
                    points.append(pointDict)
                saveData["points"] = points

            if self.dlLineEdit.text() != "0":
                saveData['dl'] = self.dlLineEdit.text()

            if self.finalAnglePointDrawn:
                initialPointDict = {}
                initialPointDict[
                    'x'] = self.initialAnglePoint.rect().center().x()
                initialPointDict[
                    'y'] = self.initialAnglePoint.rect().center().y()
                saveData['initialAnglePoint'] = initialPointDict
                finalPointDict = {}
                finalPointDict[
                    'x'] = self.finalAnglePoint.rect().center().x()
                finalPointDict[
                    'y'] = self.finalAnglePoint.rect().center().y()
                saveData['finalAnglePoint'] = finalPointDict

            # serialize the save data dictionary and save to file
            with open(fileName, 'w') as saveFile:
                json.dump(saveData, saveFile, indent=4)

    def loadSession(self):
        """Load analysis session from a .json file."""

        # open file dialog for selecting a file to load from
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            self.centralWidget, "Load Session", QtCore.QDir.currentPath(),
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        if not fileName:
            return
        else:
            with open(fileName, 'r') as loadFile:
                loadData = json.load(loadFile)

                imageFileName = loadData.get('imageFileName')

                self.resetImage()

                if not imageFileName:
                    return

                opened = self.openImage(imageFileName)
                if not opened:
                    return

                points = loadData.get('points')
                if points:
                    for point in points:
                        pointName = point["name"]
                        x = point['x']
                        y = point['y']
                        self.nEllipseDrawn += 1
                        self.pointListWidget.addItem(pointName)
                        pen, size = self.getPointPenSize(pointName)
                        drawRec = QtCore.QRectF(x, y, size, size)
                        drawRec.moveCenter(QtCore.QPointF(x, y))
                        pointEllipse = self.scene.addEllipse(drawRec, pen)
                        if pointName.startswith('s - '):
                            self.startPointName = pointName.replace('s - ', '')
                            self.mapNametoPoint[
                                pointName.replace('s - ', '')] = pointEllipse
                        elif pointName.startswith('e - '):
                            self.endPointName = pointName.replace('e - ', '')
                            self.mapNametoPoint[
                                pointName.replace('e - ', '')] = pointEllipse
                        else:
                            self.mapNametoPoint[pointName] = pointEllipse
                        self.pointListWidget.setCurrentRow(
                            self.pointListWidget.count() - 1)

                dl = loadData.get('dl')
                if dl:
                    self.dlLineEdit.setText(dl)
                    self.dL = float(dl)

                initialAnglePoint = loadData.get('initialAnglePoint')
                finalAnglePoint = loadData.get('finalAnglePoint')
                if initialAnglePoint and finalAnglePoint:
                    self.initialAnglePointDrawn = True
                    self.finalAnglePointDrawn = True
                    self.lineAnglePointDrawn = True
                    pen, size = self.getAnglePenSize()
                    drawRecInitial = QtCore.QRectF(initialAnglePoint['x'],
                                              initialAnglePoint['y'], size,
                                              size)
                    drawRecInitial.moveCenter(QtCore.QPointF(initialAnglePoint['x'],
                                              initialAnglePoint['y']))
                    drawRecFinal = QtCore.QRectF(finalAnglePoint['x'],
                                              finalAnglePoint['y'], size,
                                              size)
                    drawRecFinal.moveCenter(QtCore.QPointF(finalAnglePoint['x'],
                                              finalAnglePoint['y']))
                    self.initialAnglePoint = self.scene.addEllipse(
                        drawRecInitial, pen)
                    self.finalAnglePoint = self.scene.addEllipse(
                        drawRecFinal, pen)
                    self.lineAnglePoint = self.scene.addLine(
                        initialAnglePoint['x'], initialAnglePoint['y'],
                        finalAnglePoint['x'], finalAnglePoint['y'], pen)

    def saveScreenshot(self):
        """Save the currently visible part of the scene scroll area to an
        image.
        """
        screenshot = QtGui.QPixmap(self.sceneScrollArea.rect().size())
        self.sceneScrollArea.render(
            screenshot, QtCore.QPoint(),
            QtGui.QRegion(self.sceneScrollArea.rect()))
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            self.centralWidget, "Save Screenshot", "./untitled.png",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff *.tif)")[0]
        if not screenshot.save(fileName):
            self.displayMessage("Unable to save screenshot")

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
        self.sceneView.scale(factor, factor)
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
            pen, size = self.getPointPenSize('s - ' + self.startPointName)
            self.updateDrawCircleZoom(
                self.mapNametoPoint[self.startPointName], size, pen)
        if len(self.endPointName) > 0:
            pen, size = self.getPointPenSize('e - ' + self.endPointName)
            self.updateDrawCircleZoom(
                self.mapNametoPoint[self.endPointName], size, pen)

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
        pen.setColor(circle.pen().color())
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

        # if self.placeMarkerButton.isChecked():
        #    self.placeMarkerButton.setChecked(False)

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
            str("Fitted x_o:\t %f +/- %f [pixel]" % (fitted_circle[0][0], fitted_circle[0][1])))
        self.displayMessage(
            str("Fitted y_o:\t %f +/- %f [pixel]" % (fitted_circle[1][0], fitted_circle[1][1])))
        self.displayMessage(
            str("Fitted R_o:\t %f +/- %f [pixel]" % (fitted_circle[2][0], fitted_circle[2][1])))
        self.displayMessage(
            str("Fitted R_o:\t %f +/- %f (Stat) +/- %f (Cal) [cm]" % (fitted_circle[2][0]*self.nomCalcmPerPix, 
                fitted_circle[2][1]*self.nomCalcmPerPix, fitted_circle[2][0]*self.errCalcmPerPix)))

        # TODO: Remove this
        r_temp = fitted_circle[2][0]*self.nomCalcmPerPix
        r_err = r_temp*math.sqrt(math.pow(fitted_circle[2][1]/fitted_circle[2][0],2)+math.pow(self.errCalcmPerPix/self.nomCalcmPerPix,2))  
        self.displayMessage("Remove this from the final product")
        self.displayMessage(
                str("Fitted P_o:\t %f +/- %f (Stat) +/- %f (Cal) [MeV]" % (0.3*15.5*fitted_circle[2][0]*self.nomCalcmPerPix, 
                    0.3*15.5*fitted_circle[2][1]*self.nomCalcmPerPix, 0.3*15.5*fitted_circle[2][0]*self.errCalcmPerPix)))
        self.displayMessage(
            str("Fitted R_o:\t %f +/- %f [MeV]" % (0.3*15.5*r_temp, 0.3*15.5*r_err)))
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

        # Return if value of dL was not specified.
        if self.dL <= 0:
            self.displayMessage(
                "ERROR: Positive non-zero value for dL was not specified.")
            return

        # Check if start point was defined.
        if len(self.startPointName) == 0:
            self.displayMessage(
                "ERROR: Initial point has not been defined yet.")
            return

        # Check if end point was defined
        if len(self.endPointName) == 0:
            self.displayMessage(
                "ERROR: End point has not been defined yet.")
            return

        pointList = []
        for key, value in self.mapNametoPoint.items():
            pointList.append(value)

        # Assigned fitted circle to pass to optical density function.
        self.tmp_circle = self.circleInfo

        # Draw dL curves if dL is specified.
        try:
            self.dL = float(self.dlLineEdit.text())
        except ValueError:
            self.displayMessage("ERROR: dL is not a float")
            return

        # Call function to compute optical density.
        self.displayMessage("Computing optical density...")

        self.optDens, self.errOptDens, self.trackLengthPix  = calcOptDensity(
            self, self.sceneImage, pointList, self.tmp_circle, self.dL,
            self.mapNametoPoint[self.startPointName],
            self.mapNametoPoint[self.endPointName])
        self.displayMessage(str("Total optical density: %f +/- %f" % (self.optDens, self.errOptDens)))
        self.displayMessage(str("Track Length: %f [Pixel]" % (self.trackLengthPix)))

        # Calculation of Variables
        self.trackLengthcm = self.trackLengthPix * self.nomCalcmPerPix;
        self.trackLengtherr = self.trackLengthPix * self.errCalcmPerPix;
        self.optDenspercm = self.optDens/self.trackLengthcm;
        self.optDenspercmErr = self.optDenspercm * math.sqrt(
                math.pow(self.trackLengtherr/self.trackLengthcm,2)+math.pow(self.errOptDens/self.optDens,2));

        self.displayMessage(str("Optical density/cm: %f +/- %f [1/cm]" % (self.optDenspercm, self.optDenspercmErr)))
        self.displayMessage(str("Track Length: %f +/- %f [cm]" % (self.trackLengthcm, self.trackLengtherr)))

    def calcAngle(self):
        """The following function is used to calculate the angle between
        intial tangent and specified references"""

        if self.hasTrackMomentumCalc is False:
            self.displayMessage(
                "ERROR: Track momentum has not been calculated yet.")
            return

        if len(self.startPointName) == 0:
            self.displayMessage(
                "ERROR: Initial point has not been defined yet.")
            return

        if self.lineAnglePointDrawn is False:
            self.displayMessage(
                "ERROR: Angle Line reference not drawn.")
            return

        angleInfo = angleCalc(self, self.circleInfo,
                              self.mapNametoPoint[self.startPointName],
                              self.lineAnglePoint)

        self.displayMessage(
            str("opening Angle %f +/- %f" % (angleInfo[0], angleInfo[1])))

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

        # Clear the list of points.
        self.pointListWidget.clear()

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
        self.scaleImage(1 / self.zoomFactor)

        self.sizeOfEllipse *= self.zoomFactor
        self.widthOfEllipse *= self.zoomFactor
        self.widthOfCircle *= self.zoomFactor
        self.sizeAngleRef *= self.zoomFactor
        self.widthAngleRef *= self.zoomFactor

        if not self.sceneImage.isNull():
            scaleFactor = 1

            height_ratio = self.sceneView.height() / self.sceneImage.height()
            width_ratio = self.sceneView.width() / self.sceneImage.width()

            if height_ratio < width_ratio:
                if height_ratio < 1:
                    scaleFactor = 0.8 ** math.ceil(math.log(height_ratio, 0.8))
            else:
                if width_ratio < 1:
                    scaleFactor = 0.8 ** math.ceil(math.log(width_ratio, 0.8))

            self.scaleImage(scaleFactor)


        self.nUserClickOnPicture = 0

        self.dlLineEdit.setText("0")
        self.dL = 0

        self.mapNametoPoint = {}
        # reset count of messages printed to console
        self.num_messages = 0
