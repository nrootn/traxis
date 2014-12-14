import json
import math
from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants
from traxis.gui import skeleton
from traxis.calc import anglecalc, circlefit, optdensity
from traxis.graphics import tangent


class MainGui(skeleton.GuiSkeleton):

    """Main GUI class that inherits from base skeleton GUI class and implements
    logic that connects buttons and functions together. Defines internal
    methods to carry out various UI actions (zoom, opening images, etc.)
    and calls external functions that have been imported above.
    """

    def __init__(self):
        """Initialize gui skeleton and connect buttons to internal and
        external methods.
        """

        super().__init__()

        # set gui state variables
        self.zoomFactor = 1
        self.pointSize = constants.DEFAULTPOINTSIZE
        self.lineWidth = constants.DEFAULTLINEWIDTH
        self.imageFileName = None

        # connect buttons
        self.openImageButton.clicked.connect(self.openImage)
        self.saveSessionButton.clicked.connect(self.saveSession)
        self.loadSessionButton.clicked.connect(self.loadSession)
        self.screenshotButton.clicked.connect(self.saveScreenshot)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.resetButton.clicked.connect(self.resetImage)
        self.calcMomentumButton.clicked.connect(self.calcTrackMomentum)
        self.calcDensityButton.clicked.connect(self.calcOptDensity)
        self.calcAngleButton.clicked.connect(self.calcAngle)
        self.placeMarkerButton.clicked.connect(self.placeMarkerButtonFunc)
        self.drawRefButton.clicked.connect(self.drawRefButtonFunc)

        # connect mouse events
        self.scenePixmap.mousePressEvent = self.mousePress
        self.scenePixmap.mouseReleaseEvent = self.mouseRelease
        self.scenePixmap.mouseMoveEvent = self.mouseMove

        # connect key presses
        self.baseWidget.keyPressEvent = self.keyPressEvent

        # connect other events
        self.dlLineEdit.textEdited.connect(self.changedLCircles)
        self.markerList.itemSelectionChanged.connect(self.highlightPoint)

    ###########################
    # Mouse Event Methods
    ###########################
    def mousePress(self, event):
        """The following function draws a point (ellipse) when called with
        a mousePressEvent at specified event location. Or if the Angle draw
        mode is selected, it will send the drawing to the respective function"""

        if self.placeMarkerButton.isChecked():
            self.markerList.addMarker(
                event.pos().x(), event.pos().y(), 
                self.pointSize, self.lineWidth, self.scene)

        elif self.drawRefButton.isChecked():
            self.angleRefLine.setInitialPoint(
                event.pos().x(), event.pos().y(),
                self.pointSize, self.lineWidth, self.scene)

        else:
            # set initial reference for an image pan
            self.sceneView.lastMousePos = self.sceneView.mapFromScene(
                                              event.pos())

    def mouseRelease(self, event):
        """The following function draws the intial and final points for the
        angle reference. It is also connected to the mouse release event signal
        as well"""

        if self.angleRefLine.isBeingDrawn():
            self.angleRefLine.setFinalPoint(
                event.pos().x(), event.pos().y(),
                self.pointSize, self.lineWidth, self.scene)

    def mouseMove(self, event):
        """The following function draws a line between the intial point and the current
        mouse position. It is connected to mouse drag signal"""

        if self.angleRefLine.isBeingDrawn():
            self.angleRefLine.drawLine(
                event.pos().x(), event.pos().y(), self.lineWidth, self.scene)

        if not (self.placeMarkerButton.isChecked()
                or self.drawRefButton.isChecked()):
            # manually implement image panning
            hbar = self.sceneView.horizontalScrollBar()
            vbar = self.sceneView.verticalScrollBar()
            delta = self.sceneView.mapFromScene(
                        event.pos()) - self.sceneView.lastMousePos
            self.sceneView.lastMousePos = self.sceneView.mapFromScene(
                                              event.pos())
            hbar.setValue(hbar.value() - delta.x())
            vbar.setValue(vbar.value() - delta.y())

    ##############################
    # Keypress Events
    ##############################
    def keyPressEvent(self, event):
        """The following function handles keypressEvents used to select and
        manipulate points in the QListWidget.
        """

        currentPoint = self.markerList.currentItem()
        dx, dy = 0, 0

        # check if the Shift key was held
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            isShift = True
        else:
            isShift = False

        # WASD to move individual points around.
        if event.key() == QtCore.Qt.Key_W:
            dy = -1

        elif event.key() == QtCore.Qt.Key_S:
            dy = 1

        elif event.key() == QtCore.Qt.Key_D:
            dx = 1

        elif event.key() == QtCore.Qt.Key_A:
            dx = -1

        if dx or dy:
            if isShift and self.pointSize >= 2:
                dx *= self.pointSize / 2
                dy *= self.pointSize / 2
            if currentPoint:
                currentPoint.move(dx, dy)
        
        # F/V to select points in list.
        elif event.key() == QtCore.Qt.Key_V:
            self.markerList.selectNext()

        elif event.key() == QtCore.Qt.Key_F:
            self.markerList.selectPrevious()

        # G/H for setting start and end point
        elif event.key() == QtCore.Qt.Key_G:
            if currentPoint:
                self.markerList.setStartPoint(currentPoint)

        elif event.key() == QtCore.Qt.Key_H:
            if currentPoint:
                self.markerList.setEndPoint(currentPoint)

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            if currentPoint:
                self.markerList.deleteMarker(currentPoint)

    ##############################
    # File Dialog Methods
    ##############################
    def openImage(self, fileName=None):
        """The following function opens a file dialog and then loads
        user-specified image."""

        if not fileName:
            # open file dialog to obtain image file name
            self.imageFileName = QtWidgets.QFileDialog.getOpenFileName(
                None, "Open File", QtCore.QDir.currentPath(),
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
                "NOTICE: Cannot open file as image: {}.".format(self.imageFileName))
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

        if self.sceneImage.isNull():
            self.displayMessage("NOTICE: Nothing to save.")
            return

        # open file dialog for selecting a file to save to
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save Session", "./untitled.json",
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        if not fileName:
            return
        else:
            # create a dictionary with the data we want to save
            saveData = {}
            saveData['imageFileName'] = self.imageFileName

            if self.markerList.count() > 0:
                points = []
                for row in range(self.markerList.count()):
                    point = self.markerList.item(row)
                    pointDict = {}
                    pointDict['id'] = point.id
                    pointDict['designation'] = point.designation
                    pointDict['x'] = point.ellipse.rect().center().x()
                    pointDict['y'] = point.ellipse.rect().center().y()
                    points.append(pointDict)
                saveData["points"] = points

            if self.dlLineEdit.text() not in ["0", ""]:
                saveData['dl'] = self.dlLineEdit.text()

            if self.angleRefLine.finalPoint:
                initialPointDict = {}
                initialPointDict[
                    'x'] = self.angleRefLine.initialPoint.rect().center().x()
                initialPointDict[
                    'y'] = self.angleRefLine.initialPoint.rect().center().y()
                saveData['refInitialPoint'] = initialPointDict
                finalPointDict = {}
                finalPointDict[
                    'x'] = self.angleRefLine.finalPoint.rect().center().x()
                finalPointDict[
                    'y'] = self.angleRefLine.finalPoint.rect().center().y()
                saveData['refFinalPoint'] = finalPointDict

            # serialize the save data dictionary and save to file
            with open(fileName, 'w') as saveFile:
                json.dump(saveData, saveFile, indent=4)

    def loadSession(self):
        """Load analysis session from a .json file."""

        # open file dialog for selecting a file to load from
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            None, "Load Session", QtCore.QDir.currentPath(),
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        if not fileName:
            return
        else:
            with open(fileName, 'r') as loadFile:
                try:
                    loadData = json.load(loadFile)
                except:
                    self.displayMessage("NOTICE: Invalid JSON file: {}".format(fileName))
                    return

                imageFileName = loadData.get('imageFileName')

                if not imageFileName:
                    self.displayMessage("NOTICE: No image file name found in saved session data: {}".format(fileName))
                    return

                opened = self.openImage(imageFileName)
                if not opened:
                    return

                points = loadData.get('points')
                if points:
                    for point in points:
                        pointId = point["id"]
                        pointDesignation = point["designation"]
                        x = point['x']
                        y = point['y']
                        addedMarker = self.markerList.addMarker(
                                          x, y, self.pointSize,
                                          self.lineWidth, self.scene)
                        addedMarker.setDesignation(pointDesignation)

                dl = loadData.get('dl')
                if dl:
                    self.dlLineEdit.setText(dl)

                refInitialPoint = loadData.get('refInitialPoint')
                refFinalPoint = loadData.get('refFinalPoint')
                if refInitialPoint and refFinalPoint:
                    self.angleRefLine.setInitialPoint(
                        refInitialPoint['x'], refInitialPoint['y'],
                        self.pointSize, self.lineWidth, self.scene)
                    self.angleRefLine.drawLine(
                        refFinalPoint['x'], refFinalPoint['y'],
                        self.lineWidth, self.scene)
                    self.angleRefLine.setFinalPoint(
                        refFinalPoint['x'], refFinalPoint['y'],
                        self.pointSize, self.lineWidth, self.scene)

    def saveScreenshot(self):
        """Save the currently visible part of the scene view to an
        image.
        """

        if self.sceneImage.isNull():
            self.displayMessage("NOTICE: There is nothing to take screenshot of.")
            return

        screenshot = self.sceneView.grab()
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save Screenshot", "./untitled.png",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff *.tif)")[0]
        if not screenshot.save(fileName):
            self.displayMessage("NOTICE: Unable to save screenshot.")

    ##############################
    # Zoom Methods
    ##############################
    def zoomIn(self):
        """Scale the image by ZOOMINFACTOR."""

        self.scaleImage(constants.ZOOMINFACTOR)

    def zoomOut(self):
        """Scale the image by ZOOMOUTFACTOR."""

        self.scaleImage(constants.ZOOMOUTFACTOR)

    def scaleImage(self, factor):
        """The following helper function scales images and points."""

        self.zoomFactor = self.zoomFactor * factor
        self.sceneView.scale(factor, factor)

        # scale the drawn points when zooming
        self.pointSize /= factor
        self.lineWidth /= factor

        self.markerList.rescale(self.pointSize, self.lineWidth)
        self.momentumArc.rescale(self.lineWidth)
        self.angleRefLine.rescale(self.pointSize, self.lineWidth)
        if self.tangentLine:
            self.tangentLine.rescale(self.lineWidth)

    ##############################
    # Console Methods
    ##############################
    def displayMessage(self, msg):
        """Write msg, a string, along with the message number to the console.
        """

        # the text browser's document block count will be 1 if there are zero
        # blocks or one block. Therefore, to check if the block count is zero,
        # check the document's character count, which is 1 if there are zero
        # blocks
        if self.consoleTextBrowser.document().characterCount() == 1:
            msgNumber = 1
        # otherwise the message number is 1 more than the current block count
        else:
            msgNumber = self.consoleTextBrowser.document().blockCount() + 1

        # prepend the message number to msg
        msg = "[{}]  {}".format(msgNumber, msg)
        # add the message to the console
        self.consoleTextBrowser.append(msg)

    ##############################
    # Calculation Methods
    ##############################
    def calcTrackMomentum(self):
        """Fit a circle to the track markers in markerList and print the 
        parameters of the fit along with the momentum computed from these
        parameters to the console. Draw the momentum arc using the fit
        parameters.
        """

        # need a minimum of 3 points to fit a circle
        if self.markerList.count() < 3:
            self.displayMessage("NOTICE: Less than 3 points to fit.")
            return

        # return if the start point has not yet been defined
        if not self.markerList.getStartPoint():
            self.displayMessage(
                "NOTICE: Track start point must be selected first.")
            return

        # return if the end point has not yet been defined
        if not self.markerList.getEndPoint():
            self.displayMessage(
                "NOTICE: Track end point must be selected first.")
            return

        # remove the tangent line if it was drawn
        if self.tangentLine:
            self.tangentLine.scene().removeItem(self.tangentLine)
            self.tangentLine = None

        # fit a circle to the track markers and store the fit parameters
        # in the fittedCircle attribute
        self.fittedCircle = circlefit.fitCircle(self.markerList)

        # print the fit parameters to the console
        self.displayMessage("---Fitted Circle---")
        self.displayMessage(
            "Center (x coord):\t{:.5f} +/- {:.5f} [px]".format(
                self.fittedCircle['centerX'], 
                self.fittedCircle['centerXErr']))
        self.displayMessage(
            "Center (y coord):\t{:.5f} +/- {:.5f} [px]".format(
                self.fittedCircle['centerY'],
                self.fittedCircle['centerYErr']))
        self.displayMessage(
            "Radius (px):\t{:.5f} +/- {:.5f} [px]".format(
                self.fittedCircle['radius'],
                self.fittedCircle['radiusErr']))
        # convert the radius from px to cm and print to console
        self.displayMessage(
            "Radius (cm):\t{:.5f} +/- {:.5f} (Stat) +/- {:.5f} (Cal) [cm]".format(
                self.fittedCircle['radius']*constants.CMPERPX, 
                self.fittedCircle['radiusErr']*constants.CMPERPX, 
                self.fittedCircle['radius']*constants.ERRCMPERPX))

        # compute the track momentum from the track radius and print to
        # console. Given a track radius, R, in cm, a magnetic field, B,
        # in kG and the speed of light, c, in Giga metres per second, the
        # track momentum in MeV/c can be computed as p = c*B*R
        self.displayMessage("---Track Momentum---")
        self.displayMessage(
            "Track Momentum:\t{:.5f} +/- {:.5f} (Stat) +/- {:.5f} (Cal) [MeV/c]".format(
                constants.C*constants.MAGNETICFIELD* \
                self.fittedCircle['radius']*constants.CMPERPX,
                constants.C*constants.MAGNETICFIELD* \
                self.fittedCircle['radiusErr']*constants.CMPERPX, 
                constants.C*constants.MAGNETICFIELD* \
                self.fittedCircle['radius']*constants.ERRCMPERPX))

        # compute the start and span angles of the momentum arc using the start
        # and end markers and the fitted circle center
        startAngle = self.markerList.getStartPoint().getAngle(
                         (self.fittedCircle['centerX'],
                          self.fittedCircle['centerY']))
        spanAngle = self.markerList.getEndPoint().getAngle(
                        (self.fittedCircle['centerX'], 
                         self.fittedCircle['centerY']), 
                        self.markerList.getStartPoint())

        # get the dL value from the dL text box. If the box is empty, use
        # a value of 0
        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        # draw the momentum arc using the parameters of the fitted circle, the
        # start and span angles and the dL
        self.momentumArc.draw(
            self.fittedCircle['centerX'], self.fittedCircle['centerY'],
            self.fittedCircle['radius'], startAngle, spanAngle, dl,
            self.lineWidth, self.scene)

    def calcOptDensity(self):
        """Calculate the optical density of the portion of a track that is
        covered by the momentum arc and print it to the console.
        """

        # return if track momentum has not yet been calculated
        if not self.momentumArc.centralArc:
            self.displayMessage(
                "NOTICE: Track momentum must be calculated first.")
            return

        # get the dL value from the dL text box. If the box is empty, use
        # a value of zero
        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        # if the dl is 0, return
        if dl == 0:
            self.displayMessage("NOTICE: dL must be non-zero.")
            return

        # compute the total blackness of all the pixels contained within the
        # portion of the sceneImage that is covered by the momentum arc
        # note: ArcItems have start and span angles in units of millionths of a
        # degree, so divide them by 1e6
        blackness, blacknessErr = optdensity.calcBlackness(
            self.sceneImage, self.fittedCircle, dl,
            self.momentumArc.centralArc.startAngle() / 1e6,
            self.momentumArc.centralArc.spanAngle() / 1e6)

        # calculate the length of the momentum arc in px
        trackLengthPx = self.fittedCircle['radius'] * \
                 self.momentumArc.centralArc.spanAngle() / 1e6 * (math.pi / 180)

        # convert track length from px to cm
        trackLengthCm = trackLengthPx * constants.CMPERPX
        trackLengthCmErr = trackLengthPx * constants.ERRCMPERPX

        # calculate optical density - total blackness per unit length
        optDensity = blackness / trackLengthCm
        optDensityErr = optDensity * (
                (trackLengthCmErr / trackLengthCm)**2 + \
                (blacknessErr / blackness)**2)**0.5

        # print the optical density to the console
        self.displayMessage("---Optical Density---")
        self.displayMessage(
            "Optical density:\t{:.5f} +/- {:.5f} [1/cm] (with dL={})".format(
                optDensity, optDensityErr, dl))

    def calcAngle(self):
        """Calculate the angle between the reference line and the tangent to
        the fitted circle at the designated start point and print it to the
        console.
        """

        # return if track momentum has not yet been calculated
        if not self.momentumArc.centralArc:
            self.displayMessage(
                "NOTICE: Track momentum must be calculated first.")
            return

        # return if the start point has not yet been defined
        if not self.markerList.getStartPoint():
            self.displayMessage(
                "NOTICE: Start track point must be selected first.")
            return

        # return if the angle reference line has not yet been drawn
        if not self.angleRefLine.finalPoint:
            self.displayMessage(
                "NOTICE: Angle Reference Line must be drawn first.")
            return

        # get the tangent line to the fitted circle at the start point along
        # with the two lines that the tangent may lie between within error
        tangentLine, tangentErrA, tangentErrB = anglecalc.tangentCalc(
                          self.fittedCircle, self.markerList.getStartPoint())

        # if a tangent line has been drawn before, remove the old tangent
        if self.tangentLine:
            self.tangentLine.scene().removeItem(self.tangentLine)
        # add the new tangent line to the graphics scene
        self.tangentLine = tangent.TangentLine(tangentLine,
                                               self.lineWidth, self.scene)

        # compute the angle between the tangent line and the reference line
        # along with the error on the angle
        angle, angleErr = anglecalc.openingAngle(tangentLine,
                                                 tangentErrA, tangentErrB,
                                                 self.angleRefLine)

        # print the opening angle to the console
        self.displayMessage("---Opening Angle---")
        self.displayMessage("Opening Angle:\t{:.5f} +/- {:.5f}".format(angle,
                                                                     angleErr))

    ##############################
    # Connection to Other Events
    ##############################
    def changedLCircles(self, value):
        """The following helper function changes the diameter of dL curves.
        Connected to changing values on the dL field"""

        if not value:
            return

        dl = float(value)

        self.momentumArc.updateArcs(dl)

    def highlightPoint(self):
        self.markerList.highlightCurrent()

    def placeMarkerButtonFunc(self):
        """The following helper function creates the changes when the
        place track marker mode button is toggled"""

        self.drawRefButton.setChecked(False)

    def drawRefButtonFunc(self):
        """The following helper function creates the changes when the
        draw angle reference mode button is toggled. Resets the drawn
        angle reference as well"""

        self.placeMarkerButton.setChecked(False)

    ##############################
    # Reset
    ##############################
    def resetImage(self):
        """The following function resets image transformations,
        and clears point list and console output."""

        # remove all points, arcs and lines
        self.markerList.empty()
        self.angleRefLine.reset()
        self.momentumArc.reset()
        if self.tangentLine:
            self.tangentLine.scene().removeItem(self.tangentLine)
            self.tangentLine = None

        # clear console output
        self.consoleTextBrowser.clear()

        # reset view scale and fit image in view
        self.scaleImage(1 / self.zoomFactor)

        self.pointSize = constants.DEFAULTPOINTSIZE
        self.lineWidth = constants.DEFAULTLINEWIDTH

        if not self.sceneImage.isNull():
            scaleFactor = 1

            heightRatio = (self.sceneView.height()-2) / self.sceneImage.height()
            widthRatio = (self.sceneView.width()-2) / self.sceneImage.width()

            if heightRatio < widthRatio:
                scaleFactor = heightRatio
            else:
                scaleFactor = widthRatio

            self.scaleImage(scaleFactor)

        self.dlLineEdit.setText("0")
