import os
import math


class collectorMat(object):
    """Collector class. Holds all important parameters and methods needed to characterize the collector material."""

    def __init__(self, data={}, temperature=25):

        self.data = data
        self.temperature = temperature
        self.density = 0
        self.conductivity_ref = 1
        self.tc_sigma = 0
        self.__tempRef = 25
        self.name = "noname"

        if not data == {}:
            self.readJSON(data)

        self.infoName = self.name

    @property
    def resistivity(self):
        """ Calculates electrical resistivity of the magnet at ambient temperature. """
        try:
            return (1.0 / self.conductivity_ref) * (1 - (self.tc_sigma / 100.0) * (self.temperature - self.__tempRef))
        except:
            return 1e12

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        data = data["Used"]

        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "Density (kg/m3)" in data:
            self.density = data["Density (kg/m3)"]
        if "Electrical Resistivity (Ohm*m)" in data:
            self.conductivity_ref = 1.0 / data["Electrical Resistivity (Ohm*m)"]
        if "Tc Conductivity (%/C)" in data:
            self.tc_sigma = data["Tc Conductivity (%/C)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Used": {
                "id": self.id,
                "name": self.name,
                "Density (kg/m3)": self.density,
                "Electrical Resistivity (Ohm*m)": 1.0 / self.conductivity_ref,
                "Tc Conductivity (%/C)": self.tc_sigma,
            },
            "Options": self.data["Options"]
        }
