import math
from ...enums import statorType
from .sector import *
from .slot import *
from utils import *
from materials import *
from .geometry.geometry import geometry


class stator(object):
    """This is a stator class. It is used as a container for all other modules neccessary to define the contour of the stator"""

    def __init__(self, statortype=statorType.stator1, data={}):
        self.type = statortype
        self.material = {"Used": {"id": "init", "name": "init"},
                         "Options": [{"id": "init", "name": "init"}]}
        self.slotNumber = 12
        self.outerDiameter = 50.15
        self.innerDiameter = 24.7
        self.stacklength = 20
        self.stackingFactor = 0.95
        self.cuttingThickness = 0.1
        self.skewAngle = 0
        self.sector = sector1(self)
        self.area = None

        # Single Stator (Straight Back)
        if self.type == statorType.stator1:
            self.sector = sector1(self)

        if not data == {}:
            self.readJSON(data)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.slotNumber

    def setArea(self):
        """ Calculates the area of the stator in [mm2]. """
        self.area = (math.pi * (self.outerDiameter ** 2.0 / 4.0 - self.innerDiameter **
                     2.0 / 4.0) - float(self.slotNumber) * self.geometry.getSlotArea())

    def getWeight(self):
        """ Calculates weight of the stator in [kg]. """
        return self.getArea() * self.stacklength * self.material.density * 1E-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Type" in data:
            self.type = data["Type"]
        if "Slot Number" in data:
            self.slotNumber = data["Slot Number"]
        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = data["Outer Diameter (mm)"]
        if "Inner Diameter (mm)" in data:
            self.innerDiameter = data["Inner Diameter (mm)"]
        if "Stack Length (mm)" in data:
            self.stacklength = data["Stack Length (mm)"]
        if "Skew Angle (deg)" in data:
            self.skewAngle = data["Skew Angle (deg)"]
        if "Cutting Thickness (mm)" in data:
            self.cuttingThickness = data["Cutting Thickness (mm)"]
        if "Area (mm2)" in data:
            self.area = data["Area (mm2)"]
        if "Sector" in data:
            if self.type == statorType.stator1:
                self.sector = sector1(self, data["Sector"])

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Type": self.type,
            "Material": self.material,
            "Slot Number": self.slotNumber,
            "Outer Diameter (mm)": self.outerDiameter,
            "Inner Diameter (mm)": self.innerDiameter,
            "Stack Length (mm)": self.stacklength,
            "Skew Angle (deg)": self.skewAngle,
            "Segment Angle (deg)": self.segmentAngle,
            "Cutting Thickness (mm)": self.cuttingThickness,
            "Sector": self.sector,
            "Area (mm2)": self.area,
            # "Geometry": {
            #     "DXF": self.geometry.getDXF()
            # }
        }
