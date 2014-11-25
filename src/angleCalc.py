from PyQt5 import QtCore
from PyQt5.QtWidgets import QGraphicsEllipseItem

from mainGUI import *


# Input: gui - mainGUI class to be used ONLY for printing messages
# Input: initialPoint - point at which angle is calculated [QGraphicsEllipseItem]
# Input: circle - list of tuples [(x,dx),(y,dy),(r,dr)]
# Input: lineRef - reference line [QGraphicsLineItem]
# Output: tuple with calculated angle and associated error
def angleCalc(gui, circle, initialPoint, lineRef):
    angle = 0
    errAngle = 0

    # create the perpendicularVector
    deltaX = circle[0][0] - initialPoint.rect().center().x()
    deltaY = circle[1][0] - initialPoint.rect().center().y()

    # Tangent vector is inverse of perpendicular vector
    tangentLine = QtCore.QLineF(0, 0, - deltaY, deltaX)
    tangentLineUpErr = QtCore.QLineF(
        0, 0, -(deltaY + circle[1][1]), deltaX + circle[0][1])
    tangentLineDownErr = QtCore.QLineF(
        0, 0, -(deltaY - circle[1][1]), deltaX - circle[0][1])

    # For Debug
    gui.scene.addLine(initialPoint.rect().center().x() + deltaY, initialPoint.rect().center().y() - deltaX,
     initialPoint.rect().center().x() - deltaY,
     initialPoint.rect().center().y() + deltaX)

    # compute the angles
    angle = lineRef.line().angleTo(tangentLine)
    angleUp = abs(lineRef.line().angleTo(tangentLineUpErr) - angle)
    angleDown = abs(lineRef.line().angleTo(tangentLineDownErr) - angle)

    errAngle = (angleUp + angleDown) / 2

    return (angle, errAngle)


def getAngles(origin, pts, v):
    angles = []
    # Compute angles of each point wrt v
    for p in pts:
        xx = p.rect().center().x()
        yy = p.rect().center().y()
        r = QtCore.QLineF(origin[0], origin[1], xx, yy)
        print(r)
        angles.append(QtCore.QLineF.angleTo(r, v))
    return angles
