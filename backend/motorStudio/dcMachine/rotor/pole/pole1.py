import math
from utils import *
from ..pocket import *
from ....enums import rotorType
from ....common.ring import *
from ....utilities.functions import getPlotPoints


class pole1(ring):

    def __init__(self, rotor, data={}):
        ring.__init__(self, data={})
        self.rotor = rotor
        self.symmetryNumber = rotor.poleNumber
        self.pockets = [pocket1(self)]

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        super(pole1, self).readJSON(data)

        if "Pockets" in data:
            if self.rotor.type == rotorType.rotor1:
                self.pockets = [pocket1(self, data["Pockets"][0])]

        self.innerDiameter = self.rotor.innerDiameter
        self.outerDiameter = self.rotor.innerDiameter + 2 * self.pockets[0].magnet.getHeight()

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Pockets": self.pockets,
            # 'Coordinates': self.getCoordinates(axialPoints=False)
        }
