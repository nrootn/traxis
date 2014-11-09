from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsEllipseItem
import numpy as np

from mainGUI import *


# Input: gui - mainGUI class to be used ONLY for printing messages
# Input: Pix - image to be analyzed [QPixmap]
# Input: P - list of points [QGraphicsEllipseItem]
# Input: C - list of tuples [(x,dx),(y,dy),(r,dr)]
# Input: dL - float specifying track width
# Output: tuple with calculated optical density and associated error
def calcOptDensity(gui, Pix, P, Circle, dL):

    gui.displayMessage("Computing optical density...")
    gui.displayMessage("Radius: %f Coordinates: %f %f" %
                       (Circle[2], Circle[0], Circle[1]))
    # Define unit vector
    unit_v = QtCore.QLineF(Circle[0], Circle[1], Circle[0] + 1, Circle[1] + 0)
    # Get angle of each point wrt unit vector
    angles = getAngles([Circle[0], Circle[1]], P, unit_v)
    print(angles)

    # Start point is ellipse with lowest angle wrt unit vector
    start_angle = min(angles)
    start_idx = angles.index(start_angle)
    start_pt = P[start_idx]
    # End point is ellipse with highest angle wrt unit vector
    end_angle = max(angles)
    end_idx = angles.index(end_angle)
    end_pt = P[end_idx]

    print(start_angle)
    print(end_angle)

    # Create and draw an arc
    arc = QGraphicsEllipseItem(
        Circle[0] - Circle[2], Circle[1] - Circle[2], 2 * Circle[2], 2 * Circle[2])
    # Need to multiply by 16.0 because function uses units of 1/16th degrees
    arc.setStartAngle(start_angle)
    arc.setSpanAngle(16.0 * (end_angle - start_angle))
    gui.scene.addItem(arc)

    # Create and draw outer arc
    # outer_arc = QGraphicsEllipseItem(
    #     Circle[0] - Circle[2] - dL, Circle[1] - Circle[2] - dL, 2 * (Circle[2] + dL), 2 * (Circle[2] + dL))
    # Need to multiply by 16.0 b cause function uses units of 1/16th degrees
    # outer_arc.setStartAngle(16.0 * start_angle)
    # outer_arc.setSpanAngle(16.0 * (end_angle - start_angle))
    # gui.scene.addItem(outer_arc)

    # Create and draw inner arc
    # inner_arc = QGraphicsEllipseItem(
    #     Circle[0] - Circle[2] + dL, Circle[1] - Circle[2] + dL, 2 * (Circle[2] + dL), 2 * (Circle[2] + dL))
    # Need to multiply by 16.0 because function uses units of 1/16th degrees
    # inner_arc.setStartAngle(16.0 * start_angle)
    # inner_arc.setSpanAngle(16.0 * (end_angle - start_angle))
    # gui.scene.addItem(inner_arc)

    # SHELL: does nothing atm
    optDens = 0.0
    errOptDens = 0.0

    return (optDens, errOptDens)


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
