import math
from utils import *
from ..magnet import *
from ....enums import pocketType
from ....utilities.functions import getPlotPoints


class pocket1:
    """Class that defines the countour of the pocket for the so-called t-rotor."""

    def __init__(self, pole, data={}):
        self.type = pocketType.pocket1
        self.color = '#fff0f5'
        self.pole = pole
        self.embrace = 67
        self.cutTop = 0.5
        self.cutBottom = 0.5
        self.rib = 0.5
        self.bridgeCurved = 0.5
        self.moveInwards = 1
        self.segmentAngle = pole.segmentAngle
        self.magnet = magnet1(self)
        self.ribShaft = 1
        self.cut = 0.5
        self.bridgeClosing = 0.25
        self.ribMiddle = 0.5
        self.moveOutwards = 0.5
        self.magnetContactRatio = 90
        self.magnetAngle = 123

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if 'Embrace (%)' in data:
            self.embrace = data['Embrace (%)']
        if 'Cut Top (mm)' in data:
            self.cutTop = data['Cut Top (mm)']
        if 'Cut Bottom (mm)' in data:
            self.cutBottom = data['Cut Bottom (mm)']
        if 'Rib (mm)' in data:
            self.rib = data['Rib (mm)']
        if 'Bridge Curved (mm)' in data:
            self.bridgeCurved = data['Bridge Curved (mm)']
        if 'Move Inwards (mm)' in data:
            self.moveInwards = data['Move Inwards (mm)']
        if 'Rib Middle (mm)' in data:
            self.ribMiddle = data['Rib Middle (mm)']
        if 'Move Outwards (mm)' in data:
            self.moveOutwards = data['Move Outwards (mm)']
        if 'Cut (mm)' in data:
            self.cut = data['Cut (mm)']
        if 'Rib Shaft (mm)' in data:
            self.ribShaft = data['Rib Shaft (mm)']
        if 'Bridge Closing (mm)' in data:
            self.bridgeClosing = data['Bridge Closing (mm)']
        if 'Magnet' in data:
            self.magnet = magnet1(self, data['Magnet'])
        if "Magnet Contact Ratio (%)" in data:
            self.magnetContactRatio = data["Magnet Contact Ratio (%)"]
        if "Magnet Angle (deg)" in data:
            self.magnetAngle = data["Magnet Angle (deg)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            'Type': self.type,
            'Embrace (%)': self.embrace,
            'Cut Top (mm)': self.cutTop,
            'Cut Bottom (mm)': self.cutBottom,
            'Rib (mm)': self.rib,
            'Bridge Curved (mm)': self.bridgeCurved,
            'Move Inwards (mm)': self.moveInwards,
            'Magnet': self.magnet,
            "Color": self.color,
            "Type": self.type,
            "Cut (mm)": self.cut,
            "Rib Shaft (mm)": self.ribShaft,
            "Bridge Curved (mm)": self.bridgeCurved,
            "Bridge Closing (mm)": self.bridgeClosing,
            "Move Inwards (mm)": self.moveInwards,
            "Rib Middle (mm)": self.ribMiddle,
            "Move Outwards (mm)": self.moveOutwards,
            "Magnet Contact Ratio (%)": self.magnetContactRatio,
            "Magnet Angle (deg)": self.magnetAngle
        }

    @property
    def area(self):
        """Calculates the area of the pocket in [mm2]"""
        mainPoints = self.getCoordinates()['mainPoints']
        return areaPolygon(mainPoints)
