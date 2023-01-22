import math
import os
from utils import *


class connectionUnit:
    """This is a connection unit class."""

    def __init__(self, data={}):

        self.type = "pcb"
        self.resistance_ref = 0
        self.tc_resistance = -0.4041
        self.temperature = 25

        if not data == {}:
            self.readJSON(data)

    @property
    def resistance(self):
        return self.resistance_ref * (1 + self.tc_resistance / 100 * (self.temperature - 25))

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "type" in data:
            self.type = data["type"]
        if "Resistance (Ohm)" in data:
            self.resistance_ref = data["Resistance (Ohm)"]
        if "Resistance Tc (%/C)" in data:
            self.tc_resistance = data["Resistance Tc (%/C)"]

    def reprJSON(self):
        return {
            "type": self.type,
            "Resistance (Ohm)": self.resistance_ref,
            "Resistance Tc (%/C)": self.tc_resistance,
        }
