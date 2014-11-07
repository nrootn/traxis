__author__ = "Syed Haider Abidi,  Nooruddin Ahmed and Christopher Dydula"

from PyQt5 import QtWidgets, QtGui, QtCore

# External methods
from skeleton import GuiSkeleton
from optDensity import calcOptDensity
from circleFit import circleFit


class MainGui(GuiSkeleton):
    """Main GUI class that inherits from base skeleton GUI class and implements
    logic that connects buttons and functions together. Defines internal
    methods to carry out various UI actions (zoom, opening images, etc.)
    and calls external functions that have been imported below.
    """

    def __init__(self, main_window):
        """Initialize gui skeleton and connect buttons to internal and
        external methods.
        """

        super().__init__(main_window)

        # number of messages printed to the console
        self.num_messages = 0

        # Creates QGraphicsScene to be used to display images.
        self.scene = QtWidgets.QGraphicsScene()
        self.view = QtWidgets.QGraphicsView(self.scene)

        # Load a blank image by default. This is required by QT
        # to be able to load images after.
        self.pixmap_item = QtWidgets.QGraphicsPixmapItem(
            QtGui.QPixmap('bkgPicture.png'), None)
        self.scene.addItem(self.pixmap_item)
        self.scrollArea.setWidget(self.view)

        # Set up button to load images.
        self.btn_openImage.clicked.connect(self.openImage)

        # Set up button to zoom in/out on image.
        self.zoomFactor = 1
        self.btn_ZoomIn.clicked.connect(self.zoomIn)
        self.btn_ZoomOut.clicked.connect(self.zoomOut)

        # Set up point drawing at mousepress on image.
        self.sizeOfEllipse = 5
        self.widthOfEllipse = 2.5
        self.nEllipseDrawn = 0
        self.mapNametoPoint = {}
        self.pixmap_item.mousePressEvent = self.pixelSelect

        # Set up navigation of point list.
        self.centralWidget.keyPressEvent = self.keyPressEvent

        # Set up button to reset the tool.
        self.btn_reset.clicked.connect(self.resetImage)

        # Set up button to calculate track momentum.
        self.btn_trackMom.clicked.connect(self.calcTrackMom)

        # Set up button to calculate optical density.
        self.btn_optDen.clicked.connect(self.calcOptDen)

        # Set up text field that specifies dL (user-specified width).
        self.setDlLineEdit.textEdited.connect(self.changedLCircles)

        # Used for debugging purposes.
        self.nUserClickOnPicture = 0
        self.hasTrackMomentumCalc = False
        self.hasDrawndLCurves = False

        self.test = QtWidgets.QGraphicsEllipseItem(3, 5, 10, 10)

        self.centralWidget.resizeEvent = (self.resizeEvent)

    def pixelSelect(self, event):
        """The following function draws a point (ellipse) when called with
        a mousePressEvent at specified event location."""

        # Place an event only if 'place marker' button has been pressed.
        if not self.btn_placeMar.isChecked():
            # Count the number of times user has clicked on the picture.
            # If more than 3 times, display a help message.
            self.nUserClickOnPicture += 1
            if self.nUserClickOnPicture == 3:
                self.nUserClickOnPicture = 0
                self.displayMessage(
                    "HELP - To place track marker, first select 'Place Track Marker' button")
            return

        # Set colour of ellipse to be drawn.
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setWidth(self.widthOfEllipse)
        # set a mimimum width
        if(self.widthOfEllipse < 1):
            pen.setWidth(1)

        # Set size of ellipse to be drawn.
        size = self.sizeOfEllipse
        # set a mimimum size
        if(size < 2):
            size = 2

        # Create a drawing rectangle for the ellipse.
        drawRec = QtCore.QRectF(event.pos().x(), event.pos().y(), size, size)
        # Translate top left corner of rectangle to match the clicked position.
        drawRec.moveCenter(QtCore.QPointF(event.pos().x(), event.pos().y()))
        # Draw ellipse with specified colour.
        self.scene.addEllipse(drawRec, pen)

        # Update the widget containing the list of points.
        self.nEllipseDrawn += 1
        self.listWidget_points.addItem('Point %s' % self.nEllipseDrawn)
        self.listWidget_points.setCurrentRow(
            self.listWidget_points.count() - 1)

        # The latest drawn item is on the top of the list. Add to point list.
        itemList = self.scene.items()
        self.mapNametoPoint[
            'Point ' + str(self.nEllipseDrawn)] = itemList[0]

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
            current_row = self.listWidget_points.currentRow()
            num_rows = self.listWidget_points.count()
            if current_row == -1 or current_row == num_rows - 1:
                return
            else:
                self.listWidget_points.setCurrentRow(current_row + 1)
        elif event.key() == QtCore.Qt.Key_F:
            current_row = self.listWidget_points.currentRow()
            if current_row == -1 or current_row == 0:
                return
            else:
                self.listWidget_points.setCurrentRow(current_row - 1)

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
        elif event.key() == QtCore.Qt.Key_B: # calculate angle
            pass

        # O for open image
        elif event.key() == QtCore.Qt.Key_O:
            self.openImage()

        # P and L for mode switching
        elif event.key() == QtCore.Qt.Key_P:
            if self.btn_placeMar.isChecked():
                self.btn_placeMar.setChecked(False)
            else:
                self.btn_placeMar.setChecked(True)
            self.btn_drwAngle.setChecked(False)
        elif event.key() == QtCore.Qt.Key_L:
            if self.btn_drwAngle.isChecked():
                self.btn_drwAngle.setChecked(False)
            else:
                self.btn_drwAngle.setChecked(True)
            self.btn_placeMar.setChecked(False)

        # Delete to delete highlighted pointed
        elif event.key() == QtCore.Qt.Key_Delete:
            self.deletePoint(self.listWidget_points.currentItem().text())
            self.listWidget_points.takeItem(
                self.listWidget_points.currentRow())
            return

        # Update point location
        if(self.listWidget_points.currentItem()):
            self.movePoint(
                self.listWidget_points.currentItem().text(), dx, dy)

    def movePoint(self, pointName, dx, dy):
        """The following function moves given point by [dx,dy]"""
        self.mapNametoPoint[pointName].moveBy(dx, dy)

    def deletePoint(self, pointName):
        """The following function deletes given point"""
        itemList = self.scene.items()
        for i in itemList:
            if(i == self.mapNametoPoint[pointName]):
                self.scene.removeItem(i)
        del self.mapNametoPoint[pointName]

    def openImage(self):
        """The following function opens a file dialog and then loads
        user-specified image."""

        # Load image through FileDialog
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            self.centralWidget, "Open File", QtCore.QDir.currentPath())
        if fileName:
            qimage = QtGui.QImage()
            image = qimage.load(fileName[0])
        if not image:
            self.displayMessage("Cannot load {}.".format(fileName))
            return

        # Create a pixmap from the loaded image.
        self.pixmap_item.setPixmap(QtGui.QPixmap.fromImage(qimage))

        # Reset any image transformations.
        self.resetImage()

        # set keyboard focus to the graphics view
        self.view.setFocus()

    def resetImage(self):
        """The following function resets image transformations,
        and clears point list and console output."""

        # Clear image transformations.
        self.view.resetTransform()

        # Clear drawn points.
        itemList = self.scene.items()
        for i in itemList:
            if(i.__class__.__name__ == 'QGraphicsPixmapItem'):
                continue
            self.scene.removeItem(i)

        # Clear console output.
        self.textBrowser_consoleOutput.clear()

        # Reset the number of points.
        self.sizeOfEllipse = 5
        self.widthOfEllipse = 2.5
        self.nEllipseDrawn = 0

        # Clear the list of points.
        self.listWidget_points.clear()

        self.zoomFactor = 1
        self.nUserClickOnPicture = 0
        self.hasTrackMomentumCalc = False
        self.hasDrawndLCurves = False

        # reset count of messages printed to console
        self.num_messages = 0

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
        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        # Scale the drawn points when zooming.
        self.sizeOfEllipse /= factor
        self.widthOfEllipse /= factor
        pen = QtGui.QPen(QtCore.Qt.red)
        pen.setWidth(self.widthOfEllipse)

        # Set a minimum width.
        if(self.widthOfEllipse < 1):
            pen.setWidth(1)

        # Set size of ellipse to be drawn.
        size = self.sizeOfEllipse

        # Set a minimum size.
        if(size < 2):
            size = 2

        # Recale the points.
        for key, value in self.mapNametoPoint.items():
            drawRec = QtCore.QRectF(
                value.rect().x(), value.rect().y(), size, size)
            drawRec.moveCenter(
                QtCore.QPointF(value.rect().center().x(), value.rect().center().y()))
            value.setRect(drawRec)
            value.setPen(pen)

        self.scene.update()

    def adjustScrollBar(self, scrollBar, factor):
        """The following helper function adjusts size of scrollbar."""
        scrollBar.setValue(
            int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep() / 2)))

    def displayMessage(self, msg):
        """The following function is used to write messages to console."""

        self.num_messages += 1
        msg = "[{}] {}".format(self.num_messages, msg)
        self.textBrowser_consoleOutput.append(msg)

    def calcTrackMom(self):
        """The following function is used to calculate track momentum of
        drawn points on image and then draw a fitted circle to them."""

        # Need a minimum of 3 points to fit a circle.
        if len(self.mapNametoPoint) < 3:
            self.displayMessage("ERROR - Less than 3 points to fit.")
            return

        # Return if track momentum has already been calculated.
        if self.hasTrackMomentumCalc:
            return

        pointList = []
        for key, value in self.mapNametoPoint.items():
            pointList.append(value)
            #print('x: ', value.rect().center().x(),
            #      ' y: ', value.rect().center().y())

        # Hardcoded circle for now. TODO: FIT CIRCLE HERE.
        fitted_circle = circleFit(pointList)
        self.fittedX0 = fitted_circle[0][0]
        self.fittedY0 = fitted_circle[1][0]
        self.fittedR0 = fitted_circle[2][0]

        # Set colour of circle to be drawn.
        pen = QtGui.QPen(QtCore.Qt.green)
        # Create a drawing rectangle for the circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * self.fittedR0, 2 * self.fittedR0)
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        # Draw circle with specified colour.
        self.scene.addEllipse(drawRec, pen)

        # Store the drawn circle for future modifications.
        itemList = self.scene.items()
        # The latest drawn item is on the top of the list.
        self.nominalFittedCenter = itemList[0]

        self.drawdlCurves()
        self.hasTrackMomentumCalc = True

    def drawdlCurves(self):
        """The following helper function draws the dL curves."""
        # Draw dL curves if dL is specified.
        try:
            self.dL = float(self.setDlLineEdit.text())
        except ValueError:
            self.displayMessage("ERROR - dL is not a float")
            return

        pen = QtGui.QPen(QtCore.Qt.green)
        # Define outer circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * (self.fittedR0 + self.dL), 2 * (self.fittedR0 + self.dL))
        # Draw a dotted line.
        pen.setStyle(QtCore.Qt.DashDotLine)
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.scene.addEllipse(drawRec, pen)

        # Store the drawn circle for future modifications.
        itemList = self.scene.items()
        # The latest drawn item is on the top of the list.
        self.outerFittedCenter = itemList[0]

        # Deine inner circle.
        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0,  2 * (self.fittedR0 - self.dL), 2 * (self.fittedR0 - self.dL))
        # Draw a dotted line.
        pen.setStyle(QtCore.Qt.DashDotLine)
        # Translate top left corner of rectangle to match the center of circle.
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.scene.addEllipse(drawRec, pen)

        # Store the drawn circle for future modifications.
        itemList = self.scene.items()
        # The latest drawn item is on the top of the list.
        self.innerFittedCenter = itemList[0]

        # Used for debugging purposes.
        self.hasDrawndLCurves = True

    def calcOptDen(self):
        """The following function is used to calculate optical density of
        drawn points on image with a specified dL."""

        # Need a minimum of 3 points to fit a circle.
        if len(self.mapNametoPoint) < 3:
            self.displayMessage("ERROR - Less than 3 points to fit.")
            return

        pointList = []
        for key, value in self.mapNametoPoint.items():
            pointList.append(value)

        # Hardcoded circle for now. TODO: FIT CIRCLE HERE.
        self.tmp_circle = [50, 50, 50]

        # Draw dL curves if dL is specified.
        try:
            self.dL = float(self.setDlLineEdit.text())
        except ValueError:
            self.displayMessage("ERROR - dL is not a float")
            return

        # Call function to compute optical density.
        self.optDens, self.errOptDens = calcOptDensity(
            self, self.pixmap_item, pointList, self.tmp_circle, self.dL)
        # Used for debugging.
        self.displayMessage(str("%f %f" % (self.optDens, self.errOptDens)))

    def changedLCircles(self, value):
        """The following helper function changes the diameter of dL curves."""

        # Return if track momentum has already been calculated.
        if not self.hasTrackMomentumCalc:
            return

        # If original dL curves have not been drawn, create them.
        if not self.hasDrawndLCurves:
            self.drawdlCurves()

        try:
            self.dL = float(value)
        except ValueError:
            self.displayMessage("ERROR - dL is not a float")
            return

        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0,  2 * (self.fittedR0 + self.dL), 2 * (self.fittedR0 + self.dL))
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))
        self.outerFittedCenter.setRect(drawRec)

        drawRec = QtCore.QRectF(
            self.fittedX0, self.fittedY0, 2 * (self.fittedR0 - self.dL), 2 * (self.fittedR0 - self.dL))
        drawRec.moveCenter(QtCore.QPointF(self.fittedX0, self.fittedY0))

        self.innerFittedCenter.setRect(drawRec)

        self.scene.update()

    def resizeEvent(self,event):
        self.scrollArea.setMinimumSize(
            QtCore.QSize(0, self.centralWidget.size().height() / 1.75))
