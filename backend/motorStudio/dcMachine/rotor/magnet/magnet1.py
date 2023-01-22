import math
import os
from utils import *
from materials import *
from ..pocket import pocket1
from ....enums import pocketType, segmentType
from ....utilities.functions import getPlotPoints


class magnet1:
    """Class that defines the segment magnet shape for the DC machine."""

    def __init__(self, pocket, data={}):
        self.color = '#FEB144'
        self.pocket = pocket
        self.height = 7
        self.embrace = 50
        self.frontAngle = 87
        self.backAngle = 70
        self.edgeAngle = 20
        self.cutSide = 0.5
        self.topAirgap = 0.3
        self.edgeAirgap = 0.5
        self.offset = 0
        self.length = 30
        self.material = {"Used": {"id": "init", "name": "init"}, "Options": [{"id": "init", "name": "init"}]}

        if not data == {}:
            self.readJSON(data)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.pocket.pole.rotor.poleNumber

    @property
    def poleAngle(self):
        """Magnet pole angle in deg."""
        return self.segmentAngle * self.embrace / 100.0

    def getCoordinates(self, position=0):
        """Calculates the coordinates of the magnet."""

        l1 = line.__slopeANDpoint__(90 + (self.segmentAngle * self.embrace / 100.0) / 2.0)
        l2 = line.__slopeANDpoint__(90 + self.frontAngle / 2.0)
        l7 = line.__slopeANDpoint__(90 + self.backAngle / 2.0)
        outerDiameter = self.pocket.pole.rotor.innerDiameter + 2 * self.height
        innerDiameter = self.pocket.pole.rotor.innerDiameter

        c1 = circle(innerDiameter / 2.0 - self.offset, point(0, self.offset))
        c2 = circle(outerDiameter / 2, point(0, 0))
        c3 = circle(outerDiameter / 2 - self.edgeAirgap, point(0, 0))

        p0 = c1.lineIntersection(l2)[0]
        l3 = c1.findTangentThroughPoint(p0)
        p1 = l1.lineIntersection(l3)
        p4 = c2.lineIntersection(l7)[0]
        l6 = line.__slopeANDpoint__(180 - self.edgeAngle, p1)
        pi = c3.lineIntersection(l6)[0]

        if self.cutSide == 0:
            p2 = point(pi.X, pi.Y)
            p3 = point(pi.X, pi.Y)
        else:
            l4 = line.__slopeANDpoint__(90, pi)
            l4.moveParallelyAxis(self.cutSide)
            p2 = l6.lineIntersection(l4)
            p3 = c3.lineIntersection(l4)[0]

        p5 = point(-p4.X, p4.Y)
        p6 = point(-p3.X, p3.Y)
        p7 = point(-p2.X, p2.Y)
        p8 = point(-p1.X, p1.Y)
        p9 = point(-p0.X, p0.Y)

        helpAngle = (self.segmentAngle * self.embrace / 100.0) - self.backAngle
        helpCircle = circle(outerDiameter / 2 - self.edgeAirgap / 2, point(0, 0))

        ct = circle.__3points__(p4, point(0, outerDiameter / 2 - self.topAirgap), p5)
        cl = circle.__3points__(p3, helpCircle.pointOnCircle(90 + (self.backAngle - helpAngle / 2)), p4)
        cr = circle.__3points__(p5, helpCircle.pointOnCircle(90 - (self.backAngle - helpAngle / 2)), p6)

        mainPoints = (p0, p1, p2, p3, p4, p5, p6, p7, p8, p9)
        segments = ()
        segments += ({'points': (p0, p1), 'type': segmentType.line}, )
        segments += ({'points': (p1, p2), 'type': segmentType.line}, )
        segments += ({'points': (p2, p3), 'type': segmentType.line}, )
        pt = p5.rotateArroundPointCopy(cl.center, abs(p4.getRelativeSlope(cl.center) - p3.getRelativeSlope(cl.center)) / 2)
        segments += ({"points": (p3, pt, p4), "type": segmentType.arccircle},)
        pt = p5.rotateArroundPointCopy(ct.center, abs(p5.getRelativeSlope(ct.center) - p4.getRelativeSlope(ct.center)) / 2)
        segments += ({"points": (p4, pt, p5), "type": segmentType.arccircle},)
        pt = p6.rotateArroundPointCopy(cr.center, abs(p6.getRelativeSlope(cr.center) - p5.getRelativeSlope(cr.center)) / 2)
        segments += ({"points": (p5, pt, p6), "type": segmentType.arccircle},)
        segments += ({'points': (p6, p7), 'type': segmentType.line}, )
        segments += ({'points': (p7, p8), 'type': segmentType.line}, )
        segments += ({'points': (p8, p9), 'type': segmentType.line}, )
        pt = p9.rotateArroundPointCopy(c1.center, abs(p9.getRelativeSlope(c1.center) - p0.getRelativeSlope(c1.center)) / 2)
        segments += ({"points": (p9, pt, p0), "type": segmentType.arccircle},)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment['points']:
                points += (p.rotateCopy(-90 + (position + 0.5) * 360.0 / self.pocket.pole.rotor.poleNumber), )
            rsegments += ({'points': points, 'type': segment['type']}, )

        axialPointsTop = [
            point(-self.length / 2, innerDiameter / 2),
            point(self.length / 2, innerDiameter / 2),
            point(self.length / 2, outerDiameter / 2 - self.topAirgap),
            point(-self.length / 2, outerDiameter / 2 - self.topAirgap),
            point(-self.length / 2, innerDiameter / 2)
        ]

        axialPointsBottom = [
            point(-self.length / 2, -innerDiameter / 2),
            point(self.length / 2, -innerDiameter / 2),
            point(self.length / 2, -outerDiameter / 2 + self.topAirgap),
            point(-self.length / 2, -outerDiameter / 2 + self.topAirgap),
            point(-self.length / 2, -innerDiameter / 2)
        ]

        return {
            "polylineSegments": rsegments,
            "mainPoints": mainPoints,
            "radialPlotPoints": getPlotPoints(segments, self.pocket.pole.rotor.poleNumber),
            "axialPlotPoints": [axialPointsTop, axialPointsBottom]
        }

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Material" in data:
            self.material = magnet(data=data["Material"])
        if 'Height (mm)' in data:
            self.height = data['Height (mm)']
        if 'Embrace (%)' in data:
            self.embrace = data['Embrace (%)']
        if 'Front Angle (deg)' in data:
            self.frontAngle = data['Front Angle (deg)']
        if 'Back Angle (deg)' in data:
            self.backAngle = data['Back Angle (deg)']
        if "Edge Angle (deg)" in data:
            self.edgeAngle = data["Edge Angle (deg)"]
        if "Cut Side (mm)" in data:
            self.cutSide = data["Cut Side (mm)"]
        if "Top Airgap (mm)" in data:
            self.topAirgap = data["Top Airgap (mm)"]
        if "Edge Airgap (mm)" in data:
            self.edgeAirgap = data["Edge Airgap (mm)"]
        if "Offset (mm)" in data:
            self.offset = data["Offset (mm)"]
        if "Length (mm)" in data:
            self.length = data["Length (mm)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Material": self.material,
            "Height (mm)": self.height,
            "Embrace (%)": self.embrace,
            "Front Angle (deg)": self.frontAngle,
            "Back Angle (deg)": self.backAngle,
            "Edge Angle (deg)": self.edgeAngle,
            "Cut Side (mm)": self.cutSide,
            "Top Airgap (mm)": self.topAirgap,
            "Edge Airgap (mm)": self.edgeAirgap,
            "Offset (mm)": self.offset,
            "Length (mm)": self.length,
            # "Coordinates": self.getCoordinates()
        }

    def GetMagnetizationVector(self, position=0):
        """ Calculates the magnetization vector of the magent. """
        if self.pocket.type == pocketType.pocket1:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket2:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.angle / 2 - 90),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.angle / 2 - 90),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket3:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.angle / 2),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.angle / 2),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket4:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket5:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket6:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket7:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }
        if self.pocket.type == pocketType.pocket8:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }

    def getWidth(self):
        """Calculates the width of the magnet including the air-gapself."""
        return self.width + 2.0 * self.airgap

    def getHeight(self):
        """Calculates the height of the magnet including the air-gapself."""
        return self.height

    def setArea(self):
        """Calculates the area of the rotor in [mm2]."""
        self.area = self.pocket.pole.rotor.geometry.getMagnetArea()

    def getWeight(self):
        """Calculates weight of the magnet [kg]."""
        return self.getArea() * self.pocket.pole.rotor.stacklength * self.material.density * 1E-9
