from PyQt5 import QtWidgets, QtGui, QtCore
from traxis import constants


class TangentLine(QtWidgets.QGraphicsLineItem):

    """Tangent line class. This class subclasses QGraphicsLineItem, allowing
    an object to be instantiated with a pen width and a graphics scene to
    which it will be added in addition to a QLineF object. It also adds a
    method to facilitate rescaling of the tangent line.
    """

    def __init__(self, qlinef, width, scene):
        """Instantiate a TangentLine object with qlinef, a QLineF object,
        width, the width of the pen of the tangent line, and scene, a
        QGraphicsScene to which the tangent line will be added.
        """

        # call the __init__ method of the QGraphicsLineItem superclass, passing
        # the QLineF object
        super().__init__(qlinef)

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a pen for the tangent line using the tangent colour
        linePen = QtGui.QPen(constants.TANGENTLINECOLOR)
        # set the width of the pen to width
        linePen.setWidth(width)
        # set the newly created pen as the tangent line's pen
        self.setPen(linePen)

        # add the tangent line to the graphics scene
        scene.addItem(self)

    def rescale(self, width):
        """Set the pen width of the tangent line to width."""

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a new pen, starting from the existing pen of the tangent line
        newLinePen = self.pen()
        # set the width of the new pen
        newLinePen.setWidth(width)
        # set the resized pen as the tangent line's pen
        self.setPen(newLinePen)
