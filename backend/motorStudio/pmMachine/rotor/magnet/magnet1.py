import math
from utils import *
from materials import *
from .. pocket import pocket1
from ....enums import pocketType, segmentType, rotorType
from ....utilities.functions import getPlotPoints


class magnet1:
    """Class that defines the block magnet shape."""

    def __init__(self, pocket, data={}):
        self.color = '#FEB144'
        self.height = 2.5
        self.width = 2.5
        self.airgap = 0.2
        self.embrace = 90
        self.contourRatio = 60
        self.heightReduction = 0
        self.pocket = pocket
        self.segmentAngle = pocket.segmentAngle
        self.material = {
            "Used": {"id": "a230bb07-4473-4987-802c-cf94e75cd63e"}}
        self.area = 0

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Material" in data:
            self.material = magnet(data=data["Material"])
        if 'Width (mm)' in data:
            self.width = data['Width (mm)']
        if 'Height (mm)' in data:
            self.height = data['Height (mm)']
        if 'Airgap (mm)' in data:
            self.airgap = data['Airgap (mm)']
        if 'Embrace (%)' in data:
            self.embrace = data['Embrace (%)']
        if 'Contour Ratio (%)' in data:
            self.contourRatio = data['Contour Ratio (%)']
        if "Height Reduction (%)" in data:
            self.heightReduction = data["Height Reduction (%)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            'Material': self.material,
            'Width (mm)': self.width,
            'Height (mm)': self.height,
            'Airgap (mm)': self.airgap,
            "Color": self.color,
            "Embrace (%)": self.embrace,
            "Height Reduction (%)": self.heightReduction,
            "Contour Ratio (%)": self.contourRatio,
            "Color": self.color,
            "Area (mm2)": self.area
            # 'Coordinates': self.getCoordinates(),
        }

    def GetMagnetizationVector_vRotor1(self, position=0):
        return {
            'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.magnetAngle / 2 - 90),
            'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.magnetAngle / 2 - 90),
        }

    def GetMagnetizationVector_vRotor2(self, position=0):

        return {
            'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.magnetAngle / 2),
            'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.magnetAngle / 2),
        }

    def GetMagnetizationVector(self, position=0):
        """Calculates the magnetization vector of the magent."""

        # t-rotor, s-rotor and b-rotor (IR and OR)
        if self.pocket.pole.rotor.type == 1 or self.pocket.pole.rotor.type == 11 or self.pocket.pole.rotor.type == 4 or self.pocket.pole.rotor.type == 5 or self.pocket.pole.rotor.type == 7 or self.pocket.pole.rotor.type == 8 or self.pocket.pole.rotor.type == 9 or self.pocket.pole.rotor.type == 10:
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

        # i-rotor
        if self.pocket.pole.rotor.type == 3:
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

        # v-rotor magnet 1
        if self.pocket.pole.rotor.type == -1:

            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.magnetAngle / 2 - 90),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(self.pocket.magnetAngle / 2 - 90),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }

        # v-rotor magnet 2
        if self.pocket.pole.rotor.type == -1:
            if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
                return {
                    'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.magnetAngle / 2),
                    'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle).rotateCopy(90 - self.pocket.magnetAngle / 2),
                }
            else:
                # lateral magnetization (global coordinate system)
                return {
                    'xVector': point(1, 0),
                    'yVector': point(0, 1)
                }

        # if self.pocket.type == pocketType.pocket6:
        #     if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
        #         return {
        #             'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
        #             'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
        #         }
        #     else:
        #         # lateral magnetization (global coordinate system)
        #         return {
        #             'xVector': point(1, 0),
        #             'yVector': point(0, 1)
        #         }
        # if self.pocket.type == pocketType.pocket7:
        #     if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
        #         return {
        #             'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
        #             'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
        #         }
        #     else:
        #         # lateral magnetization (global coordinate system)
        #         return {
        #             'xVector': point(1, 0),
        #             'yVector': point(0, 1)
        #         }
        # if self.pocket.type == pocketType.pocket8:
        #     if self.pocket.pole.rotor.magnetizationType == "diametral" or self.pocket.pole.rotor.magnetizationType == "radial":
        #         return {
        #             'xVector': point((-1)**position, 0).rotateCopy((position + 0.5) * self.segmentAngle),
        #             'yVector': point(0, (-1)**position).rotateCopy((position + 0.5) * self.segmentAngle),
        #         }
        #     else:
        #         # lateral magnetization (global coordinate system)
        #         return {
        #             'xVector': point(1, 0),
        #             'yVector': point(0, 1)
        #         }

    def getWidth(self):
        """Calculates the width of the magnet including the air-gapself."""
        return self.width + 2.0 * self.airgap

    def getHeight(self):
        """Calculates the height of the magnet including the air-gapself."""
        return self.height + 2.0 * self.airgap

    def setArea(self):
        """Calculates the area of the rotor in [mm2]."""
        self.area = self.pocket.pole.rotor.geometry.getMagnetArea()

    def getWeight(self):
        """Calculates weight of the magnet [kg]."""
        return self.area * self.pocket.pole.rotor.stacklength * self.material.density * 1E-9
