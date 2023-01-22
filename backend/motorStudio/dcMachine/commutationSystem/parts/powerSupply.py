import math
import os
from utils import *


class powerSupply:
    """This is a simple power supply."""

    def __init__(self, data={}):
        self.voltage = 12
        self.resistance = 0
        self.temperature = 25

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Voltage (V)" in data:
            self.voltage = data["Voltage (V)"]
        if "Resistance (Ohm)" in data:
            self.resistance = data["Resistance (Ohm)"]

    def reprJSON(self):
        return {
            "Voltage (V)": self.voltage,
            "Resistance (Ohm)": self.resistance,
        }
