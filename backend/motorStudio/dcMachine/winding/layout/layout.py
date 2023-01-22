import math
from ....enums import terminalType, terminalPosition, terminalDirection
from utils import *
from fractions import gcd
from ...terminal import *
D2R = 2 * math.pi / 360


class layout(object):
    """Layout class. It is used to calculate the winding layout of the machine"""

    def __init__(self,  winding):
        self.winding = winding
        self.rotor = self.winding.rotor
        self.stator = self.winding.stator
        self.numberOfHarmonics = self.stator.slotNumber
        self.numberOfSectors = self.winding.symmetryNumber

        # plot variables
        self.a = winding.stator.stacklength  # mm
        self.b = (winding.coilSpan - 1) * 5  # mm
        self.c = winding.coilSpanAngle  # deg mech
        self.d = self.c / (winding.coilSpan)  # deg mech

    @property
    def coils(self):
        """Assigns the connection table to terminal objects. Returns the tuple of coils. Each coil is a dictionary of two terminals (input and output)."""
        connectionTable = self.getConnectionTable()

        coils = ()
        if (self.winding.coil.terminalType == terminalType.leftright):
            # print("Pocetak ************************************************************")
            for coil in connectionTable['table']:
                terminal = {}
                if (coil['inPosition'] == terminalPosition.left):
                    terminal['input'] = terminalLeft(self.stator, self.winding, coil['coil'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalRight(self.stator, self.winding, coil['coil'], coil['outSlot'], terminalDirection.output)
                else:
                    terminal['input'] = terminalRight(self.stator, self.winding, coil['coil'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalLeft(self.stator, self.winding, coil['coil'], coil['outSlot'], terminalDirection.output)
                coils += (terminal, )

        elif (self.winding.coil.terminalType == terminalType.topbottom):
            # print("Pocetak ************************************************************")
            for coil in connectionTable['table']:
                terminal = {}
                if (coil['inPosition'] == terminalPosition.left):
                    terminal['input'] = terminalLeft(self.stator, self.winding, coil['coil'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalRight(self.stator, self.winding, coil['coil'], coil['outSlot'], terminalDirection.output)
                else:
                    terminal['input'] = terminalRight(self.stator, self.winding, coil['coil'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalLeft(self.stator, self.winding, coil['coil'], coil['outSlot'], terminalDirection.output)
                # print(terminal['input'].name, terminal['output'].name)
                coils += (terminal, )
        elif (self.winding.coil.terminalType == terminalType.single):
            pass
        else:
            print("Terminal type is not known!")
            return None
        # print("Kraj ************************************************************", len(coils))

        return coils

    def getConnectionTable(self):
        """Calculates the connection table of the dc machine winding."""

        positions = self.getReferenceCoilPositions()
        table = ()
        for k in range(int(self.winding.numberOfCoils)):
            raw = {}
            raw["Coil Number"] = k
            raw["coil"] = self.winding.coilLetters[k]
            raw["branch"] = self.winding.coilLetters[0] if k < self.winding.numberOfCoils // 2 else self.winding.coilLetters[1]
            raw["angle"] = positions[k]['angle']
            raw["inSlot"] = (positions[k]['inSlot'] + self.winding.frontPitch) % self.stator.slotNumber
            raw["outSlot"] = (positions[k]['outSlot'] + self.winding.frontPitch) % self.stator.slotNumber

            if (self.winding.coil.terminalType == terminalType.leftright):
                raw['inPosition'] = terminalPosition.bottom
                raw['outPosition'] = terminalPosition.top
            elif (self.winding.coil.terminalType == terminalType.single):
                raw['inPosition'] = terminalPosition.single
                raw['outPosition'] = terminalPosition.single
            else:
                raw['inPosition'] = None
                raw['outPosition'] = None

            table += (raw, )

        output = {}
        output['table'] = table
        output['wf'] = None
        return output

    def getReferenceCoilPositions(self):
        """
        Calculate possible positions for the coils. Used from the bldc machines. Maybe not neccessary.
        To get the positions of other phases the phase offset has to be used (dc machines offset is 1-slot).

        Reference table example (12 slot, 10 pole machine)::
            =======    ====    ====     ====    ====    ====    ====    ====    ====    ====   ====    ====    ====
            Coil       1       2        3       4       5       6       7       8       9      10      11      12
            -------    ----    ----     ----    ----    ----    ----    ----    ----    ----   ----    ----    ----
            Angle       0       -30      -60     90      60      30      0       -30    -60    90      60      30
            inSlot      1       3        3       4       6       6       8       8       10     10      11      1
            outSlot     2       2        4       5       5       7       7       9       9      11      12      12
            =======    ====    ====     ====    ====    ====    ====    ====    ====    ====   ====    ====    ====
        """

        table = ()
        for k in range(self.stator.slotNumber):
            angle = (k * float(self.rotor.poleNumber) / self.stator.slotNumber * 180.0 + 180.0) % 360.0 - 180.0
            inslot = k
            outslot = (k + self.winding.coilSpan) % self.stator.slotNumber
            table += ({"angle": angle, "inSlot": inslot, "outSlot": outslot}, )

        return table

    def __getLapWindingCoordinates(self):
        output, leftCoord, rightCoord = [], [], []
        p0 = point(-self.d / 2 if self.winding.coilSpan % 2 == 0 else 0, -self.a / 2 - self.b - 5)
        p1 = point(-self.d / 2 if self.winding.coilSpan % 2 == 0 else 0, -self.a / 2 - self.b)
        p2 = point(-self.c / 2, -self.a / 2)
        p3 = point(-self.c / 2, self.a / 2)
        p4 = point(0, self.a / 2 + self.b)
        p5 = point(-p3.X, p3.Y)
        p6 = point(-p2.X, p2.Y)
        p7 = point(p1.X + self.d, p1.Y)
        p8 = point(p0.X + self.d, p0.Y)

        leftCoord = [p0, p1, p2, p3, p4]
        rightCoord = [p4, p5, p6, p7, p8]

        for i in range(self.winding.numberOfCoils):
            output.append({
                "Left": [point(p.X + i * self.d, p.Y) for p in leftCoord],
                "Right": [point(p.X + (i - (self.winding.coilSpan - 1)) * self.d, p.Y) for p in rightCoord]
            })

        return output

    def __getWaveWindingCoordinates(self):
        pass

    def __getPoleCoordiates(self):
        output = []
        a = self.rotor.pole.pockets[0].magnet.poleAngle
        b = self.rotor.pole.pockets[0].magnet.length
        c = self.rotor.pole.pockets[0].magnet.segmentAngle
        p0 = point(-a / 2, -b / 2)
        p1 = point(-a / 2, b / 2)
        p2 = point(a / 2, b / 2)
        p3 = point(a / 2, -b / 2)

        points = [p0, p1, p2, p3, p0]
        for i in range(self.rotor.poleNumber):
            output.append([point(p.X + i * c, p.Y) for p in points])

        return output

    def __getSlotCoordiates(self):
        output = []
        x0 = -self.c / 2 + self.d / 2
        scale = 0.8
        p0 = point(x0 - self.d / 2 * scale, -self.a / 2)
        p1 = point(x0 - self.d / 2 * scale, self.a / 2)
        p2 = point(x0 + self.d / 2 * scale, self.a / 2)
        p3 = point(x0 + self.d / 2 * scale, -self.a / 2)

        points = [p0, p1, p2, p3, p0]
        for i in range(self.stator.slotNumber):
            output.append([point(p.X + i * self.d, p.Y) for p in points])

        return output

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            # "Coils": self.coils,
            "Connection Table": self.getConnectionTable(),
            # "Winding Scheme": {
            #     "Coils": self.__getLapWindingCoordinates(),
            #     "Slots": self.__getSlotCoordiates(),
            #     "Poles": self.__getPoleCoordiates(),
            # }
        }
