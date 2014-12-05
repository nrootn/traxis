from PyQt5 import QtGui

# calibration
CMPERPX = 0.01188
ERRCMPERPX = 0.00090

# marker colours
DEFAULTMARKERCOLOR = QtGui.QColor(176, 30, 125)
STARTMARKERCOLOR = QtGui.QColor(0, 186, 186)
ENDMARKERCOLOR = QtGui.QColor(34, 197, 25)
HIGHLIGHTMARKERCOLOR = QtGui.QColor(235, 233, 0)

# momentum arc colours
ARCCOLOR = QtGui.QColor(33, 95, 147)

# reference line colours
REFLINECOLOR = QtGui.QColor(243, 42, 31)

# zoom factors
ZOOMINFACTOR = 1.25 # this should be greater than 1
ZOOMOUTFACTOR = 1/ZOOMINFACTOR

# default GUI state variables
DEFAULTPOINTSIZE = 10
DEFAULTLINEWIDTH = 2.5

# bubble chamber magnetic field
MAGNETICFIELD = 15.5 # in kG

# speed of light
C = 0.3 # in giga metres per second
