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

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from traxis.graphics import markers, angleref, fittedarc


class GuiSkeleton(QtWidgets.QWidget):

    """The topmost widget which places all the GUI's widgets onto itself upon
    initialization.
    """

    def __init__(self):
        """Setup the base user interface - create layouts and place widgets
        and labels.
        """

        super().__init__()

        # main layout of the skeleton
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # layout for the top portion of the user interface
        self.topWidget = QtWidgets.QWidget()
        self.mainLayout.addWidget(self.topWidget)
        # the top portion should have a fixed height, just big enough to fit
        # all of its contents
        self.topWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.topUiLayout = QtWidgets.QHBoxLayout(self.topWidget)
        # don't add any extra padding around the edges of this layout's widgets
        self.topUiLayout.setContentsMargins(0, 0, 0, 0)

        # track marker list GUI segment
        self.markerListLayout = QtWidgets.QVBoxLayout()  # marker list layout
        self.topUiLayout.addLayout(self.markerListLayout)

        self.markerListLabel = QtWidgets.QLabel(self)  # marker list label
        self.markerListLayout.addWidget(self.markerListLabel)
        self.markerListLabel.setText("Track Markers")

        self.markerList = markers.MarkerList(self)  # marker list widget
        self.markerListLayout.addWidget(self.markerList)
        # don't focus on this widget when clicked
        self.markerList.setFocusPolicy(QtCore.Qt.NoFocus)
        self.markerList.setFixedWidth(100)

        # first vertical GUI segment divider in top portion layout
        self.vLineDiv1 = QtWidgets.QFrame(self)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv1)
        self.vLineDiv1.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv1.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "technical button" GUI segment
        # technical button segment layout
        self.techButtonLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.techButtonLayout)

        self.resetButtonLabel = QtWidgets.QLabel(self)  # reset button label
        self.techButtonLayout.addWidget(self.resetButtonLabel)
        self.resetButtonLabel.setText("Reset Analysis")

        self.resetButton = QtWidgets.QPushButton(self)  # reset button widget
        self.techButtonLayout.addWidget(self.resetButton)
        # don't focus on this widget when clicked
        self.resetButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.resetButton.setText("Reset")
        self.resetButton.setToolTip(
            "Reset all the selected points and calculated variables")
        self.resetButton.setShortcut(QtGui.QKeySequence("R"))

        self.zoomLabel = QtWidgets.QLabel(self)  # zoom label
        self.techButtonLayout.addWidget(self.zoomLabel)
        self.zoomLabel.setText("Zoom")

        # horizontal layout for zoom buttons
        self.zoomLayout = QtWidgets.QHBoxLayout()
        self.techButtonLayout.addLayout(self.zoomLayout)

        # zoom in button widget
        self.zoomInButton = QtWidgets.QPushButton(self)
        self.zoomLayout.addWidget(self.zoomInButton)
        # don't focus on this widget when clicked
        self.zoomInButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.zoomInButton.setText("Zoom In")
        self.zoomInButton.setToolTip("Zoom into the picture")
        self.zoomInButton.setShortcut(QtGui.QKeySequence("Z"))

        # zoom out button widget
        self.zoomOutButton = QtWidgets.QPushButton(self)
        self.zoomLayout.addWidget(self.zoomOutButton)
        self.zoomOutButton.setFocusPolicy(QtCore.Qt.NoFocus)
        # don't focus on this widget when clicked
        self.zoomOutButton.setText("Zoom Out")
        self.zoomOutButton.setToolTip("Zoom out from the picture")
        self.zoomOutButton.setShortcut(QtGui.QKeySequence("X"))

        self.calcLabel = QtWidgets.QLabel(self)  # calculate label
        self.techButtonLayout.addWidget(self.calcLabel)
        self.calcLabel.setText("Calculate")

        # calculate momentum button widget
        self.calcMomentumButton = QtWidgets.QPushButton(self)
        self.techButtonLayout.addWidget(self.calcMomentumButton)
        # don't focus on this widget when clicked
        self.calcMomentumButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcMomentumButton.setText("Calculate Track Momentum")
        self.calcMomentumButton.setToolTip("Calculate Track momentum")
        self.calcMomentumButton.setShortcut(QtGui.QKeySequence("M"))

        # calculate optical density button widget
        self.calcDensityButton = QtWidgets.QPushButton(self)
        self.techButtonLayout.addWidget(self.calcDensityButton)
        # don't focus on this widget when clicked
        self.calcDensityButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcDensityButton.setText("Calculate Optical Density")
        self.calcDensityButton.setToolTip("Calculate Optical Density")
        self.calcDensityButton.setShortcut(QtGui.QKeySequence("N"))

        # calculate angle button widget
        self.calcAngleButton = QtWidgets.QPushButton(self)
        self.techButtonLayout.addWidget(self.calcAngleButton)
        # don't focus on this widget when clicked
        self.calcAngleButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcAngleButton.setText("Calculate Angle")
        self.calcAngleButton.setToolTip("Calculate Opening Angle")
        self.calcAngleButton.setShortcut(QtGui.QKeySequence("B"))

        # add stretch to segment to keep widgets together
        self.techButtonLayout.addStretch(0)

        # second vertical GUI segment divider in top portion layout
        self.vLineDiv2 = QtWidgets.QFrame(self)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv2)
        self.vLineDiv2.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv2.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "user selection" GUI segment
        # user seletion segment layout
        self.userSelectionLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.userSelectionLayout)

        self.openSaveLabel = QtWidgets.QLabel(self)  # open/save label
        self.userSelectionLayout.addWidget(self.openSaveLabel)
        self.openSaveLabel.setText("Open/Save")

        self.openImageButton = QtWidgets.QPushButton(
            self)  # open image button widget
        self.userSelectionLayout.addWidget(self.openImageButton)
        # don't focus on this widget when clicked
        self.openImageButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.openImageButton.setText("Open Image")
        self.openImageButton.setToolTip("Open image for analysis")
        self.openImageButton.setShortcut(QtGui.QKeySequence("O"))

        # horizontal layout for save and load buttons
        self.saveLayout = QtWidgets.QHBoxLayout()
        self.userSelectionLayout.addLayout(self.saveLayout)

        # save session button widget
        self.saveSessionButton = QtWidgets.QPushButton(self)
        self.saveLayout.addWidget(self.saveSessionButton)
        # don't focus on this widget when clicked
        self.saveSessionButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.saveSessionButton.setText("Save")
        self.saveSessionButton.setToolTip("Save current analysis session")
        
        # load session button widget
        self.loadSessionButton = QtWidgets.QPushButton(self)
        self.saveLayout.addWidget(self.loadSessionButton)
        # don't focus on this widget when clicked
        self.loadSessionButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.loadSessionButton.setText("Load")
        self.loadSessionButton.setToolTip(
            "Load a previously saved analysis session")

        # screenshot button widget
        self.screenshotButton = QtWidgets.QPushButton(self)
        self.userSelectionLayout.addWidget(self.screenshotButton)
        # don't focus on this widget when clicked
        self.screenshotButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.screenshotButton.setText("Save Screenshot")
        self.screenshotButton.setToolTip(
            "Take a screenshot of the scroll area contents and save to image")

        self.modeLabel = QtWidgets.QLabel(self) # mode label
        self.userSelectionLayout.addWidget(self.modeLabel)
        self.modeLabel.setText("Mode")

        # place marker mode button widget
        self.placeMarkerButton = QtWidgets.QPushButton(self)
        self.userSelectionLayout.addWidget(self.placeMarkerButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.placeMarkerButton.setCheckable(True)
        # don't focus on this widget when clicked
        self.placeMarkerButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.placeMarkerButton.setText("[Mode] Place Track Markers")
        self.placeMarkerButton.setToolTip(
            "Enter mode for placing markers on loaded image.")
        self.placeMarkerButton.setShortcut("P")

        # draw angle reference mode button widget
        self.drawRefButton = QtWidgets.QPushButton(self)
        self.userSelectionLayout.addWidget(self.drawRefButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.drawRefButton.setCheckable(True)
        # don't focus on this widget when clicked
        self.drawRefButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.drawRefButton.setText("[Mode] Draw Angle Reference")
        self.drawRefButton.setToolTip(
            "Enter mode for drawing angle reference on loaded image.")
        self.drawRefButton.setShortcut("L")

        # dl form layout
        self.dlFormLayout = QtWidgets.QFormLayout()
        self.userSelectionLayout.addLayout(self.dlFormLayout)

        # dl label
        self.dlLabel = QtWidgets.QLabel(self)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.dlLabel)
        self.dlLabel.setText("Set dL")

        # dl text box (line edit) widget
        self.dlLineEdit = QtWidgets.QLineEdit(self)
        # fix the size of the text box
        self.dlLineEdit.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.dlLineEdit)
        # set the dL value to 0 by default
        self.dlLineEdit.setText("0")
        # validate the contents of the text box so that only floats can
        # be entered
        self.dlLineEdit.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp('[0-9]+\.?[0-9]*')))

        # add stretch to segment to keep widgets together
        self.userSelectionLayout.addStretch(0)

        # third vertical GUI segment divider in top portion layout
        self.vLineDiv3 = QtWidgets.QFrame(self)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv3)
        self.vLineDiv3.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv3.setFrameShadow(QtWidgets.QFrame.Sunken)

        # console GUI segment
        self.consoleLayout = QtWidgets.QVBoxLayout()  # console segment layout
        self.topUiLayout.addLayout(self.consoleLayout)

        self.consoleLabel = QtWidgets.QLabel(self)  # console label
        self.consoleLayout.addWidget(self.consoleLabel)
        self.consoleLabel.setText("Console")

        # console text browser widget
        self.consoleTextBrowser = QtWidgets.QTextBrowser(self)
        self.consoleLayout.addWidget(self.consoleTextBrowser)
        self.consoleTextBrowser.setMinimumWidth(100)

        # determine the height of the "user selection" GUI segment (the
        # tallest segment in the top portion of the GUI)
        userSelectionHeight = \
            self.userSelectionLayout.minimumSize().height() - \
            self.openSaveLabel.height()
        # fix the height of the marker list and console to the "user selection"
        # GUI segment height
        self.markerList.setFixedHeight(userSelectionHeight)
        self.consoleTextBrowser.setFixedHeight(userSelectionHeight)

        # horizontal GUI segment divider between top portion and bottom
        # portion of the GUI
        self.hLineDiv = QtWidgets.QFrame(self)
        self.mainLayout.addWidget(self.hLineDiv)
        self.hLineDiv.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLineDiv.setFrameShadow(QtWidgets.QFrame.Sunken)

        # layout for the bottom portion of the user interface
        self.bottomUiLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.bottomUiLayout)

        # create a graphics scene on which images and all graphics will be
        # displayed
        self.scene = QtWidgets.QGraphicsScene()
        # the graphics view is the widget that actually displays the contents
        # of the graphics scene
        self.sceneView = QtWidgets.QGraphicsView(self.scene, self)
        self.bottomUiLayout.addWidget(self.sceneView)
        # set a minimum size for the scene view
        self.sceneView.setMinimumWidth(900)
        self.sceneView.setMinimumHeight(400)

        # instantiate QImage and PixmapItem
        self.sceneImage = QtGui.QImage()
        self.scenePixmap = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.scenePixmap)

        # instantiate reference line and momentum arc objects
        self.angleRefLine = angleref.ReferenceLine()
        self.momentumArc = fittedarc.MomentumArc()
 
        # set the tangentLine attribute to None initially so that there is
        # something to check for when a tangent has not been drawn yet
        self.tangentLine = None
