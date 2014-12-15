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
from PyQt5 import QtWidgets, QtGui
from traxis.gui import maingui


class TraxisApplicationWindow(QtWidgets.QMainWindow):

    """Subclass of QMainWindow, which sets the window's title and icon, and
    instantiates the MainWidget, setting it as the window's central widget.
    """

    def __init__(self):

        super().__init__()

        # set window title
        self.setWindowTitle("Traxis")

        # set the window's icon (it is kept in the root traxis directory)
        # note: this icon won't get displayed on a Mac
        icon = QtGui.QIcon()
        basePath = sys.path[0]
        icon.addPixmap(QtGui.QPixmap(os.path.join(basePath, "traxis.png")))
        self.setWindowIcon(icon)

        # initialize MainWidget and set it as the window's central widget
        self.setCentralWidget(maingui.MainWidget())
