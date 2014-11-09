from PyQt5 import QtCore, QtGui, QtWidgets


class GuiSkeleton(object):

    """The skeleton of the GUI."""

    def __init__(self, main_window):
        """Setup the base user interface - create layouts and place widgets
        and labels on main window.
        """

        # instantiate a base widget and set it as the main window's central
        # widget
        self.centralWidget = QtWidgets.QWidget(main_window)
        main_window.setCentralWidget(self.centralWidget)

        # layout of the main window
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        # layout for the top half of the user interface
        self.topUiLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.topUiLayout)

        # track marker list gui segment
        self.pointListLayout = QtWidgets.QVBoxLayout()  # marker segment layout
        self.topUiLayout.addLayout(self.pointListLayout)

        self.pointListLabel = QtWidgets.QLabel(
            self.centralWidget)  # marker list label
        self.pointListLayout.addWidget(self.pointListLabel)
        self.pointListLabel.setText("Track Markers")

        self.pointListWidget = QtWidgets.QListWidget(
            self.centralWidget)  # marker list widget
        self.pointListWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.pointListLayout.addWidget(self.pointListWidget)
        # don't focus on this widget when clicked
        self.pointListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pointListWidget.setMaximumSize(QtCore.QSize(100, 2000))
        self.pointListWidget.setMinimumSize(QtCore.QSize(100, 0))

        # first vertical gui segment divider in top half layout
        self.vLineDiv1 = QtWidgets.QFrame(
            self.centralWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv1)
        self.vLineDiv1.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv1.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "technical button" gui segment
        # technical button segment layout
        self.techButtonLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.techButtonLayout)

        self.resetButtonLabel = QtWidgets.QLabel(
            self.centralWidget)  # reset button label
        self.techButtonLayout.addWidget(self.resetButtonLabel)
        self.resetButtonLabel.setText("Reset Analysis")

        self.resetButton = QtWidgets.QPushButton(
            self.centralWidget)  # reset button widget
        self.techButtonLayout.addWidget(self.resetButton)
        self.resetButton.setText("Reset")
        self.resetButton.setToolTip(
            "Reset all the selected points and calculated variables")

        self.zoomLabel = QtWidgets.QLabel(self.centralWidget)  # zoom label
        self.techButtonLayout.addWidget(self.zoomLabel)
        self.zoomLabel.setText("Zoom")

        # horizontal layout for zoom buttons
        self.zoomLayout = QtWidgets.QHBoxLayout()
        self.techButtonLayout.addLayout(self.zoomLayout)

        self.zoomInButton = QtWidgets.QPushButton(
            self.centralWidget)  # zoom in button widget
        self.zoomLayout.addWidget(self.zoomInButton)
        self.zoomInButton.setText("Zoom In")
        self.zoomInButton.setToolTip("Zoom into the picture")

        self.zoomOutButton = QtWidgets.QPushButton(
            self.centralWidget)  # zoom out button widget
        self.zoomLayout.addWidget(self.zoomOutButton)
        self.zoomOutButton.setText("Zoom Out")
        self.zoomOutButton.setToolTip("Zoom out from the picture")

        self.calcLabel = QtWidgets.QLabel(
            self.centralWidget)  # calculate label
        self.techButtonLayout.addWidget(self.calcLabel)
        self.calcLabel.setText("Calculate")

        self.calcMomentumButton = QtWidgets.QPushButton(
            self.centralWidget)  # calculate momentum button widget
        self.techButtonLayout.addWidget(self.calcMomentumButton)
        self.calcMomentumButton.setText("Calculate Track Momentum")
        self.calcMomentumButton.setToolTip("Calculate Track momentum")

        # calculate optical density button widget
        self.calcDensityButton = QtWidgets.QPushButton(self.centralWidget)
        self.techButtonLayout.addWidget(self.calcDensityButton)
        self.calcDensityButton.setText("Calculate Optical Density")
        self.calcDensityButton.setToolTip("Calculate Optical Density")

        self.calcAngleButton = QtWidgets.QPushButton(
            self.centralWidget)  # calculate angle button widget
        self.techButtonLayout.addWidget(self.calcAngleButton)
        self.calcAngleButton.setText("Calculate Angle")
        self.calcAngleButton.setToolTip("Calculate Opening Angle")

        # add stretch rather than spacer
        self.techButtonLayout.addStretch(1)

        # second vertical gui segment divider in top half layout
        self.vLineDiv2 = QtWidgets.QFrame(
            self.centralWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv2)
        self.vLineDiv2.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv2.setFrameShadow(QtWidgets.QFrame.Sunken)

        # "user selection" gui segment
        # user seletion segment layout
        self.userSelectionLayout = QtWidgets.QVBoxLayout()
        self.topUiLayout.addLayout(self.userSelectionLayout)

        self.userInputLabel = QtWidgets.QLabel(
            self.centralWidget)  # user input label
        self.userSelectionLayout.addWidget(self.userInputLabel)
        self.userInputLabel.setText("User Input")

        self.openImageButton = QtWidgets.QPushButton(
            self.centralWidget)  # open image button widget
        self.userSelectionLayout.addWidget(self.openImageButton)
        self.openImageButton.setText("Open Image")
        self.openImageButton.setToolTip("Open image for analysis")

        self.placeMarkerButton = QtWidgets.QPushButton(
            self.centralWidget)  # place marker mode button widget
        self.userSelectionLayout.addWidget(self.placeMarkerButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.placeMarkerButton.setCheckable(True)
        # have this mode selected by default
        self.placeMarkerButton.setChecked(True)
        self.placeMarkerButton.setText("[Mode] Place Track Markers")
        self.placeMarkerButton.setToolTip(
            "Enter mode for placing markers on loaded image.")

        # draw angle reference mode button widget
        self.drawRefButton = QtWidgets.QPushButton(self.centralWidget)
        self.userSelectionLayout.addWidget(self.drawRefButton)
        # make the button checkable (i.e. stays depressed when clicked)
        self.drawRefButton.setCheckable(True)
        self.drawRefButton.setText("[Mode] Draw Angle Reference")
        self.drawRefButton.setToolTip(
            "Enter mode for drawing angle reference on loaded image.")

        self.dlFormLayout = QtWidgets.QFormLayout()  # dl form layout
        self.userSelectionLayout.addLayout(self.dlFormLayout)
        self.dlFormLayout.setLabelAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.dlFormLayout.setFormAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.dlLabel = QtWidgets.QLabel(self.centralWidget)  # dl label
        self.dlLabel.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.LabelRole, self.dlLabel)
        self.dlLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.dlLabel.setText("Set DL")

        # dl text box (line edit) widget
        self.dlLineEdit = QtWidgets.QLineEdit(self.centralWidget)
        self.dlLineEdit.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.dlFormLayout.setWidget(
            0, QtWidgets.QFormLayout.FieldRole, self.dlLineEdit)
        self.dlLineEdit.setText("0")
        self.userSelectionLayout.addStretch(1)

        # third vertical gui segment divider in top half layout
        self.vLineDiv3 = QtWidgets.QFrame(
            self.centralWidget)  # vertical divider widget
        self.topUiLayout.addWidget(self.vLineDiv3)
        self.vLineDiv3.setFrameShape(QtWidgets.QFrame.VLine)
        self.vLineDiv3.setFrameShadow(QtWidgets.QFrame.Sunken)

        # console gui segment
        self.consoleLayout = QtWidgets.QVBoxLayout()  # console segment layout
        self.topUiLayout.addLayout(self.consoleLayout)

        self.consoleLabel = QtWidgets.QLabel(
            self.centralWidget)  # console label
        self.consoleLayout.addWidget(self.consoleLabel)
        self.consoleLabel.setText("Console")

        self.consoleTextBrowser = QtWidgets.QTextBrowser(  # console text browser widget
            self.centralWidget)
        self.consoleLayout.addWidget(self.consoleTextBrowser)
        # don't focus on this widget when clicked
        self.consoleTextBrowser.setFocusPolicy(QtCore.Qt.NoFocus)
        self.consoleTextBrowser.setMinimumSize(QtCore.QSize(100, 0))

        # spacerItemConsole = QtWidgets.QSpacerItem( # add a spacer item at the bottom of the console segment
        #    100, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        # self.mainLayout.addItem(spacerItemConsole)

        # horizontal gui segment divider between top half and bottom half of ui
        self.hLineDiv = QtWidgets.QFrame(self.centralWidget)
        self.mainLayout.addWidget(self.hLineDiv)
        self.hLineDiv.setFrameShape(QtWidgets.QFrame.HLine)
        self.hLineDiv.setFrameShadow(QtWidgets.QFrame.Sunken)

        # layout for the bottom half of the user interface
        self.bottomUiLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addLayout(self.bottomUiLayout)

        # scroll area on which the graphics scene will be displayed
        self.sceneScrollArea = QtWidgets.QScrollArea(
            self.centralWidget)  # scroll area widget
        self.bottomUiLayout.addWidget(self.sceneScrollArea)
        self.sceneScrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.sceneScrollArea.setMinimumSize(
            QtCore.QSize(0, main_window.size().height() / 1.5))
        self.sceneScrollArea.setWidgetResizable(True)

        # create graphics scene on which images will be displayed
        self.scene = QtWidgets.QGraphicsScene()  # graphics scene widget
        self.view = QtWidgets.QGraphicsView(self.scene)  # grahics view widget
        # specify the graphics scene as the child widget of the scroll area
        self.sceneScrollArea.setWidget(self.view)
        # set keyboard focus to the graphics view by default
        self.view.setFocus()
        self.pixmapItem = QtWidgets.QGraphicsPixmapItem(  # create pixmap item with blank image
            QtGui.QPixmap('bkgPicture.png'), None)
        self.scene.addItem(self.pixmapItem)

        # status bar at the bottom of the window
        self.statusBar = QtWidgets.QStatusBar(main_window)
        main_window.setStatusBar(self.statusBar)

        # To the correct mane and labels
        QtCore.QMetaObject.connectSlotsByName(main_window)
