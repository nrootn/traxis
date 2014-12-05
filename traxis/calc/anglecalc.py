import math
from PyQt5 import QtCore


def tangentCalc(circle, initialPoint):

    centerX = circle[0][0]
    centerY = circle[1][0]
    radius = circle[2][0]
    errCenterX = circle[0][1]
    errCenterY = circle[1][1]

    initialAngle = initialPoint.getAngle((centerX, centerY))*math.pi/180

    tangentPointX = radius*math.cos(initialAngle) + centerX
    tangentPointY = -radius*math.sin(initialAngle) + centerY

    # create the perpendicular vector
    relativeX = tangentPointX - centerX
    relativeY = tangentPointY - centerY

    # tangent vector is inverse of perpendicular vector
    tangentLine = QtCore.QLineF(tangentPointX + relativeY,
                                tangentPointY - relativeX,
                                tangentPointX - relativeY,
                                tangentPointY + relativeX)
    tangentLineErrA = QtCore.QLineF(tangentPointX + (relativeY - errCenterY),
                                    tangentPointY - (relativeX + errCenterX),
                                    tangentPointX - (relativeY - errCenterY),
                                    tangentPointY + (relativeX + errCenterX))
    tangentLineErrB = QtCore.QLineF(tangentPointX + (relativeY + errCenterY),
                                    tangentPointY - (relativeX - errCenterX),
                                    tangentPointX - (relativeY + errCenterY),
                                    tangentPointY + (relativeX - errCenterX))

    return tangentLine, tangentLineErrA, tangentLineErrB

def openingAngle(tangent, refLine):

    angle = refLine.line().angleTo(tangent[0])
    angleErrA = abs(refLine.line().angleTo(tangent[1]) - angle)
    angleErrB = abs(refLine.line().angleTo(tangent[2]) - angle)

    # special case: reference line is in between the two error tangents
    if angleErrA > 180:
        angleErrA = abs(angleErrA - 360)
    elif angleErrB > 180:
        angleErrB = abs(angleErrB - 360)

    errAngle = (angleErrA + angleErrB) / 2

    return (angle, errAngle)
