import json
import math
from materials import *
from utils import *
from ...enums import *
from ...utilities.functions import getPlotPoints
# from .geometry.geometry import geometry


class ring:
    """This is a housing1 class. It is used to define simple round hollow shape of the machine housing."""

    def __init__(self, data={}, segmentNumber=9, partName="Housing"):
        self.color = "#CC99C9"
        self.segmentNumber = segmentNumber
        self.outerDiameter = 52.8
        self.innerDiameter = 50.15
        self.length = 20
        self.useInModel = False
        self.material = {"Used": {"id": "init", "name": "init"},
                         "Options": [{"id": "init", "name": "init"}]}
        self.axialMisalignment = 0

        if not data == {}:
            self.readJSON(data)

        # self.geometry = geometry(ring=self, partName=partName)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.segmentNumber

    def getArea(self):
        """Calculates the area of the housing in [mm2]."""
        return math.pi * (self.outerDiameter ** 2.0 / 4.0 - self.innerDiameter ** 2.0 / 4.0)

    def getWeight(self):
        """ Calculates weight of the ring in [kg]. """
        return self.getArea() * self.length * self.material.density * 1E-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = float(data["Outer Diameter (mm)"])
        if "Inner Diameter (mm)" in data:
            self.innerDiameter = float(data["Inner Diameter (mm)"])
        if "Length (mm)" in data:
            self.length = float(data["Length (mm)"])
        if "Use In Model" in data:
            self.useInModel = float(data["Use In Model"])

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            'Material': self.material,
            'Outer Diameter (mm)': self.outerDiameter,
            'Inner Diameter (mm)': self.innerDiameter,
            'Length (mm)': self.length,
            "Color": self.color,
            "Segment Number": self.segmentNumber,
            "Segment Angle (deg)": self.segmentAngle,
            "Use In Model": self.useInModel,
        }
