import math
import json
from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants
from traxis.gui import skeleton
from traxis.calc import anglecalc, circlefit, optdensity


class MainGui(skeleton.GuiSkeleton):

    """Main GUI class that inherits from base skeleton GUI class and implements
    logic that connects buttons and functions together. Defines internal
    methods to carry out various UI actions (zoom, opening images, etc.)
    and calls external functions that have been imported below.
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
        self.calcMomentumButton.clicked.connect(self.calcTrackMom)
        self.calcDensityButton.clicked.connect(self.calcOptDen)
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
        self.pointListWidget.itemSelectionChanged.connect(self.highlightPoint)

    ###########################
    # Mouse Event Methods
    ###########################
    def mousePress(self, event):
        """The following function draws a point (ellipse) when called with
        a mousePressEvent at specified event location. Or if the Angle draw
        mode is selected, it will send the drawing to the respective function"""

        if self.placeMarkerButton.isChecked():
            self.pointListWidget.addMarker(
                event.pos().x(), event.pos().y(), 
                self.pointSize, self.lineWidth, self.scene)

        elif self.drawRefButton.isChecked():
            self.angleRefLine.setInitialPoint(
                event.pos().x(), event.pos().y(),
                self.pointSize, self.lineWidth)

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
                self.pointSize, self.lineWidth)

    def mouseMove(self, event):
        """The following function draws a line between the intial point and the current
        mouse position. It is connected to mouse drag signal"""

        if self.angleRefLine.isBeingDrawn():
            self.angleRefLine.drawLine(
                event.pos().x(), event.pos().y(), self.lineWidth)

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

        currentPoint = self.pointListWidget.currentItem()
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
            self.pointListWidget.selectNext()

        elif event.key() == QtCore.Qt.Key_F:
            self.pointListWidget.selectPrevious()

        # G/H key for setting start and end point
        elif event.key() == QtCore.Qt.Key_G:
            if currentPoint:
                self.pointListWidget.setStartPoint(currentPoint)

        elif event.key() == QtCore.Qt.Key_H:
            if currentPoint:
                self.pointListWidget.setEndPoint(currentPoint)

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            if currentPoint:
                self.pointListWidget.deleteMarker(currentPoint)

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

            if self.pointListWidget.count() > 0:
                points = []
                for row in range(self.pointListWidget.count()):
                    point = self.pointListWidget.item(row)
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
                        addedMarker = self.pointListWidget.addMarker(
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
                        self.pointSize, self.lineWidth)
                    self.angleRefLine.drawLine(
                        refFinalPoint['x'], refFinalPoint['y'],
                        self.lineWidth)
                    self.angleRefLine.setFinalPoint(
                        refFinalPoint['x'], refFinalPoint['y'],
                        self.pointSize, self.lineWidth)

                self.resetImage()

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
        """The following function zooms image by 125% when called."""

        self.scaleImage(constants.ZOOMINFACTOR)

    def zoomOut(self):
        """The following function zooms image by 80% when called."""

        self.scaleImage(constants.ZOOMOUTFACTOR)

    def scaleImage(self, factor):
        """The following helper function scales images and points."""

        self.zoomFactor = self.zoomFactor * factor
        self.sceneView.scale(factor, factor)

        # scale the drawn points when zooming
        self.pointSize /= factor
        self.lineWidth /= factor

        self.pointListWidget.rescale(self.pointSize, self.lineWidth)
        self.momentumArc.rescale(self.lineWidth)
        self.angleRefLine.rescale(self.pointSize, self.lineWidth)

    ##############################
    # Console Methods
    ##############################
    def displayMessage(self, msg):
        """The following function is used to write messages to console."""

        if self.consoleTextBrowser.document().characterCount() == 1:
            msgNumber = 1
        else:
            msgNumber = self.consoleTextBrowser.document().blockCount() + 1
        msg = "[{}]  {}".format(msgNumber, msg)
        self.consoleTextBrowser.append(msg)

    ##############################
    # Main Calculation Methods
    ##############################
    def calcTrackMom(self):
        """The following function is used to calculate track momentum of
        drawn points on image and then draw a fitted circle to them."""

        # need a minimum of 3 points to fit a circle
        if self.pointListWidget.count() < 3:
            self.displayMessage("NOTICE: Less than 3 points to fit.")
            return

        # check if start point was defined
        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "NOTICE: Start track point must be selected first.")
            return

        # check if end point was defined
        if not self.pointListWidget.getEndPoint():
            self.displayMessage(
                "NOTICE: End track point must be selected first.")
            return

        # fit a circle to placed points.
        self.fittedCircle = circlefit.circleFit(self.pointListWidget)

        self.displayMessage("---Fitted Circle---")

        self.displayMessage(
            str("Center (x coord):\t{:.5f} +/- {:.5f} [px]".format(self.fittedCircle[0][0],
                                                        self.fittedCircle[0][1])))
        self.displayMessage(
            str("Center (y coord):\t{:.5f} +/- {:.5f} [px]".format(self.fittedCircle[1][0],
                                                        self.fittedCircle[1][1])))
        self.displayMessage(
            str("Radius (px):\t{:.5f} +/- {:.5f} [px]".format(self.fittedCircle[2][0],
                                                        self.fittedCircle[2][1])))
        self.displayMessage(
            str("Radius (cm):\t{:.5f} +/- {:.5f} (Stat) +/- {:.5f} (Cal) [cm]".format(
                self.fittedCircle[2][0]*constants.CMPERPX, 
                self.fittedCircle[2][1]*constants.CMPERPX, 
                self.fittedCircle[2][0]*constants.ERRCMPERPX)))

        self.displayMessage("---Track Momentum---")

        # http://www.lancaster.ac.uk/users/spc/resources/alevel/motmag.pdf
        self.displayMessage(
            str("Track Momentum:\t{:.5f} +/- {:.5f} (Stat) +/- {:.5f} (Cal) [MeV/c]".format(
                constants.C*constants.MAGNETICFIELD*self.fittedCircle[2][0]*constants.CMPERPX,
                constants.C*constants.MAGNETICFIELD*self.fittedCircle[2][1]*constants.CMPERPX, 
                constants.C*constants.MAGNETICFIELD*self.fittedCircle[2][0]*constants.ERRCMPERPX)))

        startAngle = optdensity.getAngle([self.fittedCircle[0][0], self.fittedCircle[1][0]], 
                self.pointListWidget.getStartPoint().ellipse, 
                [self.fittedCircle[0][0] + 1, self.fittedCircle[1][0] + 0])
        spanAngle = optdensity.getAngle([self.fittedCircle[0][0], self.fittedCircle[1][0]], 
                self.pointListWidget.getEndPoint().ellipse, 
                self.pointListWidget.getStartPoint().ellipse)

        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        self.momentumArc.draw(
            self.fittedCircle[0][0], self.fittedCircle[1][0], self.fittedCircle[2][0],
            startAngle, spanAngle, dl, self.lineWidth)

    def calcOptDen(self):
        """The following function is used to calculate optical density of
        drawn points on image with a specified dL."""

        # Return if track momentum has NOT been calculated.
        if not self.momentumArc.centralArc:
            self.displayMessage(
                "NOTICE: Track momentum must be calculated first.")
            return

        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        if dl == 0:
            self.displayMessage("NOTICE: dL must be non-zero.")
            return

        # Check if start point was defined.
        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "NOTICE: Start track point must be selected first.")
            return

        # Check if end point was defined
        if not self.pointListWidget.getEndPoint():
            self.displayMessage(
                "NOTICE: End track point must be selected first.")
            return

        # Call function to compute optical density
        self.optDens, self.errOptDens, self.trackLengthPix  = optdensity.calcOptDensity(
            self.sceneImage, self.fittedCircle, dl,
            self.pointListWidget.getStartPoint().ellipse,
            self.pointListWidget.getEndPoint().ellipse)
        #self.displayMessage("Total track blackness:\t{:.5f} +/- {:.5f}".format(self.optDens, self.errOptDens))
        self.displayMessage("---Track Length & Optical Density---")
        self.displayMessage("Track Length (px):\t{:.5f} [px]".format(self.trackLengthPix))

        # Calculation of Variables
        self.trackLengthcm = self.trackLengthPix * constants.CMPERPX;
        self.trackLengtherr = self.trackLengthPix * constants.ERRCMPERPX;
        self.optDenspercm = self.optDens/self.trackLengthcm;
        self.optDenspercmErr = self.optDenspercm * math.sqrt(
                math.pow(self.trackLengtherr/self.trackLengthcm,2)+math.pow(self.errOptDens/self.optDens,2))

        self.displayMessage("Track Length (cm):\t{:.5f} +/- {:.5f} [cm]".format(self.trackLengthcm, self.trackLengtherr))
        self.displayMessage("Optical density:\t{:.5f} +/- {:.5f} [1/cm]".format(self.optDenspercm, self.optDenspercmErr))

    def calcAngle(self):
        """The following function is used to calculate the angle between
        intial tangent and specified references"""

        if not self.momentumArc.centralArc:
            self.displayMessage(
                "NOTICE: Track momentum must be calculated first.")
            return

        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "NOTICE: Start track point must be selected first.")
            return

        if not self.angleRefLine.finalPoint:
            self.displayMessage(
                "NOTICE: Angle Reference Line must be drawn first.")
            return

        angleInfo = anglecalc.angleCalc(self, self.fittedCircle,
                              self.pointListWidget.getStartPoint().ellipse,
                              self.angleRefLine.line)

        self.displayMessage("---Opening Angle---")
        self.displayMessage("Opening Angle:\t{:.5f} +/- {:.5f}".format(angleInfo[0],
                                                             angleInfo[1]))

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
        self.pointListWidget.highlightCurrent()

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
        self.pointListWidget.empty()
        self.angleRefLine.reset()
        self.momentumArc.reset()

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
