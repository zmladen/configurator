import math
import os
from .commutator import *
from .parts import *
from utils import *


class commutationSystem:
    """This is a commutation system class."""

    def __init__(self, data={}, winding={}):
        self.color = "#FFA700"
        self.winding = winding
        self.commutator = commutator(
            self.winding, data=data.get("Commutator", {}))
        self.cable = cable(data=data.get("Cable", {}))
        self.powerSupply = powerSupply(data=data.get("Power Supply", {}))
        self.connectionUnit = connectionUnit(
            data=data.get("Connection Unit", {}))
        self.choke = choke(data=data.get("Choke", {}))
        self.temperature = data.get("Temperature (C)", 25)
        self.svg = None

        self.applyTemperature(self.temperature)

        self.choke.totalNumber = self.commutator.numberOfBrushes

    @property
    def totalResistance(self):
        return self.powerSupply.resistance + 2 * self.cable.resistance + self.choke.equivalentResistance + self.connectionUnit.resistance + self.commutator.brushes.equivalentResistance

    def applyTemperature(self, temperature=25):
        """Applies the ambient temperature to all parts."""
        self.commutator.temperature = temperature
        self.commutator.brushes.temperature = temperature
        self.cable.temperature = temperature
        self.powerSupply.temperature = temperature
        self.connectionUnit.temperature = temperature
        self.choke.temperature = temperature

    def getLosses(self, speed, Is, Im):
        # Is is the source current
        return {
            "Total Losses (W)": self.Psource(Is) + self.PconnectionUnit(Im) + self.Pchoke(Im) + self.Pcable(Im) + self.Pbrushes(speed, Im),
            "Source Resistance Losses (W)": self.Psource(Is),
            "Connection Unit Losses (W)": self.PconnectionUnit(Im),
            "Choke Losses (W)": self.Pchoke(Im),
            "Cable Losses (W)": self.Pcable(Im),
            "Brushes Losses (W)": self.Pbrushes(speed, Im)
        }

    def Psource(self, Is):
        return self.powerSupply.resistance * Is**2

    def PconnectionUnit(self, Is):
        return 2 * self.connectionUnit.resistance * Is**2

    def Pchoke(self, Is):
        return self.choke.equivalentResistance * Is**2

    def Pcable(self, Is):
        return 2 * self.cable.resistance * Is**2

    def Pbrushes(self, speed, Is):
        return self.commutator.brushes.equivalentResistance * Is**2 + 2 * self.commutator.contactVoltageDrop * Is + self.commutator.brushes.frictionLosses(speed)

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Power Supply": self.powerSupply,
            "Cable": self.cable,
            "Commutator": self.commutator,
            "Connection Unit": self.connectionUnit,
            "Choke": self.choke,
            "Temperature (C)": self.temperature,
            "Total Resistance (Ohm)": self.totalResistance
        }
