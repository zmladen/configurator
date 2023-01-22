import math
from utils import *
from ..pocket import *
from ....enums import rotorType, segmentType, pocketType
from ....utilities.functions import getPlotPoints


class pole1(object):
    """Class that defines the countour of the pole for the so-called t-rotor and v-rotor."""

    def __init__(self, rotor, data={}):
        """ Constructor for the tooth object with needed parameters """
        self.color = "#008744"
        self.rotor = rotor
        self.contourRatio = 70
        self.poleSeparation = 0
        self.segmentAngle = rotor.segmentAngle
        self.pockets = [pocket1(self)]

        if not data == {}:
            self.readJSON(data)

    @property
    def area(self):
        """Calculates the area of the pole in [mm2]"""
        mainPoints = self.getCoordinates()["mainPoints"]
        a1 = areaPolygon(mainPoints)

        offset = self.rotor.outerDiameter / 2.0 * (1 - self.contourRatio / 100.0)
        c = circle(self.rotor.outerDiameter / 2.0 - offset, point(0, offset))
        angle = abs(mainPoints[2].getRelativeSlope(c.center) - mainPoints[3].getRelativeSlope(c.center))
        a2 = (c.radius ** 2 / 2.0 * (math.pi / 180.0 * angle - math.sin(angle * math.pi / 180.0)))

        c1 = circle(self.rotor.innerDiameter / 2.0)
        angle = abs(mainPoints[5].getRelativeSlope(c1.center) - mainPoints[0].getRelativeSlope(c1.center))
        a3 = (c1.radius ** 2 / 2.0 * (math.pi / 180.0 * angle - math.sin(angle * math.pi / 180.0)))

        return a1 + a2 - a3

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Contour Ratio (%)" in data:
            self.contourRatio = float(data["Contour Ratio (%)"])
        if "Pole Separation (mm)" in data:
            self.poleSeparation = data["Pole Separation (mm)"]
        if "Pockets" in data:
            self.pockets = [pocket1(self, data["Pockets"][0])]

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Contour Ratio (%)": self.contourRatio,
            "Pole Separation (mm)": self.poleSeparation,
            "Pockets": self.pockets,
            "Color": self.color,
            # "Coordinates": self.getCoordinates()
        }
