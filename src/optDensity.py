from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QImage, QColor
from PyQt5.QtWidgets import QGraphicsEllipseItem
import numpy as np

from mainGUI import *


# Input: gui - mainGUI class to be used ONLY for printing messages
# Input: Img - image to be analyzed [QImage]
# Input: P - list of points [QGraphicsEllipseItem]
# Input: C - list of tuples [(x,dx),(y,dy),(r,dr)]
# Input: dL - float specifying track width
# Output: tuple with calculated optical density and associated error
def calcOptDensity(gui, Img, P, Circle, dL, startPt, endPt):

    # Create variables for circle parameters to make code more readable
    x0 = Circle[0][0]
    dx0 = Circle[0][1]
    y0 = Circle[1][0]
    dy0 = Circle[1][1]
    r0 = Circle[2][0]
    dr0 = Circle[2][1]

    # Get angle between start point and unit vector
    start_angle = getAngle([x0, y0], startPt, [x0 + 1, y0 + 0])

    # Get angle that spans the start vector and end vector
    span_angle = getAngle([x0, y0], endPt, startPt)

    # Create and draw outer arc
    outer_arc = QGraphicsEllipseItem(
        x0 - r0 - dL, y0 - r0 - dL, 2 * (r0 + dL), 2 * (r0 + dL))
    # Need to multiply by 16.0 b cause function uses units of 1/16th degrees
    outer_arc.setStartAngle(16.0 * start_angle)
    outer_arc.setSpanAngle(16.0 * span_angle)
    gui.scene.addItem(outer_arc)

    # Create and draw inner arc
    inner_arc = QGraphicsEllipseItem(
        x0 - r0 + dL, y0 - r0 + dL, 2 * (r0 - dL), 2 * (r0 - dL))
    # Need to multiply by 16.0 because function uses units of 1/16th degrees
    inner_arc.setStartAngle(16.0 * start_angle)
    inner_arc.setSpanAngle(16.0 * span_angle)
    gui.scene.addItem(inner_arc)

    # Get points along arc
    dR = np.linspace(
        r0 - abs(dr0) - dL, r0 + abs(dr0) + dL, 2 * (dL + dr0) + 1)
    pointSet = set()
    errPointSet = set()

    # Loop through all arc points and create set of distinct pixel values
    for r in dR:
        dTheta = np.linspace(
            start_angle, start_angle + span_angle, int(r * span_angle))
        for theta in dTheta:
            radians = theta * (np.pi / 180.0)
            x = x0 + r * np.cos(radians)
            y = y0 - r * np.sin(radians)
            if r < (r0 - dL) or r > (r0 + dL):
                errPointSet.add((int(x), int(y)))
            else:
                pointSet.add((int(x), int(y)))
    
    # Loop over distinct pixel coordinates and sum the blackness of each
    blackness = 0.
    num = 0.
    for p in pointSet:
        c = Img.pixel(p[0], p[1])
        blackness += QColor(c).blackF()
        num += 1

    # Repeat the calculation above for error region
    errBlackness = 0.
    errNum = 0.
    for p in errPointSet:
        c = Img.pixel(p[0], p[1])
        errBlackness += QColor(c).blackF()
        errNum += 1

    # Calculate and return optical density
    print("num: %f" % num)
    print("errNum: %f" % errNum)
    optDens = blackness / num
    errOptDens = errBlackness / errNum

    return (optDens, errOptDens)


def getAngles(origin, pts, v_pt):
    angles = []
    # Compute angles of each point wrt v
    for p in pts:
        angles.append(getAngle(origin, p, v_pt))
    return angles


def getAngle(origin, r_pt, v_pt):

    # Define vector r
    if r_pt.__class__.__name__ == 'QGraphicsEllipseItem':
        rx = r_pt.rect().center().x()
        ry = r_pt.rect().center().y()
    else:
        rx = r_pt[0]
        ry = r_pt[1]
    r = QtCore.QLineF(origin[0], origin[1], rx, ry)

    # Define vector v
    if v_pt.__class__.__name__ == 'QGraphicsEllipseItem':
        vx = v_pt.rect().center().x()
        vy = v_pt.rect().center().y()
    else:
        vx = v_pt[0]
        vy = v_pt[1]
    v = QtCore.QLineF(origin[0], origin[1], vx, vy)

    # Compute angle between vector r and v
    angle = QtCore.QLineF.angleTo(v, r)
    return angle


def getRoi():
    return
