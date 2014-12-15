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

from PyQt5 import QtGui


# calibration
CMPERPX = 0.01188 # the number of cm in the actual bubble chamber corresponding
                  # to each pixel in a bubble chamber image scan
ERRCMPERPX = 0.00090 # the error on the px to cm conversion

# marker colours
DEFAULTMARKERCOLOR = QtGui.QColor(176, 30, 125)
STARTMARKERCOLOR = QtGui.QColor(0, 186, 186)
ENDMARKERCOLOR = QtGui.QColor(34, 197, 25)
HIGHLIGHTMARKERCOLOR = QtGui.QColor(235, 233, 0)

# momentum arc colours
ARCCOLOR = QtGui.QColor(33, 95, 147)

# reference line colours
REFLINECOLOR = QtGui.QColor(243, 42, 31)

# tangent line colours
TANGENTLINECOLOR = QtGui.QColor(0, 0, 0)

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
