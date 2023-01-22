import math
import os


class mechanics:
    """This is a shaft class. It is used to define simple pie-shape of the shaft. Using the pie-shape symmetry can be modeled easier and the drawing is much simpler."""

    def __init__(self, data={}):
        self.damping = 0
        self.frictionTorque = 0.01
        self.momentOfInertia = 0

        if not data == {}:
            self.readJSON(data)

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Damping (Nm*s/rad)" in data:
            self.damping = data["Damping (Nm*s/rad)"]
        if "Friction Torque (Nm)" in data:
            self.frictionTorque = data["Friction Torque (Nm)"]
        if "Moment of Inertia (kg*m^2)" in data:
            self.momentOfInertia = data["Moment of Inertia (kg*m^2)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Damping (Nm*s/rad)": self.damping,
            "Friction Torque (Nm)": self.frictionTorque,
            "Moment of Inertia (kg*m^2)": self.momentOfInertia,
        }
