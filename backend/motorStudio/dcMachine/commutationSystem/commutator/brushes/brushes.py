import math
from utils import *
from materials import *
from .....enums import segmentType
from .....utilities.functions import getPlotPoints


class brushes(object):
    """This is a brushes class used for the DC machines."""

    def __init__(self, winding, commutator, data={}):

        self.id = "123"
        self.name = "brush"
        self.width = 2
        self.height = 5
        self.length = 10
        self.frictionCoefficient = 0
        self.temperature = 25
        self.commutator = commutator
        self.winding = winding
        self.resistance_ref = 0
        self.tc_resistance = -0.404
        self.data = data
        self.springPressure = 0  # Correct later

        if not data == {}:
            self.readJSON(data)

    def getCurrentDensity(self, Is):
        """Calculates the current density in A/mm2"""
        return Is / self.crossSectionSurface / (self.commutator.numberOfBrushes / 2)

    @property
    def resistance(self):
        return self.resistance_ref * (1 + self.tc_resistance / 100 * (self.temperature - 25))

    @property
    def crossSectionSurface(self):
        """mm2"""
        return self.width * self.height

    @property
    def equivalentResistance(self):
        if self.commutator.numberOfBrushes <= 2:
            return 2 * self.resistance
        else:
            # 4, 6, 8, ...
            return 2 * self.resistance / self.commutator.numberOfBrushes

    @property
    def segmentAngle(self):
        """ Calculates segment angle of the brushes in [deg]. """
        return 360.0 / self.commutator.numberOfBrushes

    def frictionLosses(self, speed):
        # Bosch - Kleinmotoren 2 (Seite 57)
        v = (2 * math.pi * speed / 60) * \
            self.commutator.outerDiameter / 2 / 1E3   # m/s
        Pbar = self.commutator.springPressure * \
            10                                            # bar
        # cm2
        Fges = (self.crossSectionSurface * 1E-2)

        return 9.81 * self.frictionCoefficient * Pbar * Fges * v  # W

    def getWeight(self):
        """ Calculates weight of the stator in [kg]. """
        pass

    def getCoordinates(self, position=0, axialPoints=True):
        """Calculates the coordinates of the brush."""

        c = circle(self.commutator.outerDiameter / 2.0)
        p0 = c.pointOnCircle(90 - c.getChordAngle(self.width) / 2)
        p1 = c.pointOnCircle(90 + c.getChordAngle(self.width) / 2)
        l0 = line.__slopeANDpoint__(90, p0)
        l1 = line.__slopeANDpoint__(90, p1)
        p2 = l1.movePoint(p1, self.height)
        p3 = l0.movePoint(p0, self.height)

        mainPoints = [p0, p1, p2, p3]
        segments = ()
        pt = p0.rotateArroundPointCopy(
            c.center, c.getChordAngle(self.width) / 2)
        segments += ({"points": (p0, pt, p1), "type": segmentType.arccircle},)
        segments += ({"points": (p1, p2), "type": segmentType.line},)
        segments += ({"points": (p2, p3), "type": segmentType.line},)
        segments += ({"points": (p3, p0), "type": segmentType.line},)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (p.rotateCopy((position + 0.5) * self.segmentAngle),)
            rsegments += ({"points": points, "type": segment["type"]},)

        topPoints = [
            point(-self.length / 2 - (self.commutator.stackDistance + self.commutator.length / 2 +
                  self.winding.stator.stacklength / 2), self.commutator.outerDiameter / 2 + self.height),
            point(-self.length / 2 - (self.commutator.stackDistance + self.commutator.length /
                  2 + self.winding.stator.stacklength / 2), self.commutator.outerDiameter / 2),
            point(self.length / 2 - (self.commutator.stackDistance + self.commutator.length /
                  2 + self.winding.stator.stacklength / 2), self.commutator.outerDiameter / 2),
            point(self.length / 2 - (self.commutator.stackDistance + self.commutator.length / 2 +
                  self.winding.stator.stacklength / 2), self.commutator.outerDiameter / 2 + self.height),
            point(-self.length / 2 - (self.commutator.stackDistance + self.commutator.length / 2 +
                  self.winding.stator.stacklength / 2), self.commutator.outerDiameter / 2 + self.height),
        ]

        bottomPoints = [point(p.X, -p.Y) for p in topPoints]

        return {
            "layout": self.__getLayoutCoordinates(),
            "polylineSegments": rsegments,
            "mainPoints": mainPoints,
            "radialPlotPoints": getPlotPoints(rsegments, self.commutator.numberOfBrushes),
            "axialPlotPoints": [topPoints, bottomPoints]
        }

    def __getLayoutCoordinates(self):
        output = []
        # circle chord
        a = 2 * math.asin(self.width /
                          self.commutator.outerDiameter) * 180 / math.pi
        b = self.length
        c = self.winding.rotor.segmentAngle
        scale = 0.95
        y0 = self.winding.layout.a / 2 + self.winding.layout.b + \
            self.commutator.stackDistance + self.commutator.length / 2 + b / 2

        p0 = point(-a / 2 * scale, -b / 2 - y0)
        p1 = point(-a / 2 * scale, b / 2 - y0)
        p2 = point(a / 2 * scale, b / 2 - y0)
        p3 = point(a / 2 * scale, -b / 2 - y0)

        points = [p0, p1, p2, p3, p0]
        for i in range(self.commutator.numberOfBrushes):
            output.append([point(p.X + i * c, p.Y) for p in points])

        return output

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        # print("In brush data")
        # print(data)
        if "id" in data["Used"]:
            self.id = data["Used"]["id"]
        if "name" in data["Used"]:
            self.type = data["Used"]["name"]
        if "Length (mm)" in data["Used"]:
            self.length = data["Used"]["Length (mm)"]
        if "Width (mm)" in data["Used"]:
            self.width = data["Used"]["Width (mm)"]
        if "Height (mm)" in data["Used"]:
            self.height = data["Used"]["Height (mm)"]
        if "Friction Coefficient" in data["Used"]:
            self.frictionCoefficient = data["Used"]["Friction Coefficient"]
        if "Resistance (Ohm)" in data["Used"]:
            self.resistance_ref = data["Used"]["Resistance (Ohm)"]
        if "Resistance Tc (%/C)" in data["Used"]:
            self.tc_resistance = data["Used"]["Resistance Tc (%/C)"]

    def reprJSON(self):
        return {
            "Used": {
                "id": self.id,
                "name": self.name,
                "Width (mm)": self.width,
                "Height (mm)": self.height,
                "Length (mm)": self.length,
                "Resistance (Ohm)": self.resistance,
                "Friction Coefficient": self.frictionCoefficient,
                "Equivalent Resistance (Ohm)": self.equivalentResistance,
            },
            "Options": self.data["Options"],
        }
