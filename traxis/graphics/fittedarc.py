from PyQt5 import QtGui, QtCore, QtWidgets
from traxis import constants


class ArcItem(QtWidgets.QGraphicsEllipseItem):
    
    """This class is a QGraphicsEllipseItem with a custom paint method.
    Instead a drawing an ellipse or a pie, an ArcItem object draws an arc
    when added to a graphics scene. The start and span angles of an ArcItem
    object must be specified before it is added to a graphics scene.
    """

    def paint(self, painter, option, widget=0):
        """Reimplement the paint method so that it draws arcs. painter is a
        QPainter object. option and widget are included in the parameter
        list because a graphics item paint method expects them but they are
        not used here."""

        # set the pen of the painter to the ArcItem object's pen
        painter.setPen(self.pen())
        # set the brush of the painter to the ArcItem object's brush
        painter.setBrush(self.brush())
        # draw an arc, using the ArcItem object's rect, startAngle and
        # spanAngle
        painter.drawArc(self.rect(), self.startAngle(), self.spanAngle())

class MomentumArc(object):

    """Momentum arc class. This class is a container for three ArcItem objects
    which together form the momentum arc. This class implements methods for
    manipulating the ArcItems it contains such that they function as a unit.
    A MomentumArc object is to be added to a GUI as one would add a QWidget.
    """

    def __init__(self):
        """Initialize this object's attributes, setting them to None."""

        # the attributes are all ArcItems, each with the same center, or all
        # None, if the momentum arc has not yet been drawn. The radius of the
        # outer arc is to be greater than or equal to the central arc. The
        # radius of the inner arc is to be less than or equal to the central
        # arc.
        self.centralArc = None
        self.outerArc = None
        self.innerArc = None

    def draw(self, centerX, centerY, radius, startAngle,
             spanAngle, dl, width, scene):
        """Reset the momentum arc if it has already been drawn before. Then 
        create three ArcItems, one with radius radius, the second with radius
        radius+dl and the third with radius radius-dl. Set each arc's center to
        (centerX, centerY), the start angle to startAngle and the span
        angle to spanAngle, both given in degrees. Set each arc's pen width to
        width and add each arc to scene, a QGraphicsScene.
        """

        # reset the momentum arc object
        self.reset()

        # set a minimum pen width
        if width < 1:
            width = 1

        # create a pen for the arcs using the momentum arc colour
        momentumPen = QtGui.QPen(constants.ARCCOLOR)
        # set the width of the pen to width
        momentumPen.setWidth(width)

        # create a rect for the central arc with the given center
        # coordinates and radius (for an arc with radius r, the rect will
        # have width and height 2*r)
        centralRect = QtCore.QRectF(centerX, centerY, 2 * radius, 2 * radius)
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        centralRect.moveCenter(QtCore.QPointF(centerX, centerY))
        # create an ArcItem using the rect created above. Set it
        # as the momentum arc's centralArc attribute.
        self.centralArc = ArcItem(centralRect)
        # set the start and span angles of the central arc to the given values.
        # the arc item's angle unit is 16ths of a degree so multiply the given
        # angles (which are in degrees) by 16
        self.centralArc.setStartAngle(16 * startAngle)
        self.centralArc.setSpanAngle(16 * spanAngle)
        # set the central arc's pen to the pen created above
        self.centralArc.setPen(momentumPen)

        # for the inner and outer arcs, use a dash-dot-line pen style
        momentumPen.setStyle(QtCore.Qt.DashDotLine)

        # create a rect for the outer arc with the given center
        # coordinates. Set the radius to radius+dl (for an arc with radius
        # r, the rect will have width and height 2*r)
        outerRect = QtCore.QRectF(
            centerX, centerY, 2 * (radius + dl), 2 * (radius + dl))
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        outerRect.moveCenter(QtCore.QPointF(centerX, centerY))
        # create an ArcItem using the rect created above. Set it
        # as the momentum arc's outerArc attribute.
        self.outerArc = ArcItem(outerRect)
        # set the start and span angles of the outer arc to the given values.
        # the arc item's angle unit is 16ths of a degree so multiply the given
        # angles (which are in degrees) by 16
        self.outerArc.setStartAngle(16 * startAngle)
        self.outerArc.setSpanAngle(16 * spanAngle)
        # set the outer arc's pen to the pen created above
        self.outerArc.setPen(momentumPen)

        # create a rect for the inner arc with the given center
        # coordinates. Set the radius to radius-dl (for an arc with radius
        # r, the rect will have width and height 2*r)
        innerRect = QtCore.QRectF(
            centerX, centerY, 2 * (radius - dl), 2 * (radius - dl))
        # when instantiating a rect, the given coordinates are used for the
        # top-left corner so we must explicitly move the rect's center to the
        # desired coordinates
        innerRect.moveCenter(QtCore.QPointF(centerX, centerY))
        # create an ArcItem using the rect created above. Set it
        # as the momentum arc's innerArc attribute.
        self.innerArc = ArcItem(innerRect)
        # set the start and span angles of the inner arc to the given values.
        # the arc item's angle unit is 16ths of a degree so multiply the given
        # angles (which are in degrees) by 16
        self.innerArc.setStartAngle(16 * startAngle)
        self.innerArc.setSpanAngle(16 * spanAngle)
        # set the outer arc's pen to the pen created above
        self.innerArc.setPen(momentumPen)

        # add the three arcs to the graphics scene
        scene.addItem(self.centralArc)
        scene.addItem(self.outerArc)
        scene.addItem(self.innerArc)

    def updateArcs(self, dl):
        """Redraw the inner and outer arcs so that their radii are equal to
        central arc's +/- the new dl.
        """

        # if the arcs haven't been drawn yet, return
        if not self.centralArc:
            return

        # get the width of the central arc's rect (which is equal to twice its
        # radius)
        centralWidth = self.centralArc.rect().width()

        # create a new rect, starting from the existing rect of the outer arc
        newOuterRect = self.outerArc.rect()
        # set the width and height of the new rect, incorporating the new dl
        # (the width and height of the rect are twice the radius of the arc)
        newOuterRect.setWidth(centralWidth + 2 * dl)
        newOuterRect.setHeight(centralWidth + 2 * dl)
        # move the rect's center to match that of the original rect's (the
        # center gets shifted when resizing)
        newOuterRect.moveCenter(self.outerArc.rect().center())
        # set the resized rect as the outer arc's rect
        self.outerArc.setRect(newOuterRect)

        # create a new rect, starting from the existing rect of the inner arc
        newInnerRect = self.innerArc.rect()
        # set the width and height of the new rect, incorporating the new dl
        # (the width and height of the rect are twice the radius of the arc)
        newInnerRect.setWidth(centralWidth - 2 * dl)
        newInnerRect.setHeight(centralWidth - 2 * dl)
        # move the rect's center to match that of the original rect's (the
        # center gets shifted when resizing)
        newInnerRect.moveCenter(self.innerArc.rect().center())
        # set the resized rect as the inner arc's rect
        self.innerArc.setRect(newInnerRect)

    def rescale(self, width):
        """Set the pen width of the three arcs to width."""

        # set a minimum pen width
        if width < 1:
            width = 1

        # if the arcs haven't been drawn yet, return
        if not self.centralArc:
            return

        # create a new pen, starting from the existing pen of the central arc
        newPen = self.centralArc.pen()
        # set the width of the new pen
        newPen.setWidth(width)
        # set the resized pen as the central arc's pen
        self.centralArc.setPen(newPen)

        # for the inner and outer arcs, use a dash-dot-line pen style
        newPen.setStyle(QtCore.Qt.DashDotLine)
        # set the resized pen as the inner and outer arcs' pen
        self.outerArc.setPen(newPen)
        self.innerArc.setPen(newPen)

    def reset(self):
        """Remove the momentum arc's attributes from their graphics scene and
        reset them to None.
        """

        # if the central, inner and outer arcs exist, remove them from
        # their graphics scene
        if self.centralArc:
            self.centralArc.scene().removeItem(self.centralArc)
        if self.outerArc:
            self.outerArc.scene().removeItem(self.outerArc)
        if self.innerArc:
            self.innerArc.scene().removeItem(self.innerArc)

        # reset the momentum arc's attributes to None
        self.centralArc = None
        self.outerArc = None
        self.innerArc = None
