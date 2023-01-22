import os
import math
from scipy import interpolate
import numpy as np


class oilMat(object):
    """Oil class. Holds all important parameters and methods needed to characterize the oil material."""

    def __init__(self, temperature=25, data={}):
        """
        data = {"Used":{}, "Options":[]}
        """
        self.data = data
        self.temperature = temperature
        self.id = data.get("Used", {}).get("id", None)
        self.name = data.get("Used", {}).get("name", "Noname")
        self.__tempArray = data.get("Used", {}).get("Density", {}).get("Temperature (C)", [])
        self.__densityArray = data.get("Used", {}).get("Density", {}).get("Density (kg/m3)", [])
        self.__dynViscArray = data.get("Used", {}).get("Dynamic Viscosity", {}).get("Viscosity (mPas)", [])
        self.__kinVisArray = data.get("Used", {}).get("Kinematic Viscosity", {}).get("Viscosity (mm2/s)", [])

    @property
    def kinematicViscosity(self):
        f = interpolate.interp1d(self.__tempArray, self.__kinVisArray, kind='linear', fill_value="extrapolate")
        return f(self.temperature)

    def try1(self):
        return "Success"

    @property
    def dynamicViscosity(self):
        f = interpolate.interp1d(self.__tempArray, self.__dynViscArray, kind='linear', fill_value="extrapolate")
        return f(self.temperature)

    @property
    def density(self):
        f = interpolate.interp1d(self.__tempArray, self.__densityArray, kind='linear')
        return f(self.temperature)

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Used": self.data.get("Used", {}),
            "Options": self.data.get("Options", [])
        }
