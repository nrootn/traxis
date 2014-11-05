from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QGraphicsEllipseItem as qgei


# Input: Img - image to be analyzed [QPixmap]
# Input: P - list of points [QGraphicsEllipseItem]
# Input: Circle - list of tuples [(x,dx),(y,dy),(r,dr)]
# Input: dL - float specifying track width
# Output: tuple with calculated optical density and associated error
def calcOptDensity(gui, Img, P, Circle, dL):

    # SHELL: does nothing atm
    optDens = 0.0
    errOptDens = 0.0

    return (optDens, errOptDens)


if __name__ == "__main__":
    # List of qgei points
    pts = [qgei(36, 14, 10, 10),
           qgei(36, 10, 10, 10),
           qgei(19, 28, 10, 10),
           qgei(18, 31, 10, 10),
           qgei(33, 18, 10, 10),
           qgei(26, 26, 10, 10)]

    #
