from PyQt5 import QtCore, QtGui
import numpy as np


# Input: gui - mainGUI class to be used ONLY for printing messages
# Input: Img - image to be analyzed [QImage]
# Input: P - list of points [QGraphicsEllipseItem]
# Input: C - list of tuples [(x,dx),(y,dy),(r,dr)]
# Input: dL - float specifying track width
# Output: tuple with calculated optical density, associated error and track lenght
def calcOptDensity(Img, Circle, dL, startPt, endPt):

    # Create variables for circle parameters to make code more readable
    x0 = Circle[0][0]
    dx0 = Circle[0][1]
    y0 = Circle[1][0]
    dy0 = Circle[1][1]
    r0 = Circle[2][0]
    dr0 = 1 # To give sensical error output, assume 1 pixel error box around the selected area

    # Get angle between start point and unit vector
    start_angle = startPt.getAngle((x0, y0))

    # Get angle that spans the start vector and end vector
    # This is in degrees
    span_angle = endPt.getAngle((x0, y0), startPt)

    # Get points along arc
    dR = np.linspace(
        r0 - abs(dr0) - dL, r0 + abs(dr0) + dL, 2 * (dL + dr0) + 1)
    pointSet = set()
    errPointSet = set()

    # vectorized calculations are easier
    for r in dR:
        dTheta = np.linspace(
            start_angle, start_angle + span_angle, int(2 * r * span_angle * (np.pi / 180.0)))
        cosTransform = np.cos(dTheta * (np.pi / 180.0))
        sinTransform = np.sin(dTheta * (np.pi / 180.0))
        for i in range(0, len(dTheta)):
            x = x0 + r * cosTransform[i]
            y = y0 - r * sinTransform[i]
            if r < (r0 - dL) or r > (r0 + dL):
                errPointSet.add((int(x), int(y)))
            else:
                pointSet.add((int(x), int(y)))

    # Loop over distinct pixel coordinates and sum the blackness of each
    blackness = 0.
    for p in pointSet:
        c = Img.pixel(p[0], p[1])
        blackness += QtGui.QColor(c).blackF()

    # Repeat the calculation above for error region
    errBlackness = 0.
    for p in errPointSet:
        c = Img.pixel(p[0], p[1])
        errBlackness += QtGui.QColor(c).blackF()

    # Calculate and return optical density
    optDens = blackness 
    errOptDens = errBlackness
    trackLength = r0 * span_angle * (np.pi / 180.0)
    return (optDens, errOptDens, trackLength)
