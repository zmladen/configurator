import math
from materials import *


class wire:
    """
    The wire class. It holds the important parameters for the machine winding.

    :param dict data: JSON dictionary used for the object initialization. Default value is empty string.
    :ivar string conductorColor: Hex code of the conductor color.
    :ivar string isolationColor: Hex code of the isolation color.
    :ivar float conductorDiameter: Diameter of the current conducting wire (mm).
    :ivar float isolationDiameter: Diameter of the wire including the isolation thickness (mm). It is equal or larger than the conductorDiameter.
    """

    def __init__(self, data={}):

        self.conductorColor = "#e3cfaa"
        self.isolationColor = "#f55b1d"
        self.material = {"id": "0e042161-8b02-4a18-b316-1ba09cd988af"}
        self.isolationGrade = "Isolation Diameter G2 max (mm)"
        self.gauge = {
            "name": "0.950",
            "Conductor Diameter (mm)": 0.95,
            "Isolation Diameter (mm)": 1.041,
            "Isolation Diameter G1 min (mm)": 0.979,
            "Isolation Diameter G1 max (mm)": 1.017,
            "Isolation Diameter G2 min (mm)": 1.007,
            "Isolation Diameter G2 max (mm)": 1.041,
            "id": "27ee626f-6e19-48e1-9357-ed476c39d079",
        }

        if not data == {}:
            self.readJSON(data)

    @property
    def surface(self):
        """ Calculates the surface of the conducting wire (mm^2). """
        return math.pi * float(self.gauge["Conductor Diameter (mm)"]) ** 2 / 4.0

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Material" in data:
            self.material = metal(data=data["Material"])
        if "Gauge" in data:
            self.gauge = data["Gauge"]
        if "Isolation Grade" in data:
            self.isolationGrade = data["Isolation Grade"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Material": self.material,
            "Gauge": self.gauge,
            "Isolation Grade": self.isolationGrade,
        }
