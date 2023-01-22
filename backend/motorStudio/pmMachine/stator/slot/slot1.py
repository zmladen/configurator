import math
from utils import *
from ....enums import segmentType
from ....utilities.functions import getPlotPoints


class slot1:
    """Class that defines the slot countour with the round back."""

    def __init__(self, sector, data={}):
        self.color = "#EEEED1"
        self.sector = sector
        self.tipHeightReduction = 10
        self.toothThickness = 3.8
        self.yokeThickness = 2.475
        self.tipHeight = 0.8
        self.tipAngle = 120
        self.openingLeft = 0.95
        self.openingRight = 0.95
        self.backWidth = 3.11
        self.backAngle = 90
        self.segmentAngle = sector.segmentAngle
        self.connectionAngle = 90
        self.connectionOpening = 0.5
        self.connectionPeekRatio = 50
        self.slotDiameter = 12
        self.slotClosingHeight = 0.2
        self.spokeAngle = 120
        self.spokeGap = 0.5
        self.spokeBridgeHeight = 0.25
        self.connectionHeight = 1.5
        self.connectionWidth = 6.5
        self.connectionThickness = 0.15

        if not data == {}:
            self.readJSON(data)

        self.area = None
        self.coordinates = self.getCoordinates()

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Tip Height Reduction (%)" in data:
            self.tipHeightReduction = float(data["Tip Height Reduction (%)"])
        if "Tooth Thickness (mm)" in data:
            self.toothThickness = data["Tooth Thickness (mm)"]
        if "Yoke Thickness (mm)" in data:
            self.yokeThickness = data["Yoke Thickness (mm)"]
        if "Tip Height (mm)" in data:
            self.tipHeight = data["Tip Height (mm)"]
        if "Tip Angle (deg)" in data:
            self.tipAngle = data["Tip Angle (deg)"]
        if "Opening Left (mm)" in data:
            self.openingLeft = data["Opening Left (mm)"]
        if "Opening Right (mm)" in data:
            self.openingRight = data["Opening Right (mm)"]
        if "Back Width (mm)" in data:
            self.backWidth = data["Back Width (mm)"]
        if "Back Angle (deg)" in data:
            self.backAngle = data["Back Angle (deg)"]
        if "Slot Diameter (mm)" in data:
            self.slotDiameter = data["Slot Diameter (mm)"]
        if "Connection Angle (deg)" in data:
            self.connectionAngle = data["Connection Angle (deg)"]
        if "Connection Opening (mm)" in data:
            self.connectionOpening = data["Connection Opening (mm)"]
        if "Connection Peek Ratio (%)" in data:
            self.connectionPeekRatio = data["Connection Peek Ratio (%)"]
        if "Slot Closing Height (mm)" in data:
            self.slotClosingHeight = data["Slot Closing Height (mm)"]
        if "Spoke Angle (deg)" in data:
            self.spokeAngle = data["Spoke Angle (deg)"]
        if "Spoke Gap (mm)" in data:
            self.spokeGap = data["Spoke Gap (mm)"]
        if "Spoke Bridge Height (mm)" in data:
            self.spokeBridgeHeight = data["Spoke Bridge Height (mm)"]
        if "Connection Height (mm)" in data:
            self.connectionHeight = data["Connection Height (mm)"]
        if "Connection Width (mm)" in data:
            self.connectionWidth = data["Connection Width (mm)"]
        if "Connection Thickness (mm)" in data:
            self.connectionThickness = data["Connection Thickness (mm)"]

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Tip Height Reduction (%)": self.tipHeightReduction,
            "Tooth Thickness (mm)": self.toothThickness,
            "Yoke Thickness (mm)": self.yokeThickness,
            "Tip Height (mm)": self.tipHeight,
            "Tip Angle (deg)": self.tipAngle,
            "Opening Left (mm)": self.openingLeft,
            "Opening Right (mm)": self.openingRight,
            "Color": self.color,
            'Back Width (mm)': self.backWidth,
            'Back Angle (deg)': self.backAngle,
            'Slot Diameter (mm)': self.slotDiameter,
            "Connection Opening (mm)": self.connectionOpening,
            "Connection Angle (deg)": self.connectionAngle,
            "Connection Peek Ratio (%)": self.connectionPeekRatio,
            "Slot Closing Height (mm)": self.slotClosingHeight,
            "Spoke Angle (deg)": self.spokeAngle,
            "Spoke Gap (mm)": self.spokeGap,
            "Area (mm2)": self.area,
            "Spoke Bridge Height (mm)": self.spokeBridgeHeight,
            "Connection Height (mm)": self.connectionHeight,
            "Connection Width (mm)": self.connectionWidth,
            "Connection Thickness (mm)": self.connectionThickness,
            # "Coordinates": self.getCoordinates(),
        }

    def getCoordinates(self, position=0):
        """
        Calculates the coordinates of the slot.

        :param int position: Position of the slot. Used to rotate the coordinates to the corresponding position.
        :return: dictionary = {'polylineSegments' : rsegments, 'mainPoints' : mainPoints}:
        """
        l1 = line.__slopeANDpoint__(90 + self.segmentAngle / 2.0)
        l2 = line.__slopeANDpoint__(90 - self.segmentAngle / 2.0)
        l1.moveParallel(self.toothThickness / 2.0)
        l2.moveParallel(self.toothThickness / 2.0)
        l3 = line.__slopeANDpoint__(90, point(-self.openingLeft, 0))
        l4 = line.__slopeANDpoint__(90, point(self.openingRight, 0))
        c1 = circle(self.sector.stator.innerDiameter / 2.0)
        c2 = circle(self.sector.stator.outerDiameter /
                    2.0 - self.yokeThickness)
        pt = c1.lineIntersection(l3)[0]
        p1 = l3.movePoint(pt, self.tipHeight)
        p0 = l3.movePoint(pt, self.tipHeight * self.tipHeightReduction / 100.0)
        p3 = c2.lineIntersection(l1)[0]
        l5 = line.__slopeANDpoint__(
            90 - (self.tipAngle - self.segmentAngle / 2.0), p1)
        p2 = l1.lineIntersection(l5)
        p4 = c2.lineIntersection(l2)[0]
        pt = c1.lineIntersection(l4)[0]
        p6 = l4.movePoint(pt, self.tipHeight)
        p7 = l4.movePoint(pt, self.tipHeight * self.tipHeightReduction / 100.0)
        l6 = line.__slopeANDpoint__(-90 +
                                    (self.tipAngle - self.segmentAngle / 2.0), p6)
        p5 = l6.lineIntersection(l2)

        segments = ()
        # segments += ({'points' : (p0, p1), 'type' : segmentType.line}, )
        segments += ({"points": (p1, p2), "type": segmentType.line},)
        segments += ({"points": (p2, p3), "type": segmentType.line},)
        pt = p3.rotateArroundPointCopy(
            c2.center,
            -abs(p3.getRelativeSlope(c2.center) -
                 p4.getRelativeSlope(c2.center)) / 2.0,
        )
        segments += ({"points": (p3, pt, p4), "type": segmentType.arccircle},)
        segments += ({"points": (p4, p5), "type": segmentType.line},)
        segments += ({"points": (p5, p6), "type": segmentType.line},)
        segments += ({"points": (p6, p1), "type": segmentType.line},)
        # segments += ({'points' : (p7, p0), 'type' : segmentType.line}, )

        mainPoints = (p0, p1, p2, p3, p4, p5, p6, p7)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (
                    p.rotateCopy(
                        -90 + (position + 0.5) * 360.0 /
                        self.sector.stator.slotNumber
                    ),
                )
            rsegments += ({"points": points, "type": segment["type"]},)

        return {
            "polylineSegments": rsegments,
            "mainPoints": mainPoints,
            "radialPlotPoints": getPlotPoints(segments, self.sector.stator.slotNumber),
        }

    def setArea(self):
        self.area = self.sector.stator.geometry.getSlotArea()
