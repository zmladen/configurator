from .coil import coil
from .layout import *
from utils import *
# from .geometry.geometry import geometry


class winding(object):
    """The winding class. It holds the important parameters for the machine winding."""

    def __init__(self, stator, rotor, data={}, symmetryNumber=1):
        """
        numberOfCoils - for 2 layer simplex winding is equal to the number of slots
        frontPitch (yc) -  lap winding +-x, wave winding (C+x)/p or (C-x)/p
        layers and plex number influence the number of collector segments
        """
        self.data = data
        self.coilLetters = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K",
                            "L", "M", "N", "O", "P", "Q" "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
        self.symmetryNumber = symmetryNumber
        self.coilConnection = {"Options": [{"name": "lap", "id": "7384b066-3929-403f-949b-f9f1a484350d"}], "Used": {
            "name": "lap", "id": "7384b066-3929-403f-949b-f9f1a484350d"}}
        self.slotIsolation = 0.5
        self.axialOverhang = 1
        self.numberOfLayers = {"Options": [2], "Used": 2}
        self.plexNumber = {"Options": [1], "Used": 1}
        self.coilSpan = 5
        self.frontPitch = 1
        self.stator = stator
        self.rotor = rotor
        self.coil = coil(self)
        self.layout = layout(self)
        self.estimatePhaseResistance = True
        self.estimatePhaseEndInductance = True
        self.phaseResistance = 1e-16
        self.phaseEndInductance = 1e-16
        self.parallelPaths = 2

        if not data == {}:
            self.readJSON(data)

        # self.geometry = geometry(winding=self)
        # self.terminalCoordinates = self.geometry.getTerminalCoordinates()
        # (self.coil.wireCoordinates, self.coil.wireCoordinatesMax, self.coil.layers) = self.coil.getWireCoordinates(self.terminalCoordinates)

        # self.coil.wireCoordinates = self.coil.getWireCoordinates(self.terminalCoordinates)[0]

        # self.terminalLeftCoordinates = terminalCoordinates[0]
        # self.terminalRightCoordinates = terminalCoordinates[1]
        # leftWireCoordinates = self.coil.getLeftWireCoordinates(self.terminalLeftCoordinates)
        # rightWireCoordinates = self.coil.getRightWireCoordinates(self.terminalRightCoordinates)
        #
        # self.coil.leftWireCoordinates = leftWireCoordinates[0]
        # self.coil.rightWireCoordinates = rightWireCoordinates[0]
        # self.coil.leftWireCoordinatesMax = leftWireCoordinates[1]
        # self.coil.rightWireCoordinatesMax = rightWireCoordinates[1]
        # self.coil.leftWireNumberOfLayers = leftWireCoordinates[2]
        # self.coil.rightWireNumberOfLayers = rightWireCoordinates[2]

    def getWireCoordinates(self):
        self.terminalCoordinates = self.stator.geometry.getTerminalCoordinates()
        (self.coil.wireCoordinates, self.coil.wireCoordinatesMax,
         self.coil.layers) = self.coil.getWireCoordinates(self.terminalCoordinates)

    @property
    def numberOfCoils(self):
        """Calculates the maximum pole pitch in number of slots."""
        return int(self.stator.slotNumber * self.plexNumber["Used"] * self.numberOfLayers["Used"] / 2)

    @property
    def polePitch(self):
        """Calculates the maximum pole pitch in number of slots."""
        return self.stator.slotNumber / self.rotor.poleNumber

    @property
    def coilSpanAngle(self):
        """Calculates the angle of the coil span in deg."""
        return 360.0 / self.stator.slotNumber * self.coilSpan

    @property
    def wirelength(self):
        """Calculates the length of a wire of a winding (mm)."""
        return self.coil.wirelength * self.numberOfCoils

    @property
    def axialHeight(self):
        """Calculates the length of a wire of a winding (mm)."""
        return self.coil.axialHeight

    @property
    def armatureResistance(self):
        # N - number of coils in one branch. If N is odd one branch has one coils more. The branches are connected in parallel.
        N = int(self.numberOfCoils / self.parallelPaths)
        if self.numberOfCoils % self.parallelPaths == 0:
            R = self.coil.resistance * N
            return (R ** self.parallelPaths) / (R * self.parallelPaths)

        else:
            R = self.coil.resistance * N
            Ra = self.coil.resistance * (N + 1)
            return (R ** (self.parallelPaths - 1)) * Ra / (R * (self.parallelPaths - 1) + Ra)

    def getArmatureResistanceForAddedLength(self, addedLength):
        # N - number of coils in one branch. If N is odd one branch has one coils more. The branches are connected in parallel.
        if addedLength == 0:
            return 0

        N = int(self.numberOfCoils / self.parallelPaths)
        if self.numberOfCoils % self.parallelPaths == 0:
            R = self.coil.getResistance(addedLength) * N
            return (R ** self.parallelPaths) / (R * self.parallelPaths)

        else:
            R = self.coil.getResistance(addedLength) * N
            Ra = self.coil.getResistance(addedLength) * (N + 1)
            return (R ** (self.parallelPaths - 1)) * Ra / (R * (self.parallelPaths - 1) + Ra)

    def getPhaseEndInductance(self):
        return 1e-15

    def getWeight(self):
        """ Calculates weight of the winding in [kg]. """
        return self.numberOfCoils * self.coil.wirelength * self.coil.wire.surface * self.coil.wire.material.density * 1E-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """

        if "Coil Connection" in data:
            self.coilConnection = data["Coil Connection"]
        if "Slot Isolation (mm)" in data:
            self.slotIsolation = data["Slot Isolation (mm)"]
        if "Axial Overhang (mm)" in data:
            self.axialOverhang = data["Axial Overhang (mm)"]
        if "Number Of Layers" in data:
            self.numberOfLayers = data["Number Of Layers"]
        if "Plex Number" in data:
            self.plexNumber = data["Plex Number"]
        if "Front Pitch" in data:
            self.frontPitch = data["Front Pitch"]
        if "Coil Span" in data:
            self.coilSpan = data["Coil Span"]
        if "Coil" in data:
            self.coil = coil(self, data["Coil"])
        if "Phase End-Inductance (H)" in data:
            self.phaseEndInductance = data["Phase End-Inductance (H)"]
        if "Winding Angle (deg)" in data:
            self.windingAngle = data["Winding Angle (deg)"]
        if "Height Ratio (%)" in data:
            self.heightRatio = data["Height Ratio (%)"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Slot Isolation (mm)": self.slotIsolation,
            "Axial Overhang (mm)": self.axialOverhang,
            "Front Pitch": self.frontPitch,
            "Coil Span": self.coilSpan,
            "Coil": self.coil,
            "Layout": self.layout,
            "Front Pitch": self.frontPitch,
            "Number of Coils": self.numberOfCoils,
            "Axial Height (mm)": self.axialHeight,
            "Wire Length (mm)": self.wirelength,
            "Armature Resistance (Ohm)": self.armatureResistance,
            "Coil Letters": self.coilLetters,
            "Coil Connection": {
                "Used": self.coilConnection["Used"],
                "Options": self.coilConnection["Options"],
            },
            "Plex Number": {
                "Used": self.plexNumber["Used"],
                "Options": self.plexNumber["Options"]
            },
            "Number Of Layers": {
                "Used": self.numberOfLayers["Used"],
                "Options": self.numberOfLayers["Options"]
            },
        }
