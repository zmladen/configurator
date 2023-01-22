import math
from utils import *
from materials import *
from ...enums import *
from ...utilities.functions import getPlotPoints
# from .geometry.geometry import geometry
import random
import string


class pie:
    """This is a shaft class. It is used to define simple pie-shape of the shaft. Using the pie-shape symmetry can be modeled easier and the drawing is much simpler."""

    def __init__(self, data={}, segmentNumber=3, partName="Shaft"):
        self.color = "#FFA700"
        self.segmentNumber = segmentNumber
        self.outerDiameter = 8
        self.length = 70
        self.partName = partName
        self.material = {"Used": {"id": "init", "name": "init"},
                         "Options": [{"id": "init", "name": "init"}]}

        if not data == {}:
            self.readJSON(data)

        # self.geometry = geometry(pie=self, partName=partName)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / float(self.segmentNumber)

    def closeDocument(self):
        FreeCAD.closeDocument(self.templateName)

    def getArea(self):
        """Calculates the area of the shaft in [mm2]."""
        return math.pi * self.outerDiameter ** 2 / 4.0

    def getWeight(self):
        """ Calculates weight of the ring in [kg]. """
        return self.getArea() * self.length * self.material.density * 1E-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = float(data["Outer Diameter (mm)"])
        if "Length (mm)" in data:
            self.length = float(data["Length (mm)"])

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Material": self.material,
            "Outer Diameter (mm)": self.outerDiameter,
            "Length (mm)": self.length,
            "Color": self.color,
            "Segment Number": self.segmentNumber,
            "Segment Angle (deg)": self.segmentAngle,
        }
