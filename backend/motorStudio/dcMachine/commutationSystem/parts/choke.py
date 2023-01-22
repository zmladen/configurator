import math
import os
from utils import *


class choke:
    """This is a choke class."""

    def __init__(self, data={}):

        self.data = data
        self.name = "choke"
        self.type = ""
        self.resistance_ref = 0
        self.tc_resistance = -0.4041
        self.inductance = 0
        self.temperature = 25
        self.totalNumber = data.get("Total Number", 2)

        if not data == {}:
            self.readJSON(data["Used"])

    @property
    def resistance(self):
        return self.resistance_ref * (1 + self.tc_resistance / 100 * (self.temperature - 25))

    @property
    def equivalentResistance(self):
        # if self.totalNumber <= 2:
        #     return 2 * self.resistance
        # else:
        #     return 2 * self.resistance / self.totalNumber
        return self.totalNumber * self.resistance

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "id" in data:
            self.id = data["id"]
        if "type" in data:
            self.type = data["type"]
        if "name" in data:
            self.type = data["name"]
        if "Resistance (Ohm)" in data:
            self.resistance_ref = data["Resistance (Ohm)"]
        if "Resistance Tc (%/C)" in data:
            self.tc_resistance = data["Resistance Tc (%/C)"]
        if "Inductance (H)" in data:
            self.inductance = data["Inductance (H)"]

    def reprJSON(self):
        return {
            "Used": {
                "id": self.id,
                "name": self.name,
                "type": self.type,
                "Resistance (Ohm)": self.resistance_ref,
                "Inductance (H)": self.inductance,
                "Resistance Tc (%/C)": self.tc_resistance,

            },
            "Options": self.data["Options"],
            "Total Number": self.totalNumber,
            "Resistance (Ohm)": self.resistance,
            "Equivalent Resistance (Ohm)": self.equivalentResistance,
        }
