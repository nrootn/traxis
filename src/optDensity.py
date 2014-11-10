from PyQt5 import QtCore
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

    gui.displayMessage("Computing optical density...")
    gui.displayMessage("Radius: %f Coordinates: %f %f" %
                       (Circle[2], Circle[0], Circle[1]))

    # Get angle between start point and unit vector
    start_angle = getAngle(
        [Circle[0], Circle[1]], startPt, [Circle[0] + 1, Circle[1] + 0])

    # Get angle that spans the start vector and end vector
    span_angle = getAngle([Circle[0], Circle[1]], endPt, startPt)

    # Create and draw an arc
    arc = QGraphicsEllipseItem(
        Circle[0] - Circle[2], Circle[1] - Circle[2], 2 * Circle[2], 2 * Circle[2])
    # Need to multiply by 16.0 because function uses units of 1/16th degrees
    arc.setStartAngle(16.0 * start_angle)
    arc.setSpanAngle(16.0 * span_angle)
    gui.scene.addItem(arc)

    # Create and draw outer arc
    outer_arc = QGraphicsEllipseItem(
        Circle[0] - Circle[2] - dL, Circle[1] - Circle[2] - dL, 2 * (Circle[2] + dL), 2 * (Circle[2] + dL))
    # Need to multiply by 16.0 b cause function uses units of 1/16th degrees
    outer_arc.setStartAngle(16.0 * start_angle)
    outer_arc.setSpanAngle(16.0 * span_angle)
    gui.scene.addItem(outer_arc)

    # Create and draw inner arc
    inner_arc = QGraphicsEllipseItem(
        Circle[0] - Circle[2] + dL, Circle[1] - Circle[2] + dL, 2 * (Circle[2] - dL), 2 * (Circle[2] - dL))
    # Need to multiply by 16.0 because function uses units of 1/16th degrees
    inner_arc.setStartAngle(16.0 * start_angle)
    inner_arc.setSpanAngle(16.0 * span_angle)
    gui.scene.addItem(inner_arc)

    # Get points along arc
    dR = np.linspace(Circle[2] - dL, Circle[2] + dL, 100.0)
    dTheta = np.linspace(start_angle, start_angle + span_angle, 100.0)

    # Loop through all arc points and average alphas
    alpha = 0.
    num = 0.
    for r in dR:
        for theta in dTheta:
            radians = theta * (np.pi / 180.0)
            x = Circle[0] + r * np.cos(radians)
            y = Circle[1] + r * np.sin(radians)
            # print("%f, %f" % (x, y))
            # c = Img.pixel(int(x), int(y))
            # colors = QColor(c).getRgbF()
            Img.setPixel(QtCore.QPoint(int(x), int(y)), 255)
            alpha += x * y
            num += 1

# SHELL: does nothing atm
    optDens = alpha / num
    errOptDens = 0.0

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
