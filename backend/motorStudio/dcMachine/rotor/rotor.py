from utils import *
from materials import *
from .pole import *
from ...enums import rotorType, magnetizationType
from .geometry.geometry import geometry


class rotor(object):
    """This is a rotor class. It is used as a container for all other modules neccessary to define the contour of the rotor"""

    def __init__(self, rotortype=rotorType.rotor1, data={}):

        self.type = rotortype
        self.material = {"Used": {"id": "init", "name": "init"},
                         "Options": [{"id": "init", "name": "init"}]}
        self.poleNumber = 2
        self.outerDiameter = 23.5
        self.innerDiameter = 8
        self.magnetizationType = magnetizationType.radial
        self.stacklength = 25
        self.stackingFactor = 0.95
        self.pole = pole1(self)
        self.area = None

        # Maget segment
        if self.type == rotorType.rotor1:
            self.pole = pole1(self)

        if not data == {}:
            self.readJSON(data)

        # self.area = self.getArea()
        # self.geometry = geometry(rotor=self)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.poleNumber

    def setArea(self):
        """Calculates the area of the rotor in [mm2]. There is no rotor steel, only the magnet and the housing."""
        self.area = 0

    def getWeight(self):
        """ Calculates weight of the rotor in [kg]. """
        return self.getArea() * self.stacklength * self.material.density * 1E-9

    def getMagnetsWeight(self):
        """ Calculates weight of the magnets in [kg]. """
        weight_m = 0
        for pocket in self.pole.pockets:
            weight_m += pocket.magnet.getWeight()

        return weight_m * self.poleNumber

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Type" in data:
            self.type = data["Type"]
        if "Pole Number" in data:
            self.poleNumber = data["Pole Number"]
        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Outer Diameter (mm)" in data:
            self.outerDiameter = float(data["Outer Diameter (mm)"])
        if "Inner Diameter (mm)" in data:
            self.innerDiameter = float(data["Inner Diameter (mm)"])
        if "Magnetization Type" in data:
            self.magnetizationType = data["Magnetization Type"]
        if "Stack Length (mm)" in data:
            self.stacklength = float(data["Stack Length (mm)"])
        if "Area (mm2)" in data:
            self.area = data["Area (mm2)"]
        if "Pole" in data:
            if self.type == rotorType.rotor1:
                self.pole = pole1(self, data["Pole"])

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Type": self.type,
            "Pole Number": self.poleNumber,
            "Magnetization Type": self.magnetizationType,
            "Material": self.material,
            "Outer Diameter (mm)": self.outerDiameter,
            "Inner Diameter (mm)": self.innerDiameter,
            "Stack Length (mm)": self.stacklength,
            "Segment Angle (deg)": self.segmentAngle,
            "Pole": self.pole,
            "Area (mm2)": self.area,
            "Geometry": {
                # "DXF": self.geometry.getDXF(),
            }
        }
