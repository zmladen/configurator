import math
from utils import *
from ....utilities.functions import getPlotPoints
from ....enums import segmentType


class slot1:
    """Class that defines the slot countour for the inner-runner dc motor with straight back."""

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
        self.segmentAngle = sector.segmentAngle
        self.roundingRadius = 0.3
        self.area = None
        if not data == {}:
            self.readJSON(data)


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
        if "Rounding Radius (mm)" in data:
            self.roundingRadius = data["Rounding Radius (mm)"]

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
            "Area (mm2)": self.area,
            "Rounding Radius (mm)": self.roundingRadius
            # "Coordinates": self.getCoordinates(),
        }

    def getCoordinates(self, position=0):
        """Calculates the coordinates of the slot."""
        l1 = line.__slopeANDpoint__(90 + self.segmentAngle / 2.0)
        l2 = line.__slopeANDpoint__(90 - self.segmentAngle / 2.0)
        l1.moveParallel(self.toothThickness / 2.0)
        l2.moveParallel(self.toothThickness / 2.0)
        l3 = line.__slopeANDpoint__(90, point(-self.openingLeft, 0))
        l4 = line.__slopeANDpoint__(90, point(self.openingRight, 0))
        c1 = circle(self.sector.stator.outerDiameter / 2.0)
        c2 = circle(self.sector.stator.innerDiameter / 2.0)

        pt = c1.lineIntersection(l3)[0]
        p1 = l3.movePoint(pt, -self.tipHeight)
        p0 = l3.movePoint(pt, -self.tipHeight * self.tipHeightReduction / 100.0)
        l5 = line.__slopeANDpoint__(0, point(0, self.sector.stator.innerDiameter / 2.0 + self.yokeThickness))
        p3 = l1.lineIntersection(l5)
        l6 = line.__slopeANDpoint__(90 + (self.tipAngle + self.segmentAngle / 2.0), p1)
        p2 = l1.lineIntersection(l6)
        p4 = point(-p3.X, p3.Y)
        pt = c1.lineIntersection(l4)[0]
        p6 = l4.movePoint(pt, -self.tipHeight)
        p7 = l4.movePoint(pt, -self.tipHeight * self.tipHeightReduction / 100.0)
        l7 = line.__slopeANDpoint__(-90 - (self.tipAngle + self.segmentAngle / 2.0), p6)
        p5 = l2.lineIntersection(l7)

        segments = ()
        # segments += ({'points': (p0, p1), 'type': segmentType.line}, )
        segments += ({'points': (p1, p2), 'type': segmentType.line}, )
        segments += ({'points': (p2, p3), 'type': segmentType.line}, )
        segments += ({'points': (p3, p4), 'type': segmentType.line}, )
        segments += ({'points': (p4, p5), 'type': segmentType.line}, )
        segments += ({'points': (p5, p6), 'type': segmentType.line}, )
        segments += ({'points': (p6, p1), 'type': segmentType.line}, )
        # segments += ({'points': (p6, p7), 'type': segmentType.line}, )
        # segments += ({'points': (p7, p0), 'type': segmentType.line}, )
        mainPoints = (p0, p1, p2, p3, p4, p5, p6, p7)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment['points']:
                points += (p.rotateCopy(-90 + (position + 0.5) * 360 / self.sector.stator.slotNumber), )
            rsegments += ({'points': points, 'type': segment['type']}, )

        return {
            'polylineSegments': rsegments,
            'mainPoints': mainPoints,
            "radialPlotPoints": getPlotPoints(segments, self.sector.stator.slotNumber),
        }

    def setArea(self):
        self.area = self.sector.stator.geometry.getSlotArea()
