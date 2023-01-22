import math
from utils import *
from ..magnet import *
from ....common.ring import *
from ....enums import rotorType, pocketType
from ....utilities.functions import getPlotPoints


class pocket1(ring):

    def __init__(self, pole, data={}):
        ring.__init__(self, data={})
        self.type = pocketType.pocket1
        self.pole = pole
        self.symmetryNumber = pole.symmetryNumber
        self.magnet = magnet1(self)

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        super(pocket1, self).readJSON(data)
        if 'Magnet' in data:
            if (self.pole.rotor.type == rotorType.rotor1):
                self.magnet = magnet1(self, data['Magnet'])

        self.innerDiameter = self.pole.rotor.innerDiameter
        self.outerDiameter = self.pole.rotor.innerDiameter + 2 * self.magnet.getHeight()

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            'Magnet': self.magnet,
            # 'Coordinates': self.getCoordinates()
        }
