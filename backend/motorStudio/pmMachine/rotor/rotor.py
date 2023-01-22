import json
from .pole import *
from utils import *
from materials import *
from ...enums import rotorType, magnetizationType
# from .geometry.geometry import geometry


class rotor(object):
    """This is a rotor class. It is used as a container for all other modules neccessary to define the contour of the rotor"""

    def __init__(self, rotortype=rotorType.rotor1, data={}):

        self.type = rotortype
        self.material = {
            "Used": {"id": "a230bb07-4473-4987-802c-cf94e75cd63e"}}
        self.poleNumber = 6
        self.outerDiameter = 23.5
        self.innerDiameter = 8
        self.magnetizationType = magnetizationType.diametral
        self.stacklength = 25
        self.stackingFactor = 0.95
        self.cuttingThickness = 0
        self.axialMisalignment = 0
        self.skewAngle = 0
        self.numberOfSkewSlices = 1
        self.pole = pole1(self)

        if not data == {}:
            self.readJSON(data)

        # self.geometry = geometry(rotor=self)

    @property
    def segmentAngle(self):
        """Depends on the slotNumber (deg)"""
        return 360.0 / self.poleNumber

    @property
    def volume(self):
        """Volume in mm3"""
        return self.area * self.stacklength

    def setArea(self):
        """Calculates the area of the rotor in [mm2]."""
        self.area = self.geometry.getRotorArea()

    def getWeight(self):
        """ Calculates weight of the rotor in [kg]. """
        return self.area * self.stacklength * self.material.density * 1E-9

    def getMagnetsWeight(self):
        """ Calculates weight of the magnets in [kg]. """
        weight_m = 0
        for pocket in self.pole.pockets:
            weight_m += pocket.magnet.getWeight()

        return weight_m * self.poleNumber

    def getMagnetizationVectors(self):

        vectors = []

        for position in range(self.poleNumber):
            for pocket in self.pole.pockets:
                if self.type == 12:
                    vectors.append(
                        pocket.magnet.GetMagnetizationVector_vRotor1(position))
                    vectors.append(
                        pocket.magnet.GetMagnetizationVector_vRotor2(position))
                else:
                    vectors.append(
                        pocket.magnet.GetMagnetizationVector(position))

        # print(vectors)
        return vectors

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
        if "Cutting Thickness (mm)" in data:
            self.cuttingThickness = data["Cutting Thickness (mm)"]
        if "Axial Misalignment (mm)" in data:
            self.axialMisalignment = data["Axial Misalignment (mm)"]
        if "Area (mm2)" in data:
            self.area = data["Area (mm2)"]
        if "Skew Angle (deg)" in data:
            self.skewAngle = data["Skew Angle (deg)"]
        if "Number of Skew Slices" in data:
            self.numberOfSkewSlices = data["Number of Skew Slices"]
        if "Pole" in data:
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
            "Cutting Thickness (mm)": self.cuttingThickness,
            "Axial Misalignment (mm)": self.axialMisalignment,
            "Segment Angle (deg)": self.segmentAngle,
            "Pole": self.pole,
            "Magnetization Vectors": self.getMagnetizationVectors(),
            "Area (mm2)": self.area,
            "Volume (mm3)": self.volume,
            "Skew Angle (deg)": self.skewAngle,
            "Number of Skew Slices": self.numberOfSkewSlices
        }
