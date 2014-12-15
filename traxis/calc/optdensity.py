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

import numpy as np
from PyQt5 import QtGui


def calcBlackness(image, circleParams, dL, startAngle, spanAngle):
    """Given image, a QImage, a circle defined by circleParams (a dict
    containing the radius and centre coordinates of a circle), a
    startAngle and spanAngle (both in degrees) specifying an arc of that
    circle, and dL, the 'infinitesimal' thickness of a polar rectangle
    surrounding that arc, return the sum of the blackness of all the pixels
    in image that are contained within the polar rectangle along with an
    error on the blackness.
    """

    # assume 1 px error on the dL
    dLErr = 1

    # initialize a set of distinct points that are contained within the polar
    # rectangle surrounding an arc of the circle defined by circleParams
    # from startAngle to startAngle + spanAngle and with radial thickness
    # 2*dL+1
    pointSet = set()
    # initialize also a set of distinct points that are in the polar rectangles
    # of thickness dLErr that lie radially just above and just below the
    # previously defined polar rectangle
    errPointSet = set()

    # loop over all the points in the combined area of the three polar
    # rectangles, adding each point to the appropriate set
    radii = np.linspace(circleParams['radius'] - dL - dLErr,
                        circleParams['radius'] + dL + dLErr,
                        2 * (dL + dLErr) + 1)
    for r in radii:
        # for the number of angles to generate, use twice the length of the
        # arc in pixels to ensure every pixel in the region is covered
        angles = np.linspace(startAngle, startAngle + spanAngle,
                             int(2 * r * spanAngle * (np.pi / 180)))
        # compute cos and sin for each angle
        cosAngles = np.cos(angles * (np.pi / 180))
        sinAngles = np.sin(angles * (np.pi / 180))
        for angleIndex in range(len(angles)):
            # get the x and y coordinates of the point
            x = circleParams['centerX'] + r * cosAngles[angleIndex]
            # note: y values increase going down
            y = circleParams['centerY'] - r * sinAngles[angleIndex]
            # add the point to the appropriate set
            if r < (circleParams['radius'] - dL) or r > (circleParams['radius'] + dL):
                errPointSet.add((int(x), int(y)))
            else:
                pointSet.add((int(x), int(y)))

    # sum up the black colour components of pixels located at the points in
    # pointSet
    blackness = 0
    for point in pointSet:
        pixel = image.pixel(point[0], point[1])
        blackness += QtGui.QColor(pixel).blackF()

    # sum up the black colour components of pixels located at the points in
    # errPointSet
    errBlackness = 0
    for point in errPointSet:
        pixel = image.pixel(point[0], point[1])
        errBlackness += QtGui.QColor(pixel).blackF()

    return blackness, errBlackness
