from ...enums import statorType
from .coil import coil
from .layout import *
import json
from utils import *


class winding(object):
    """The winding class. It holds the important parameters for the machine winding."""

    def __init__(self, stator, rotor, data={}, symmetryNumber=1):

        self.data = data
        self.phaseColors = {"A": "#D63118", "B": "#5BB83C", "C": "#418CFC", "D": "#0E3C56",
                            "E": "#FAE5AE", "F": "#ECE8DF", "G": "#A75240", "H": "#40A752", "I": "#5240A7"}
        self.phaseLetters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                             "L", "M", "N", "O", "P", "Q" "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
        self.phaseNumber = 3
        self.phaseSeparation = 2
        self.phaseConnection = {"name": "star",
                                "id": "6ef70fa6-cbf5-4450-b121-dfa1f41d0988"}
        self.coilConnection = {"name": "parallel",
                               "id": "7384b066-3929-403f-949b-f9f1a484350d"}
        self.symmetryNumber = symmetryNumber
        self.numberParallelCoils = 3
        self.slotIsolation = 0.5
        self.axialOverhang = 1
        self.customPhaseSeparation = False
        self.layers = 2
        self.coilSpan = 1
        self.stator = stator
        self.rotor = rotor
        self.coil = coil(self)
        self.layout = layout(self)
        self.estimatePhaseResistance = True
        self.estimatePhaseEndInductance = True
        self.Ld = None
        self.Lq = None
        self.ke = None
        self.measuredData = None
        self.phaseResistance = 1e-16
        self.phaseEndInductance = 1e-16
        self.cableResistance = 1e-16

        self.phaseResistanceScaleFactor = 1

        if not data == {}:
            self.readJSON(data)

    def getWireCoordinates(self):

        self.terminalLeftCoordinates = self.stator.geometry.getTerminalLeftCoordinates()
        self.terminalRightCoordinates = self.stator.geometry.getTerminalRightCoordinates()
        self.terminalSingleCoordinates = self.stator.geometry.getTerminalSingleCoordinates()

        (self.coil.wireLeftCoordinates, self.coil.wireLeftCoordinatesMax,
         self.coil.layers) = self.coil.getWireLeftCoordinates(self.terminalLeftCoordinates)
        (self.coil.wireRightCoordinates, self.coil.wireRightCoordinatesMax,
         self.coil.layers) = self.coil.getWireRightCoordinates(self.terminalRightCoordinates)

        if self.terminalSingleCoordinates != None:
            (self.coil.wireSingleCoordinates, self.coil.wireSingleCoordinatesMax,
             self.coil.layers) = self.coil.getSingleWireCoordinates(self.terminalSingleCoordinates)

    def getPhaseEndInductance(self):
        return 1e-15

    def getPhaseConnectionResistance(self):
        if self.stator.type == statorType.stator5:
            # Outer-Runner
            Lconn = math.pi * (self.stator.innerDiameter +
                               2 * self.stator.sector.slot.yokeThickness)
        else:
            # Inner-Runner
            Lconn = math.pi * self.stator.outerDiameter

        return 1.335 * (1e3 * self.coil.wire.material.resistivity) * Lconn / self.coil.wire.surface / 3 / self.coil.numberOfMultipleWires

    def getPhaseResistance(self):
        if self.coilConnection["name"] == "serial":
            return self.coil.resistance * self.coilsPerPhase + self.getPhaseConnectionResistance() + self.cableResistance
        else:
            return self.coil.resistance * self.coilsPerPhase / self.numberParallelCoils ** 2 + self.getPhaseConnectionResistance() + self.cableResistance

    def getPhaseResistanceForAddedLength(self, addedLength):
        # print("length", self.usedWindingNumber,  length, 2 * self.usedWindingNumber * (1e3 * self.wire.material.resistivity) * length / surface)

        print("addedLength", addedLength)

        print(self.coil.getResistance(addedLength) * self.coilsPerPhase)
        if self.coilConnection["name"] == "serial":
            return self.coil.getResistance(addedLength) * self.coilsPerPhase
        else:
            return self.coil.getResistance(addedLength) * self.coilsPerPhase / self.numberParallelCoils ** 2

    def getWeight(self):
        """ Calculates weight of the winding in [kg]. """
        return self.coil.wirelength * self.coil.wire.surface * self.stator.slotNumber * self.coil.wire.material.density * 1E-9

    @ property
    def numberOfCrossings(self):
        """Number of coil crossing on the axial side. 1 is added due to the fact that binding of the snop of wires cannot be ideal."""
        return max(1, self.coilSpan - 1)

    @property
    def terminalResistance(self):
        if self.phaseConnection["name"] == "delta":
            return 2.0 / 3.0 * self.getPhaseResistance()
        else:
            return 2.0 * self.getPhaseResistance()

    @property
    def coilsPerPhase(self):
        """ Calculates the number of coils per phase."""
        return self.stator.slotNumber / self.phaseNumber

    @property
    def polePitch(self):
        """Calculates the maximum pole pitch in number of slots."""
        return self.stator.slotNumber / self.rotor.poleNumber

    @property
    def phaseShift(self):
        """Calculates the phase shift in electrical degrees."""
        if self.phaseNumber == 2:
            return 180 / self.phaseNumber
        else:
            return 360 / self.phaseNumber

    @property
    def phaseOffset(self):
        """Calculates the phase offset in number of slots."""
        if self.phaseNumber > 1:
            for K0 in range(1, self.stator.slotNumber):
                if (K0 * 180 * self.rotor.poleNumber / self.stator.slotNumber % 360 == self.phaseShift):
                    if self.layers == 2:
                        return K0
                    else:
                        if K0 % 2:
                            return K0 + 1
                        return K0
        else:
            return None

    def getMaximumNumberOfParallelCoils(self):
        """Finds maximum number of coils that can be connected in parallel.
        The maximum number of parallel coils is equal to the summ of all coils
        in which the induced emf is in phase, i.e. has the same "angle" value.
        """
        table = self.layout.getConnectionTable()["table"]
        phaseA = [coil for coil in table if coil["phase"] == "A"]
        angle = phaseA[0]["angle"]

        count = 0
        for coil in phaseA:
            if coil["angle"] == angle:
                count += 1
        return count

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Phase Number" in data:
            self.phaseNumber = data["Phase Number"]
        if "Phase Connection" in data:
            self.phaseConnection = data["Phase Connection"]["Used"]
        if "Coil Connection" in data:
            self.coilConnection = data["Coil Connection"]["Used"]
        if "Parallel Coils" in data:
            self.numberParallelCoils = data["Parallel Coils"]
        if "Slot Isolation (mm)" in data:
            self.slotIsolation = data["Slot Isolation (mm)"]
        if "Axial Overhang (mm)" in data:
            self.axialOverhang = data["Axial Overhang (mm)"]
        if "Phase Separation (mm)" in data:
            self.phaseSeparation = data["Phase Separation (mm)"]
        if "Custom Phase Separation" in data:
            self.customPhaseSeparation = data["Custom Phase Separation"]
        if "Layers" in data:
            self.layers = data["Layers"]
        if "Coil Span (Teeth)" in data:
            self.coilSpan = data["Coil Span (Teeth)"]
        if "Coil" in data:
            self.coil = coil(self, data["Coil"])
        if "Phase Resistance (Ohm)" in data:
            self.phaseResistance = data["Phase Resistance (Ohm)"]
        if "Phase End-Inductance (H)" in data:
            self.phaseEndInductance = data["Phase End-Inductance (H)"]
        if "Cable Resistance (Ohm)" in data:
            self.cableResistance = data["Cable Resistance (Ohm)"]
        if "Phase Resistance Scale Factor (%)" in data:
            self.phaseResistanceScaleFactor = data[
                "Phase Resistance Scale Factor (%)"]
        if "Terminal Left Coordinates" in data:
            self.terminalLeftCoordinates = data["Terminal Left Coordinates"]
        if "Terminal Right Coordinates" in data:
            self.terminalRightCoordinates = data["Terminal Right Coordinates"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        # self.coilConnection
        if self.coilConnection["name"] == "serial":
            self.numberParallelCoils = 1

        return {
            "Phase Number": self.phaseNumber,
            "Parallel Coils": self.numberParallelCoils,
            "Max. Parallel Coils": self.getMaximumNumberOfParallelCoils(),
            "Slot Isolation (mm)": self.slotIsolation,
            "Axial Overhang (mm)": self.axialOverhang,
            "Phase Separation (mm)": self.phaseSeparation,
            "Custom Phase Separation": self.customPhaseSeparation,
            "Layers": self.layers,
            "Coil Span (Teeth)": self.coilSpan,
            "Coil": self.coil,
            "Layout": self.layout,
            "Phase Resistance (Ohm)": self.getPhaseResistance(),
            "Terminal Resistance (Ohm)": self.terminalResistance,
            "Phase End-Inductance (H)": self.getPhaseEndInductance(),
            "Cable Resistance (Ohm)": self.cableResistance,
            "Phase Letters": self.phaseLetters,
            "Phase Resistance Scale Factor (%)": self.phaseResistanceScaleFactor,
            "Phase Connection": {
                "Used": self.phaseConnection,
                "Options": self.data["Phase Connection"]["Options"]
            },
            "Coil Connection": {
                "Used": self.coilConnection,
                "Options": self.data["Coil Connection"]["Options"]
            },
            "Terminal Left Coordinates": self.terminalLeftCoordinates,
            "Terminal Right Coordinates": self.terminalRightCoordinates
        }
