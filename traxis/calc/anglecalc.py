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

import math
from PyQt5 import QtCore


def tangentCalc(circleParams, point):
    """Given a circle defined by circleParams (a dict containing the radius
    and center coordinates of the circle along with the errors on these
    parameters) and point, one of the TrackMarker objects to which
    the circle was fitted, return three QLineF objects, one being the tangent
    to the circle at point and the other two being the errors on the
    tangent line in each direction. The real tangent lies somewhere between
    the two error lines.
    """

    # compute the angular coordinate of the point with respect to the center
    # of the circle
    pointAngle = point.getAngle((circleParams['centerX'],
                                 circleParams['centerY']))*math.pi/180

    # determine the coordinates of the point that has the same angular
    # coordinate as point but actually lies on the circle
    tangentPointX = circleParams['radius']*math.cos(pointAngle) + \
                    circleParams['centerX']
    # note: y values increase going down
    tangentPointY = -circleParams['radius']*math.sin(pointAngle) + \
                    circleParams['centerY']

    # determine the coordinates of the tangent point relative to the center of
    # the circle -- the line joining the centre to the tangent point is
    # perpendicular to the tangent line
    relativeX = tangentPointX - circleParams['centerX']
    relativeY = tangentPointY - circleParams['centerY']

    # construct the tangent line
    tangentLine = QtCore.QLineF(tangentPointX + relativeY,
                                tangentPointY - relativeX,
                                tangentPointX - relativeY,
                                tangentPointY + relativeX)

    # construct the two error tangent lines using the error on the circle
    # center. These two lines also pass through the tangent point and the real
    # tangent line lies between these two lines within error. Note that the
    # error on the circle radius is not considered when constructing the error
    # tangents because it would only translate the tangent radially without
    # changing the slope
    tangentLineErrA = QtCore.QLineF(tangentPointX + \
                                      (relativeY - circleParams['centerYErr']),
                                    tangentPointY - \
                                      (relativeX + circleParams['centerXErr']),
                                    tangentPointX - \
                                      (relativeY - circleParams['centerYErr']),
                                    tangentPointY + \
                                      (relativeX + circleParams['centerXErr']))
    tangentLineErrB = QtCore.QLineF(tangentPointX + \
                                      (relativeY + circleParams['centerYErr']),
                                    tangentPointY - \
                                      (relativeX - circleParams['centerXErr']),
                                    tangentPointX - \
                                      (relativeY + circleParams['centerYErr']),
                                    tangentPointY + \
                                      (relativeX - circleParams['centerXErr']))

    return tangentLine, tangentLineErrA, tangentLineErrB

def openingAngle(tangent, tangentErrA, tangentErrB, refLine):
    """Return the angle (in degrees) between tangent, a QLineF, and refLine,
    a ReferenceLine object. Return also the error on the angle using the
    two tangent error lines tangentErrA and tangentErrB, both QLineF objects.
    """

    # compute the angle between the reference line and the tangent line
    angle = refLine.line.line().angleTo(tangent)

    # compute the differences between the angles between the reference line
    # and the error tangent lines and the angle between the reference line
    # and the tangent estimate. These give the error on the angle in both
    # directions.
    angleErrA = abs(refLine.line.line().angleTo(tangentErrA) - angle)
    angleErrB = abs(refLine.line.line().angleTo(tangentErrB) - angle)

    # special case: reference line is in between the two error tangents.
    # one of the two angle errors will be 360 - theta in this case
    if angleErrA > 180:
        angleErrA = abs(angleErrA - 360)
    elif angleErrB > 180:
        angleErrB = abs(angleErrB - 360)

    # take the error on the angle to be the average of the errors in each
    # direction
    errAngle = (angleErrA + angleErrB) / 2

    return angle, errAngle
