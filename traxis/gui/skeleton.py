import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from traxis.graphics import markers, angleref, fittedarc


class GuiSkeleton(object):

    """The skeleton of the GUI."""

    def __init__(self):
        """Setup the base user interface - create layouts and place widgets
        and labels on main window.
        """

        # instantiate a base widget
        self.baseWidget = QtWidgets.QWidget()

        # layout of the main window
        self.mainLayout = QtWidgets.QVBoxLayout(self.baseWidget)

        # layout for the top half of the user interface
        self.topWidget = QtWidgets.QWidget()
        self.mainLayout.addWidget(self.topWidget)
        self.topWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.topUiLayout = QtWidgets.QHBoxLayout(self.topWidget)
        self.topUiLayout.setContentsMargins(0, 0, 0, 0)

        # track marker list gui segment
        self.pointListLayout = QtWidgets.QVBoxLayout()  # marker segment layout
        self.topUiLayout.addLayout(self.pointListLayout)

        self.pointListLabel = QtWidgets.QLabel(
            self.baseWidget)  # marker list label
        self.pointListLayout.addWidget(self.pointListLabel)
        self.pointListLabel.setText("Track Markers")

        self.pointListWidget = markers.MarkerList(
            self.baseWidget)  # marker list widget
        self.pointListLayout.addWidget(self.pointListWidget)
        # don't focus on this widget when clicked
        self.pointListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pointListWidget.setFixedWidth(100)

        # first vertical gui segment divider in top half layout
        self.vLineDiv1 = QtWidgets.QFrame(
            self.baseWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv1)
        self.vLineDiv1.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv1.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "technical button" gui segment
        # technical button segment layout
        self.techButtonLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.techButtonLayout)

        self.resetButtonLabel = QtWidgets.QLabel(
            self.baseWidget)  # reset button label
        self.techButtonLayout.addWidget(self.resetButtonLabel)
        self.resetButtonLabel.setText("Reset Analysis")

        self.resetButton = QtWidgets.QPushButton(
            self.baseWidget)  # reset button widget
        self.techButtonLayout.addWidget(self.resetButton)
        self.resetButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.resetButton.setText("Reset")
        self.resetButton.setToolTip(
            "Reset all the selected points and calculated variables")

        self.zoomLabel = QtWidgets.QLabel(self.baseWidget)  # zoom label
        self.techButtonLayout.addWidget(self.zoomLabel)
        self.zoomLabel.setText("Zoom")

        # horizontal layout for zoom buttons
        self.zoomLayout = QtWidgets.QHBoxLayout()
        self.techButtonLayout.addLayout(self.zoomLayout)

        self.zoomInButton = QtWidgets.QPushButton(
            self.baseWidget)  # zoom in button widget
        self.zoomLayout.addWidget(self.zoomInButton)
        self.zoomInButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.zoomInButton.setText("Zoom In")
        self.zoomInButton.setToolTip("Zoom into the picture")

        self.zoomOutButton = QtWidgets.QPushButton(
            self.baseWidget)  # zoom out button widget
        self.zoomLayout.addWidget(self.zoomOutButton)
        self.zoomOutButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.zoomOutButton.setText("Zoom Out")
        self.zoomOutButton.setToolTip("Zoom out from the picture")

        self.calcLabel = QtWidgets.QLabel(
            self.baseWidget)  # calculate label
        self.techButtonLayout.addWidget(self.calcLabel)
        self.calcLabel.setText("Calculate")

        self.calcMomentumButton = QtWidgets.QPushButton(
            self.baseWidget)  # calculate momentum button widget
        self.techButtonLayout.addWidget(self.calcMomentumButton)
        self.calcMomentumButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcMomentumButton.setText("Calculate Track Momentum")
        self.calcMomentumButton.setToolTip("Calculate Track momentum")

        # calculate optical density button widget
        self.calcDensityButton = QtWidgets.QPushButton(self.baseWidget)
        self.techButtonLayout.addWidget(self.calcDensityButton)
        self.calcDensityButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcDensityButton.setText("Calculate Optical Density")
        self.calcDensityButton.setToolTip("Calculate Optical Density")

        self.calcAngleButton = QtWidgets.QPushButton(
            self.baseWidget)  # calculate angle button widget
        self.techButtonLayout.addWidget(self.calcAngleButton)
        self.calcAngleButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.calcAngleButton.setText("Calculate Angle")
        self.calcAngleButton.setToolTip("Calculate Opening Angle")

        self.techButtonLayout.addStretch(0)  # add stretch to segment

        # second vertical gui segment divider in top half layout
        self.vLineDiv2 = QtWidgets.QFrame(
            self.baseWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv2)
        self.vLineDiv2.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv2.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "user selection" gui segment
        # user seletion segment layout
        self.userSelectionLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.userSelectionLayout)

        self.openSaveLabel = QtWidgets.QLabel(
            self.baseWidget)  # open/save label
        self.userSelectionLayout.addWidget(self.openSaveLabel)
        self.openSaveLabel.setText("Open/Save")

        self.openImageButton = QtWidgets.QPushButton(
            self.baseWidget)  # open image button widget
        self.userSelectionLayout.addWidget(self.openImageButton)
        self.openImageButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.openImageButton.setText("Open Image")
        self.openImageButton.setToolTip("Open image for analysis")

        self.saveLayout = QtWidgets.QHBoxLayout()
        self.userSelectionLayout.addLayout(self.saveLayout)

        self.saveSessionButton = QtWidgets.QPushButton(
            self.baseWidget) # save session button widget
        self.saveLayout.addWidget(self.saveSessionButton)
        self.saveSessionButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.saveSessionButton.setText("Save")
        self.saveSessionButton.setToolTip("Save current analysis session")
        
        self.loadSessionButton = QtWidgets.QPushButton(
            self.baseWidget) # load session button widget
        self.saveLayout.addWidget(self.loadSessionButton)
        self.loadSessionButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.loadSessionButton.setText("Load")
        self.loadSessionButton.setToolTip(
            "Load a previously saved analysis session")

        self.screenshotButton = QtWidgets.QPushButton(
            self.baseWidget)  # screenshot button widget
        self.userSelectionLayout.addWidget(self.screenshotButton)
        self.screenshotButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.screenshotButton.setText("Save Screenshot")
        self.screenshotButton.setToolTip(
            "Take a screenshot of the scroll area contents and save to image")

        self.modeLabel = QtWidgets.QLabel(self.baseWidget) # mode label
        self.userSelectionLayout.addWidget(self.modeLabel)
        self.modeLabel.setText("Mode")

        self.placeMarkerButton = QtWidgets.QPushButton(
            self.baseWidget)  # place marker mode button widget
        self.userSelectionLayout.addWidget(self.placeMarkerButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.placeMarkerButton.setCheckable(True)
        self.placeMarkerButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.placeMarkerButton.setText("[Mode] Place Track Markers")
        self.placeMarkerButton.setToolTip(
            "Enter mode for placing markers on loaded image.")

        # draw angle reference mode button widget
        self.drawRefButton = QtWidgets.QPushButton(self.baseWidget)
        self.userSelectionLayout.addWidget(self.drawRefButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.drawRefButton.setCheckable(True)
        self.drawRefButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.drawRefButton.setText("[Mode] Draw Angle Reference")
        self.drawRefButton.setToolTip(
            "Enter mode for drawing angle reference on loaded image.")

        self.dlFormLayout = QtWidgets.QFormLayout()  # dl form layout
        self.userSelectionLayout.addLayout(self.dlFormLayout)
        self.dlFormLayout.setLabelAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.dlFormLayout.setFormAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.dlLabel = QtWidgets.QLabel(self.baseWidget)  # dl label
        self.dlLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.dlLabel)
        self.dlLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.dlLabel.setText("Set DL")

        # dl text box (line edit) widget
        self.dlLineEdit = QtWidgets.QLineEdit(self.baseWidget)
        self.dlLineEdit.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.dlLineEdit)
        self.dlLineEdit.setText("0")
        self.dlLineEdit.setValidator(
            QtGui.QRegExpValidator(QtCore.QRegExp('[0-9]+\.?[0-9]*')))

        self.userSelectionLayout.addStretch(0)  # add stretch to segment

        # third vertical gui segment divider in top half layout
        self.vLineDiv3 = QtWidgets.QFrame(
            self.baseWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv3)
        self.vLineDiv3.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv3.setFrameShadow(QtWidgets.QFrame.Sunken)

        # console gui segment
        self.consoleLayout = QtWidgets.QVBoxLayout()  # console segment layout
        self.topUiLayout.addLayout(self.consoleLayout)

        self.consoleLabel = QtWidgets.QLabel(
            self.baseWidget)  # console label
        self.consoleLayout.addWidget(self.consoleLabel)
        self.consoleLabel.setText("Console")

        self.consoleTextBrowser = QtWidgets.QTextBrowser(  # console text browser widget
            self.baseWidget)
        self.consoleLayout.addWidget(self.consoleTextBrowser)
        self.consoleTextBrowser.setMinimumWidth(100)

        consoleHeight = self.userSelectionLayout.minimumSize().height() - \
                    self.openSaveLabel.height()
        self.pointListWidget.setFixedHeight(consoleHeight)
        self.consoleTextBrowser.setFixedHeight(consoleHeight)

        # horizontal gui segment divider between top half and bottom half of ui
        self.hLineDiv = QtWidgets.QFrame(self.baseWidget)
        self.mainLayout.addWidget(self.hLineDiv)
        self.hLineDiv.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLineDiv.setFrameShadow(QtWidgets.QFrame.Sunken)

        # layout for the bottom half of the user interface
        self.bottomUiLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.bottomUiLayout)

        # create graphics scene on which images will be displayed
        self.scene = QtWidgets.QGraphicsScene()  # graphics scene widget
        self.sceneView = QtWidgets.QGraphicsView(self.scene, self.baseWidget)  # grahics view widget
        self.bottomUiLayout.addWidget(self.sceneView)
        self.sceneView.setMinimumWidth(900)
        self.sceneView.setMinimumHeight(400)

        # instantiate QImage and PixmapItem
        self.sceneImage = QtGui.QImage()
        self.scenePixmap = QtWidgets.QGraphicsPixmapItem()
        self.scene.addItem(self.scenePixmap)

        # instantiate reference line and momentum arc objects
        self.angleRefLine = angleref.ReferenceLine(self.scene)
        self.momentumArc = fittedarc.MomentumArc(self.scene)
