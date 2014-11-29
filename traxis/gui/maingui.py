import math
import json
from PyQt5 import QtWidgets, QtGui, QtCore
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

        # calibration
        self.nomCalcmPerPix = 0.01188
        self.errCalcmPerPix = 0.00090

        # set gui state variables
        self.num_messages = 0
        self.nUserClickOnPicture = 0
        self.zoomFactor = 1
        self.pointSize = 10
        self.lineWidth = 2.5
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
        self.baseWidget.resizeEvent = self.resizeEvent

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
            # Count the number of times user has clicked on the picture.
            # If more than 3 times, display a help message.
            self.nUserClickOnPicture += 1
            if self.nUserClickOnPicture == 3:
                self.nUserClickOnPicture = 0
                self.displayMessage(
                    "HELP - To place track marker, first select 'Place Track Marker' button")
                self.displayMessage(
                    "HELP - To draw angle reference, first select 'Draw Angle Reference' button")

    def mouseRelease(self, event):
        """The following function draws the intial and final points for the
        angle reference. It is also connected to the mouse release event signal
        as well"""

        self.angleRefLine.setFinalPoint(
            event.pos().x(), event.pos().y(),
            self.pointSize, self.lineWidth)

    def mouseMove(self, event):
        """The following function draws a line between the intial point and the current
        mouse position. It is connected to mouse drag signal"""

        self.angleRefLine.drawLine(
            event.pos().x(), event.pos().y(), self.lineWidth)

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
                #self.scene.update()
        
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

        elif event.key() == QtCore.Qt.Key_B:
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

        elif event.key() == QtCore.Qt.Key_L:
            if self.drawRefButton.isChecked():
                self.drawRefButton.setChecked(False)
            else:
                self.drawRefButton.setChecked(True)

            self.drawRefButtonFunc()

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            if currentPoint:
                self.pointListWidget.deleteMarker(currentPoint)

    def highlightPoint(self):
        self.pointListWidget.highlightCurrent()
        #self.scene.update()

    ##############################
    # File Dialog Methods
    ##############################
    def openImage(self, fileName=None):
        """The following function opens a file dialog and then loads
        user-specified image."""

        if not fileName:
            # open file dialog to obtain image file name
            self.imageFileName = QtWidgets.QFileDialog.getOpenFileName(
                self.baseWidget, "Open File", QtCore.QDir.currentPath(),
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
            self.baseWidget, "Save Session", "./untitled.json",
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
            self.baseWidget, "Load Session", QtCore.QDir.currentPath(),
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

    def saveScreenshot(self):
        """Save the currently visible part of the scene view to an
        image.
        """
        screenshot = self.sceneView.grab()
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            self.baseWidget, "Save Screenshot", "./untitled.png",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff *.tif)")[0]
        if not screenshot.save(fileName):
            self.displayMessage("Unable to save screenshot")

    ##############################
    # Zoom Methods
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

        # scale the drawn points when zooming
        self.pointSize /= factor
        self.lineWidth /= factor

        self.pointListWidget.rescale(self.pointSize, self.lineWidth)
        self.momentumArc.rescale(self.lineWidth)
        self.angleRefLine.rescale(self.pointSize, self.lineWidth)

        #self.scene.update()

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

        # need a minimum of 3 points to fit a circle
        if self.pointListWidget.count() < 3:
            self.displayMessage("ERROR: Less than 3 points to fit.")
            return

        # check if start point was defined
        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "ERROR: Initial point has not been defined yet.")
            return

        # check if end point was defined
        if not self.pointListWidget.getEndPoint():
            self.displayMessage(
                "ERROR: End point has not been defined yet.")
            return

        # fit a circle to placed points.
        fitted_circle = circlefit.circleFit(self.pointListWidget)
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
            str("Fitted R_o:\t %f +/- %f (Stat) +/- %f (Cal) [cm]" % 
                (fitted_circle[2][0]*self.nomCalcmPerPix, 
                fitted_circle[2][1]*self.nomCalcmPerPix, 
                fitted_circle[2][0]*self.errCalcmPerPix)))
        self.displayMessage(
            str("Fitted P_o:\t %f +/- %f (Stat) +/- %f (Cal) [MeV]" 
                % (0.3*15.5*fitted_circle[2][0]*self.nomCalcmPerPix, 
                0.3*15.5*fitted_circle[2][1]*self.nomCalcmPerPix, 
                0.3*15.5*fitted_circle[2][0]*self.errCalcmPerPix)))

        startAngle = optdensity.getAngle([self.fittedX0, self.fittedY0], 
                self.pointListWidget.getStartPoint().ellipse, 
                [self.fittedX0 + 1, self.fittedY0 + 0])
        spanAngle = optdensity.getAngle([self.fittedX0, self.fittedY0], 
                self.pointListWidget.getEndPoint().ellipse, 
                self.pointListWidget.getStartPoint().ellipse)

        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        self.momentumArc.draw(
            self.fittedX0, self.fittedY0, self.fittedR0,
            startAngle, spanAngle, dl, self.lineWidth)

    def calcOptDen(self):
        """The following function is used to calculate optical density of
        drawn points on image with a specified dL."""

        # Return if track momentum has NOT been calculated.
        if not self.momentumArc.centralArc:
            self.displayMessage(
                "ERROR: Track momentum has not been calculated yet.")
            return

        if self.dlLineEdit.text():
            dl = float(self.dlLineEdit.text())
        else:
            dl = 0

        if dl == 0:
            self.displayMessage(
                "ERROR: dL must be non-zero.")
            return

        # Check if start point was defined.
        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "ERROR: Initial point has not been defined yet.")
            return

        # Check if end point was defined
        if not self.pointListWidget.getEndPoint():
            self.displayMessage(
                "ERROR: End point has not been defined yet.")
            return

        # Assigned fitted circle to pass to optical density function.
        self.tmp_circle = self.circleInfo

        # Call function to compute optical density.
        self.displayMessage("Computing optical density...")

        self.optDens, self.errOptDens, self.trackLengthPix  = optdensity.calcOptDensity(
            self.sceneImage, self.tmp_circle, dl,
            self.pointListWidget.getStartPoint().ellipse,
            self.pointListWidget.getEndPoint().ellipse)
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

        if not self.momentumArc.centralArc:
            self.displayMessage(
                "ERROR: Track momentum has not been calculated yet.")
            return

        if not self.pointListWidget.getStartPoint():
            self.displayMessage(
                "ERROR: Initial point has not been defined yet.")
            return

        if not self.angleRefLine.finalPoint:
            self.displayMessage(
                "ERROR: Angle Line reference not drawn.")
            return

        angleInfo = anglecalc.angleCalc(self, self.circleInfo,
                              self.pointListWidget.getStartPoint().ellipse,
                              self.angleRefLine.line)

        self.displayMessage(
            str("opening Angle %f +/- %f" % (angleInfo[0], angleInfo[1])))

    ##############################
    # Connection to Other Buttons
    ##############################
    def changedLCircles(self, value):
        """The following helper function changes the diameter of dL curves.
        Connected to changing values on the dL field"""

        if not value:
            return

        dl = float(value)

        self.momentumArc.updateArcs(dl)

        #self.scene.update()

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
    # Resize Function
    ##############################
    def resizeEvent(self, event):
        self.sceneView.setMinimumSize(
            QtCore.QSize(0, self.baseWidget.size().height() / 1.65))

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

        self.pointSize = 10
        self.lineWidth = 2.5

        if not self.sceneImage.isNull():
            scaleFactor = 1

            height_ratio = self.sceneView.height() / self.sceneImage.height()
            width_ratio = self.sceneView.width() / self.sceneImage.width()

            if height_ratio < width_ratio:
                scaleFactor = height_ratio
            else:
                scaleFactor = width_ratio

            self.scaleImage(scaleFactor)


        self.nUserClickOnPicture = 0

        self.dlLineEdit.setText("0")

        # reset count of messages printed to console
        self.num_messages = 0
