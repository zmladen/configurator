import math
from utils import *
from ..slot import *
from ....utilities.functions import getPlotPoints
from ....enums import segmentType, statorType


class sector1(object):
    """Class that defines the countour of the sector for the inner-runner dc drive."""

    def __init__(self, stator, data={}):
        self.color = "#6fcb9f"
        self.stator = stator
        self.segmentAngle = self.stator.segmentAngle
        self.slot = slot1(self)

        # Single stator (straight back)
        if self.stator.type == statorType.stator1:
            self.slot = slot1(self)

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Slot" in data:
            if self.stator.type == statorType.stator1:
                self.slot = slot1(self, data["Slot"])

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Slot": self.slot,
            # "Coordinates": self.getCoordinates()
        }

    def getCoordinates(self, position=0):
        """Calculates the coordinates of the sector."""
        segments = ()
        l1 = line.__slopeANDpoint__(90 + self.segmentAngle / 2.0)
        l2 = line.__slopeANDpoint__(90 - self.segmentAngle / 2.0)
        l3 = line.__slopeANDpoint__(90 + self.segmentAngle / 2.0)
        l3.moveParallel(self.slot.toothThickness / 2.0)
        l4 = line.__slopeANDpoint__(90, point(-self.slot.openingLeft, 0))
        l5 = line.__slopeANDpoint__(90, point(self.slot.openingRight, 0))
        c1 = circle(self.stator.outerDiameter / 2.0)
        c2 = circle(self.stator.innerDiameter / 2.0)

        pt = c1.lineIntersection(l4)[0]
        p0 = l4.movePoint(pt, -self.slot.tipHeight)
        p1 = l4.movePoint(pt, -self.slot.tipHeight * self.slot.tipHeightReduction / 100.0)
        segments += ({"points": (p0, p1), "type": segmentType.line},)

        p1m = l1.mirrorPoint(p1)
        p2 = c1.lineIntersection(l1)[0]
        c3 = circle.__3points__(p1, p1m, p2)
        pt = p1.rotateArroundPointCopy(c3.center, abs(p1.getRelativeSlope(c3.center) - p2.getRelativeSlope(c3.center)) / 2.0)
        segments += ({"points": (p1, pt, p2), "type": segmentType.arccircle},)

        p3 = c2.lineIntersection(l1)[0]
        segments += ({"points": (p2, p3), "type": segmentType.line},)

        p4 = point(-p3.X, p3.Y)
        pt = p3.rotateArroundPointCopy(c2.center, -abs(p3.getRelativeSlope(c2.center) - p4.getRelativeSlope(c2.center)) / 2)
        segments += ({"points": (p3, pt, p4), "type": segmentType.arccircle},)

        p5 = point(-p2.X, p2.Y)
        segments += ({"points": (p4, p5), "type": segmentType.line},)

        pt = c1.lineIntersection(l5)[0]
        p7 = l5.movePoint(pt, -self.slot.tipHeight)
        p6 = l5.movePoint(pt, -self.slot.tipHeight * self.slot.tipHeightReduction / 100.0)

        p6m = l2.mirrorPoint(p6)
        c4 = circle.__3points__(p6m, p5, p6)
        pt = p5.rotateArroundPointCopy(c4.center, abs(p5.getRelativeSlope(c4.center) - p6.getRelativeSlope(c4.center)) / 2)
        segments += ({"points": (p5, pt, p6), "type": segmentType.arccircle},)
        segments += ({"points": (p6, p7), "type": segmentType.line},)
        segments += ({"points": (p7, p0), "type": segmentType.line},)

        mainPoints = (p0, p1, p2, p3, p4, p5, p6, p7)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (
                    p.rotateCopy(-90 + (position + 0.5) * 360 / self.stator.slotNumber),
                )
            rsegments += ({"points": points, "type": segment["type"]},)

        axialPointsTop = [
            point(-self.stator.stacklength / 2, self.stator.outerDiameter / 2),
            point(self.stator.stacklength / 2, self.stator.outerDiameter / 2),
            point(self.stator.stacklength / 2, self.stator.innerDiameter / 2),
            point(-self.stator.stacklength / 2, self.stator.innerDiameter / 2),
            point(-self.stator.stacklength / 2, self.stator.outerDiameter / 2),
        ]

        axialPointsBottom = [
            point(-self.stator.stacklength / 2, -self.stator.innerDiameter / 2),
            point(self.stator.stacklength / 2, -self.stator.innerDiameter / 2),
            point(self.stator.stacklength / 2, -self.stator.outerDiameter / 2),
            point(-self.stator.stacklength / 2, -self.stator.outerDiameter / 2),
            point(-self.stator.stacklength / 2, -self.stator.innerDiameter / 2),
        ]

        return {
            "polylineSegments": rsegments,
            "mainPoints": mainPoints,
            "radialPlotPoints": getPlotPoints(segments, self.stator.slotNumber),
            "axialPlotPoints": [axialPointsTop, axialPointsBottom],
        }
