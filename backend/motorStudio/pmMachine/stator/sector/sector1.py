import math
from utils import *
from ..slot import *
from ....enums import statorType, segmentType
from ....utilities.functions import getPlotPoints


class sector1(object):
    """Class that defines the countour of the sector mainly user for the so-called inner-runner drive."""

    def __init__(self, stator, data={}):
        self.color = "#6fcb9f"

        self.stator = stator
        self.segmentAngle = self.stator.segmentAngle
        self.slot = slot1(self)

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Slot" in data:
            self.slot = slot1(self, data["Slot"])

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Slot": self.slot,
            "Color": self.color,
            "Cutting Areas Color": "#bad0e3"
            # "Coordinates": self.getCoordinates()
        }
