
from utils import *
from .brushes import *
from ....enums import segmentType
from materials import *
from ....utilities.functions import getPlotPoints


class commutator(object):
    """This is a commutator class used for the DC machines."""

    def __init__(self, winding, data={}):
        self.material = {"Used": {"id": "init", "name": "init"},
                         "Options": [{"id": "init", "name": "init"}]}
        self.outerDiameter = 50.15
        self.innerDiameter = 24.7
        self.length = 5
        self.stackDistance = 10
        self.isolationThickness = 0.5
        self.displacementAngle = 15
        self.winding = winding
        self.numberOfBrushes = 2
        self.springPressure = 0
        self.brushes = brushes(winding=self.winding, commutator=self)
        if not data == {}:
            self.readJSON(data)

    @property
    def numberOfSegments(self):
        """Number of segments of the Commutator."""
        return self.winding.numberOfCoils

    @property
    def segmentAngle(self):
        """Commutator segment angle in deg."""
        return 360.0 / self.numberOfSegments

    def getWeight(self):
        """Calculates weight of the stator in [kg]."""
        pass

    def getCoordinates(self, position=0, axialPoints=True):
        """Calculates the coordinates of the housing."""
        p1tmp = point(0, self.innerDiameter / 2.0)
        p2tmp = point(0, self.outerDiameter / 2.0)
        p0 = p1tmp.rotateCopy(-self.segmentAngle / 2.0)
        p1 = p2tmp.rotateCopy(-self.segmentAngle / 2.0)
        p2 = p2tmp.rotateCopy(self.segmentAngle / 2.0)
        p3 = p1tmp.rotateCopy(self.segmentAngle / 2.0)

        mainPoints = (p0, p1, p2, p3)
        c = circle(self.outerDiameter / 2.0)
        c1 = circle(self.innerDiameter / 2.0)

        segments = ()
        segments += ({"points": (p0, p1), "type": segmentType.line},)
        pt = p1.rotateArroundPointCopy(c.center, self.segmentAngle / 2)
        segments += ({"points": (p1, pt, p2), "type": segmentType.arccircle},)
        segments += ({"points": (p2, p3), "type": segmentType.line},)
        pt = p3.rotateArroundPointCopy(c1.center, -self.segmentAngle / 2)
        segments += ({"points": (p3, pt, p0), "type": segmentType.arccircle},)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (p.rotateCopy(0 + self.displacementAngle +
                           (position + 0) * self.segmentAngle),)
            rsegments += ({"points": points, "type": segment["type"]},)

        topPoints = [
            point(-self.length - (self.stackDistance +
                  self.winding.stator.stacklength / 2), self.outerDiameter / 2),
            point(-self.length - (self.stackDistance +
                  self.winding.stator.stacklength / 2), self.innerDiameter / 2),
            point(-(self.stackDistance + self.winding.stator.stacklength / 2),
                  self.innerDiameter / 2),
            point(-(self.stackDistance + self.winding.stator.stacklength / 2),
                  self.outerDiameter / 2),
            point(-self.length - (self.stackDistance +
                  self.winding.stator.stacklength / 2), self.outerDiameter / 2),
        ]

        bottomPoints = [point(p.X, -p.Y) for p in topPoints]

        return {
            "layout": self.__getLayoutCoordinates(),
            "polylineSegments": rsegments,
            "mainPoints": mainPoints,
            "radialPlotPoints": getPlotPoints(rsegments, self.numberOfSegments),
            "axialPlotPoints": [topPoints, bottomPoints]
        }

    def __getLayoutCoordinates(self):
        output = []
        a = 360 / self.numberOfSegments
        b = self.length
        c = self.winding.rotor.segmentAngle
        scale = 0.95
        y0 = self.winding.layout.a / 2 + self.winding.layout.b + self.stackDistance
        x0 = -self.winding.layout.c / 2 + a / 2

        p0 = point(x0 - a / 2 * scale, -b / 2 - y0)
        p1 = point(x0 - a / 2 * scale, b / 2 - y0)
        p2 = point(x0 + a / 2 * scale, b / 2 - y0)
        p3 = point(x0 + a / 2 * scale, -b / 2 - y0)

        points = [p0, p1, p2, p3, p0]
        for i in range(self.numberOfSegments):
            output.append([point(p.X + i * a, p.Y) for p in points])

        return output

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Material" in data:
            pass
            self.material = collectorMat(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = data["Outer Diameter (mm)"]
        if "Inner Diameter (mm)" in data:
            self.innerDiameter = data["Inner Diameter (mm)"]
        if "Length (mm)" in data:
            self.length = data["Length (mm)"]
        if "Stack Distance (mm)" in data:
            self.stackDistance = data["Stack Distance (mm)"]
        if "Isolation Thickness (mm)" in data:
            self.isolationThickness = data["Isolation Thickness (mm)"]
        if "Displacement Angle (deg)" in data:
            self.displacementAngle = data["Displacement Angle (deg)"]
        if "Number of Brushes" in data:
            self.numberOfBrushes = data["Number of Brushes"]
        if "Brushes" in data:
            self.brushes = brushes(
                commutator=self, winding=self.winding, data=data["Brushes"])
        if "Contact Voltage Drop (V)" in data:
            self.contactVoltageDrop = data["Contact Voltage Drop (V)"]
        if "Spring Pressure (N/mm2)" in data:
            self.springPressure = data["Spring Pressure (N/mm2)"]

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Material": self.material,
            "Number Of Segments": self.numberOfSegments,
            "Outer Diameter (mm)": self.outerDiameter,
            "Inner Diameter (mm)": self.innerDiameter,
            "Length (mm)": self.length,
            "Stack Distance (mm)": self.stackDistance,
            "Isolation Thickness (mm)": self.isolationThickness,
            "Displacement Angle (deg)": self.displacementAngle,
            "Number of Brushes": self.numberOfBrushes,
            "Brushes": self.brushes,
            "Spring Pressure (N/mm2)": self.springPressure,
            "Contact Voltage Drop (V)": self.contactVoltageDrop,
        }
