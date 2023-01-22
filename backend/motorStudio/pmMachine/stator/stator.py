import math
import json
from .sector import *
from utils import *
from ...enums import statorType, segmentType
from materials import *
# from .geometry.geometry import geometry


class stator(object):
    """This is a stator class. It is used as a container for all other modules neccessary to define the contour of the stator"""

    def __init__(self, statortype=statorType.stator3, data={}):
        self.type = statortype
        self.material = {"id": "a230bb07-4473-4987-802c-cf94e75cd63e"}
        self.slotNumber = 9
        self.outerDiameter = 50.15
        self.innerDiameter = 24.7
        self.stacklength = 20
        self.stackingFactor = 0.95
        self.cuttingThickness = 0.1
        self.sector = sector1(self)

        if not data == {}:
            self.readJSON(data)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.slotNumber

    @property
    def volume(self):
        """Volume in mm3"""
        return self.area * self.stacklength

    def getToothLineCoordinates(self):
        """ Calculate the coordinates for the flux line. """
        segments = ()
        p1 = point(-self.sector.slot.toothThickness / 2.0, self.innerDiameter / 2 + (self.outerDiameter - self.innerDiameter) / 4)
        p2 = point(self.sector.slot.toothThickness / 2.0, self.innerDiameter / 2 + (self.outerDiameter - self.innerDiameter) / 4)
        segments += ({"points": (p1, p2), "type": segmentType.line},)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (p.rotateCopy(-90 + 360.0 / self.slotNumber),)
            rsegments += ({"points": points, "type": segment["type"]},)

        return {"polylineSegments": rsegments}

    def getYokeLineCoordinates(self):
        """ Calculate the coordinates for the flux line. """
        segments = ()
        p1 = point(0, self.outerDiameter / 2.0 - self.sector.slot.yokeThickness)
        p2 = point(0, self.outerDiameter / 2.0)

        if (self.type == statorType.stator5):
            p1 = point(0, self.innerDiameter / 2.0 + self.sector.slot.yokeThickness)
            p2 = point(0, self.innerDiameter / 2.0)

        segments += ({"points": (p1, p2), "type": segmentType.line},)

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment["points"]:
                points += (p.rotateCopy(-90 + 180.0 / self.slotNumber),)
            rsegments += ({"points": points, "type": segment["type"]},)

        return {"polylineSegments": rsegments}

    def setArea(self):
        """ Calculates the area of the stator in [mm2]. """
        self.area = (math.pi * (self.outerDiameter ** 2.0 / 4.0 - self.innerDiameter ** 2.0 / 4.0) - float(self.slotNumber) * self.geometry.getSlotArea())

    def getWeight(self):
        """ Calculates weight of the stator in [kg]. """
        return self.area * self.stacklength * self.material.density * 1E-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Type" in data:
            self.type = data["Type"]
        if "Slot Number" in data:
            self.slotNumber = data["Slot Number"]
        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = float(data["Outer Diameter (mm)"])
        if "Inner Diameter (mm)" in data:
            self.innerDiameter = float(data["Inner Diameter (mm)"])
        if "Stack Length (mm)" in data:
            self.stacklength = float(data["Stack Length (mm)"])
        if "Cutting Thickness (mm)" in data:
            self.cuttingThickness = data["Cutting Thickness (mm)"]
        if "Area (mm2)" in data:
            self.area = data["Area (mm2)"]
        if "Sector" in data:
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
            "Cutting Thickness (mm)": self.cuttingThickness,
            "Segment Angle (deg)": self.segmentAngle,
            "Sector": self.sector,
            "Tooth Line Coordinates": self.getToothLineCoordinates(),
            "Yoke Line Coordinates": self.getYokeLineCoordinates(),
            "Area (mm2)": self.area,
            "Volume (mm3)": self.volume
        }
