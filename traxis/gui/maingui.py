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

import json
import math
from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants
from traxis.gui import skeleton
from traxis.calc import anglecalc, circlefit, optdensity
from traxis.graphics import tangent


class MainWidget(skeleton.GuiSkeleton):

    """Class that extends the base skeleton widget class, implementing
    logic that connects button clicks and other widget events to their
    handlers. Defines the GUI's event handler methods.
    """

    def __init__(self):
        """Initialize the GUI skeleton, set default state variables and connect
        buttons and events to methods.
        """

        # initialize the skeleton of the GUI
        super().__init__()

        # set default GUI state variables
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
        self.resetButton.clicked.connect(self.reset)
        self.calcMomentumButton.clicked.connect(self.calcTrackMomentum)
        self.calcDensityButton.clicked.connect(self.calcOptDensity)
        self.calcAngleButton.clicked.connect(self.calcAngle)
        self.placeMarkerButton.clicked.connect(self.placeMarkerButtonFunc)
        self.drawRefButton.clicked.connect(self.drawRefButtonFunc)

        # connect the scene pixmap's mouse events
        self.scenePixmap.mousePressEvent = self.pixmapMousePress
        self.scenePixmap.mouseReleaseEvent = self.pixmapMouseRelease
        self.scenePixmap.mouseMoveEvent = self.pixmapMouseMove

        # connect other events
        self.dlLineEdit.textEdited.connect(self.dLEdited)
        self.markerList.itemSelectionChanged.connect(self.highlightPoint)

    ##############################
    # Keypress Event Handler
    ##############################
    def keyPressEvent(self, event):
        """Handle the key presses that are not hooked up to buttons."""

        # get the currently selected track marker
        currentPoint = self.markerList.currentItem()
        # initialize the point movement variables
        dx, dy = 0, 0

        # check if the Shift key was held
        if event.modifiers() & QtCore.Qt.ShiftModifier:
            isShift = True
        else:
            isShift = False

        # WASD to set the direction of the movement of the selected point
        if event.key() == QtCore.Qt.Key_W:
            dy = -1 # up (y increases going down)

        elif event.key() == QtCore.Qt.Key_S:
            dy = 1 # down (y increases going down)

        elif event.key() == QtCore.Qt.Key_D:
            dx = 1 # right

        elif event.key() == QtCore.Qt.Key_A:
            dx = -1 # left

        # if one of WASD was pressed, move the currently selected point
        if dx or dy:
            # if shift was held, do a course movement (half the point size, if
            # the point size is more than 2 px), otherwise move the point by
            # 1 px
            if isShift and self.pointSize >= 2:
                dx *= self.pointSize / 2
                dy *= self.pointSize / 2
            if currentPoint:
                currentPoint.move(dx, dy)
        
        # F/V to select the next or previous marker in the marker list
        elif event.key() == QtCore.Qt.Key_V:
            self.markerList.selectNext()

        elif event.key() == QtCore.Qt.Key_F:
            self.markerList.selectPrevious()

        # G/H to set the currently selected point as the start or end point
        elif event.key() == QtCore.Qt.Key_G:
            if currentPoint:
                self.markerList.setStartPoint(currentPoint)

        elif event.key() == QtCore.Qt.Key_H:
            if currentPoint:
                self.markerList.setEndPoint(currentPoint)

        # Delete key to delete the currently selected point
        elif event.key() == QtCore.Qt.Key_Delete:
            if currentPoint:
                self.markerList.deleteMarker(currentPoint)

    #############################
    # Pixmap Mouse Event Handlers
    #############################
    def pixmapMousePress(self, event):
        """Respond differently to mouse presses on the image depending on the
        currently selected mode. If in track marker placment mode, place a
        marker, if in angle reference drawing mode, reset the reference line
        and set the initial point for a new line, if in neither mode,
        initialize an image pan. event is a QGraphicsSceneMouseEvent object
        containing the coordinates of the mouse press.
        """

        # if the track marker placement mode is selected, add a new marker at
        # the location of the mouse press
        if self.placeMarkerButton.isChecked():
            self.markerList.addMarker(
                event.pos().x(), event.pos().y(), 
                self.pointSize, self.lineWidth, self.scene)

        # if angle reference drawing mode is selected, set the initial point
        # of the reference line at the location of the mouse press
        elif self.drawRefButton.isChecked():
            self.angleRefLine.setInitialPoint(
                event.pos().x(), event.pos().y(),
                self.pointSize, self.lineWidth, self.scene)

        # if neither mode is selected, set the initial reference position for
        # an image pan (store the position of this mouse press)
        # note: the event position is in image/scene coordinates but the pan
        # is to be done using graphics view coordinates so apply the
        # coordinate mapping
        else:
            self.sceneView.lastMousePos = self.sceneView.mapFromScene(
                                              event.pos())

    def pixmapMouseRelease(self, event):
        """Set the final point of the angle reference line if it is in the
        process of being drawn. event is a QGraphicsSceneMouseEvent object
        containing the coordinates of the mouse release.
        """

        # if the reference line is being drawn, set the final point of the
        # reference line at the location of the mouse release 
        if self.angleRefLine.isBeingDrawn():
            self.angleRefLine.setFinalPoint(
                event.pos().x(), event.pos().y(),
                self.pointSize, self.lineWidth, self.scene)

    def pixmapMouseMove(self, event):
        """Redraw the line of the angle reference if it is in the process of
        being drawn so that its end point follows the mouse cursor. If neither
        mode is selected, pan the image. event is a QGraphicsSceneMouseEvent
        object containing the coordinates of the mouse position.
        """

        # if the reference line is being drawn, redraw its line attribute so
        # that its end matches the current mouse location
        if self.angleRefLine.isBeingDrawn():
            self.angleRefLine.drawLine(
                event.pos().x(), event.pos().y(), self.lineWidth, self.scene)

        # if neither mode is currently selected, translate the image so that
        # the pixel under the mouse cursor follows the mouse (i.e. pan the
        # image)
        if not (self.placeMarkerButton.isChecked()
                or self.drawRefButton.isChecked()):
            # get the graphics view's scroll bar objects
            hbar = self.sceneView.horizontalScrollBar()
            vbar = self.sceneView.verticalScrollBar()
            # determine the difference between the current mouse event postion
            # and the previous mouse event position (in graphics view
            # coordinates)
            delta = self.sceneView.mapFromScene(
                        event.pos()) - self.sceneView.lastMousePos
            # store the position of this mouse event
            self.sceneView.lastMousePos = self.sceneView.mapFromScene(
                                              event.pos())
            # shift the scroll bars by the difference in mouse event positions
            hbar.setValue(hbar.value() - delta.x())
            vbar.setValue(vbar.value() - delta.y())

    ##############################
    # File Dialog Event Handlers
    ##############################
    def openImage(self, fileName=None):
        """If fileName, a string containing the complete location of an image
        is passed, open that image. Otherwise have the user select the image
        to open via file dialog.
        """

        # if no file name was given, open file dialog to obtain image file name
        if not fileName:
            fileName = QtWidgets.QFileDialog.getOpenFileName(
                None, "Open File", QtCore.QDir.currentPath(),
                "Images (*.png *.jpg);;All Files (*)")[0]

        # load the image into sceneImage
        if not fileName:
            return False # image not loaded successfully
        else:
            image = self.sceneImage.load(fileName)
        if not image:
            self.displayMessage(
                "NOTICE: Cannot open file as image: {}.".format(fileName))
            return False # image not loaded successfully

        # store the image file name
        self.imageFileName = fileName

        # resize the graphics scene to the loaded image dimensions
        self.scene.setSceneRect(
            0, 0, self.sceneImage.width(), self.sceneImage.height())

        # create a pixmap from the loaded image
        self.scenePixmap.setPixmap(QtGui.QPixmap.fromImage(self.sceneImage))

        # set keyboard focus to the graphics view
        self.sceneView.setFocus()

        # reset the application
        self.reset()

        # an image was successfully opened
        return True

    def saveSession(self):
        """Save analysis session to a .json file selected by the user via file
        dialog.
        """

        # if no image has been opened, return
        if self.scenePixmap.pixmap().isNull():
            self.displayMessage("NOTICE: Nothing to save.")
            return

        # open file dialog for selecting a file to save to
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save Session", "./untitled.json",
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        # return if no file was selected
        if not fileName:
            return

        else:
            # initialize a dictionary for the data we want to save
            saveData = {}
            
            # store the image's file location
            saveData['imageFileName'] = self.imageFileName

            # if there are any markers in the marker list, store their data
            if self.markerList.count() > 0:
                # store the marker data in a list to preserve order
                points = []
                for row in range(self.markerList.count()):
                    point = self.markerList.item(row)
                    pointDict = {}
                    # save the marker designation and the coordinates
                    pointDict['designation'] = point.designation
                    pointDict['x'] = point.ellipse.rect().center().x()
                    pointDict['y'] = point.ellipse.rect().center().y()
                    points.append(pointDict)
                saveData["points"] = points

            # store the dL if it is not empty or 0
            if self.dlLineEdit.text() not in ["0", ""]:
                saveData['dl'] = self.dlLineEdit.text()

            # store the coordinates of the initial and final points of the
            # reference line
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
        """Load an analysis session from a .json file selected by the user via
        file dialog.
        """

        # open file dialog for selecting a file to load from
        fileName = QtWidgets.QFileDialog.getOpenFileName(
            None, "Load Session", QtCore.QDir.currentPath(),
            "HEP Track Analysis (*.json);;All Files (*)")[0]

        # return if no file was selected
        if not fileName:
            return

        else:
            # open the file contents
            with open(fileName, 'r') as loadFile:
                # try to load the file contents as a JSON formatted object
                try:
                    loadData = json.load(loadFile)
                except:
                    self.displayMessage("NOTICE: Invalid JSON file: {}".format(
                                                                     fileName))
                    return

                # get the image filename from the saved session data
                imageFileName = loadData.get('imageFileName')

                # if the image filename is missing, return
                if not imageFileName:
                    self.displayMessage("NOTICE: No image file name found in saved session data: {}".format(fileName))
                    return

                # try to open the image. If it fails to open, return
                opened = self.openImage(imageFileName)
                if not opened:
                    return

                # get the track marker data from the saved session
                points = loadData.get('points')
                if points:
                    # add each track marker to the marker list
                    for point in points:
                        pointDesignation = point["designation"]
                        x = point['x']
                        y = point['y']
                        addedMarker = self.markerList.addMarker(
                                          x, y, self.pointSize,
                                          self.lineWidth, self.scene)
                        # set the appropriate designation for each marker
                        addedMarker.setDesignation(pointDesignation)

                # get the dl data from the saved session
                dl = loadData.get('dl')
                # if it is a float, set it to the dl text box value
                try:
                    float(dl)
                    self.dlLineEdit.setText(dl)
                except ValueError:
                    pass

                # get the data for the initial and final points for the
                # reference line
                refInitialPoint = loadData.get('refInitialPoint')
                refFinalPoint = loadData.get('refFinalPoint')
                if refInitialPoint and refFinalPoint:
                    # set the initial point, line and final point of the
                    # reference line
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
        """Save the currently visible part of the graphics scene to an
        image.
        """

        # if no image has been opened, return
        if self.scenePixmap.pixmap().isNull():
            self.displayMessage(
                "NOTICE: There is nothing to take screenshot of.")
            return

        # grab the currently visible portion of the graphics scene and put it
        # in a pixmap
        screenshot = self.sceneView.grab()

        # open a file dialog for selecting a file to save to
        fileName = QtWidgets.QFileDialog.getSaveFileName(
            None, "Save Screenshot", "./untitled.png",
            "PNG (*.png);;JPEG (*.jpg);;TIFF (*.tiff *.tif)")[0]

        # return if no file was selected
        if not fileName:
            return

        # try to save the pixmap to the selected file
        if not screenshot.save(fileName):
            self.displayMessage("NOTICE: Unable to save screenshot.")

    ##############################
    # Zoom Events Handlers
    ##############################
    def zoomIn(self):
        """Scale the image by ZOOMINFACTOR."""

        self.scaleImage(constants.ZOOMINFACTOR)

    def zoomOut(self):
        """Scale the image by ZOOMOUTFACTOR."""

        self.scaleImage(constants.ZOOMOUTFACTOR)

    def scaleImage(self, factor):
        """Scale the graphics view and all graphics items drawn on it by
        factor.
        """

        # update the current zoom level
        self.zoomFactor = self.zoomFactor * factor
        
        # scale the graphics view
        self.sceneView.scale(factor, factor)

        # scale the point size and line width state variables
        self.pointSize /= factor
        self.lineWidth /= factor

        # scale all graphics items drawn on the graphics scene
        # using the updated point size and line width
        self.markerList.rescale(self.pointSize, self.lineWidth)
        self.momentumArc.rescale(self.lineWidth)
        self.angleRefLine.rescale(self.pointSize, self.lineWidth)
        if self.tangentLine:
            self.tangentLine.rescale(self.lineWidth)

    ###################################
    # Calculation Button Event Handlers
    ###################################
    def calcTrackMomentum(self):
        """Fit a circle to the track markers in markerList and print the 
        parameters of the fit along with the momentum computed from these
        parameters to the console. Draw the momentum arc using the fit
        parameters. Print the length of the momentum arc to the console.
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

        # calculate the length of the momentum arc in px
        # note: ArcItems have start and span angles in units of millionths of a
        # degree, so divide them by 1e6
        trackLengthPx = self.fittedCircle['radius'] * \
                 self.momentumArc.centralArc.spanAngle() / 1e6 * (math.pi / 180)

        # convert track length from px to cm
        trackLengthCm = trackLengthPx * constants.CMPERPX
        trackLengthCmErr = trackLengthPx * constants.ERRCMPERPX

        # print the track length to the console
        self.displayMessage("---Track Length---")
        self.displayMessage(
            "Track Length (px):\t{:.5f} [px]".format(trackLengthPx))
        self.displayMessage(
            "Track Length (cm):\t{:.5f} +/- {:.5f} [cm]".format(
                trackLengthCm, trackLengthCmErr))

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
    # Mode Change Event Handlers
    ##############################
    def placeMarkerButtonFunc(self):
        """Ensure that the angle reference drawing mode is not selected at the
        same time as the track marker placement mode.
        """

        self.drawRefButton.setChecked(False)

    def drawRefButtonFunc(self):
        """Ensure that the track marker placement mode is not selected at the
        same time as the angle reference drawing mode.
        """

        self.placeMarkerButton.setChecked(False)

    ##############################
    # Other Event Handlers
    ##############################
    def dLEdited(self, newDL):
        """Update the outer and inner arcs of the momentum arc to reflect
        newDL, the new value in the dL text box.
        """

        # if the dL text box is empty (and so newDL is an empty string),
        # return
        if not newDL:
            return

        # otherwise convert newDL to a float and update the arcs
        dl = float(newDL)
        self.momentumArc.updateArcs(dl)

    def highlightPoint(self):
        """Highlight the track marker that is currently selected."""

        self.markerList.highlightCurrent()

    ##############################
    # Reset Event Handler
    ##############################
    def reset(self):
        """Remove all graphics items drawn on the graphics scene, clear all
        messages from the console, reset image zoom and reset dL.
        """

        # remove all points, arcs and lines from the graphics scene
        self.markerList.empty()
        self.angleRefLine.reset()
        self.momentumArc.reset()
        if self.tangentLine:
            self.tangentLine.scene().removeItem(self.tangentLine)
            self.tangentLine = None

        # clear the console
        self.consoleTextBrowser.clear()

        # reset the dL to 0
        self.dlLineEdit.setText("0")

        # reset any image zoom
        self.scaleImage(1 / self.zoomFactor)

        # scale the image so that it fills as much of the graphics view as it
        # can without requiring scroll bars
        if not self.sceneImage.isNull():
            # determine how many times smaller (or larger) the graphics view
            # height is than the image height. Same for the widths.
            # note: the graphics view object has 2 extra pixels of height and
            # width that the image does not occupy
            heightRatio = (self.sceneView.height()-2) / \
                           self.sceneImage.height()
            widthRatio = (self.sceneView.width()-2) / \
                          self.sceneImage.width()

            if heightRatio < widthRatio:
                scaleFactor = heightRatio
            else:
                scaleFactor = widthRatio

            self.scaleImage(scaleFactor)

    ##############################
    # Helper Methods
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
