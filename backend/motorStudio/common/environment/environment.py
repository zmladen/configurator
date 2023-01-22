import math
import os


class environment:
    """This is a shaft class. It is used to define simple pie-shape of the shaft. Using the pie-shape symmetry can be modeled easier and the drawing is much simpler."""

    def __init__(self, data={}):
        self.ambientTemperature = 25

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Ambient Temperature (C)" in data:
            self.ambientTemperature = data["Ambient Temperature (C)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Ambient Temperature (C)": self.ambientTemperature,
        }
