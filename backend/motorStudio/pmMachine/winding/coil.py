from numpy import mat
from ...enums import headType, terminalType
from utils import *
from .wire import wire
import json
import math


class coil:

    def __init__(self, winding, data={}):
        self.winding = winding
        self.windingNumber = data.get("Winding Number", 12)
        self.moveFirstWire = data.get("Move First Wire (mm)", 0)
        self.nestingFactor = data.get("Nesting Factor (%)", 100)
        self.wireStreching = data.get("Wire Streching (%)", 0)
        self.headType = data.get("Head Type", headType.round)
        self.terminalType = data.get("Terminal Type", terminalType.leftright)
        self.numberOfMultipleWires = data.get("Number of Multiple Wires", 1)
        self.wireLeftCoordinates = data.get("Wire Left Coordinates", None)
        self.wireLeftCoordinatesMax = data.get(
            "Wire Left Coordinates Max", None)
        self.wireRightCoordinates = data.get("Wire Left Coordinates", None)
        self.wireRightCoordinatesMax = data.get(
            "Wire Left Coordinates Max", None)
        self.wireSingleCoordinates = data.get("Wire Single Coordinates", None)
        self.wireSingleCoordinatesMax = data.get(
            "Wire Single Coordinates Max", None)
        self.layers = data.get("Layers", None)
        self.wire = wire(data["Wire"]) if data.get("Wire") else wire()
        self.totalNumberOfWindings = self.windingNumber * self.numberOfMultipleWires

        # self.layers = None
        # self.wireLeftCoordinates = None
        # self.wireLeftCoordinatesMax = None

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            "Winding Number": self.usedWindingNumber,
            "Maximal Winding Number": self.maxWindingNumber,
            "Number of Multiple Wires": self.numberOfMultipleWires,
            "Move First Wire (mm)": self.moveFirstWire,
            "Nesting Factor (%)": self.nestingFactor,
            "Wire Streching (%)": self.wireStreching,
            "Head Type": self.headType,
            "Terminal Type": self.terminalType,
            "Axial Height (mm)": self.axialHeight,
            "Wire Length (mm)": self.wirelength,
            "Resistance (Ohm)": self.resistance,
            "Wire": self.wire,
            "Wire Left Coordinates": self.wireLeftCoordinates,
            "Wire Right Coordinates": self.wireRightCoordinates,
            "Wire Single Coordinates": self.wireSingleCoordinates,
            "Wire Left Coordinates Max": self.wireLeftCoordinatesMax,
            "Wire Right Coordinates Max": self.wireRightCoordinatesMax,
            "Wire Single Coordinates Max": self.wireSingleCoordinatesMax,
            "Layers": self.layers,
            "Wire Surface (mm2)": self.usedWireSurface,
            "Maximal Wire Surface (mm2)": self.maxWireSurface,
            "Total Number of Windings": self.totalNumberOfWindings,
        }

    @property
    def numberOfCoils(self):
        """Integer"""
        return self.winding.stator.slotNumber / self.winding.phaseNumber

    @property
    def usedWireSurface(self):
        """in mm2"""
        surface = 0
        for i in range(self.usedWindingNumber * 2):
            surface += self.wire.surface
        return surface * self.numberOfMultipleWires

    @property
    def maxWireSurface(self):
        """in mm2"""
        surface = 0
        for i in range(self.maxWindingNumber * 2):
            surface += self.wire.surface
        return surface * self.numberOfMultipleWires

    @property
    def usedWindingNumber(self):
        """Used number of windings."""

        if self.winding.coilSpan == 1:
            return int(len(self.wireLeftCoordinates) / self.numberOfMultipleWires)
        else:
            return int(len(self.wireSingleCoordinates) / self.numberOfMultipleWires / 2)

    @property
    def maxWindingNumber(self):
        """Used number of windings."""
        if self.winding.coilSpan == 1:
            return len(self.wireLeftCoordinatesMax)
        else:
            return int(len(self.wireSingleCoordinatesMax)/2)

    @property
    def wirelength(self):
        """Calculates the length of a wire of a coil (mm)."""
        if self.winding.coilSpan == 1:
            # angle = abs(getCentroidDict(self.wireLeftCoordinates).getSlope(
            # ) - getCentroidDict(self.wireRightCoordinates).getSlope())

            angle = self.winding.stator.segmentAngle + \
                abs(getCentroidDict(self.wireRightCoordinates).getSlope()) - \
                abs(getCentroidDict(self.wireLeftCoordinates).getSlope())

            radius = point(0, 0).distance(
                getCentroidDict(self.wireLeftCoordinates))

            d = angle * math.pi / 180.0 * radius
            if self.headType == headType.round:
                # axial length of the equivalent coil
                laxial = 2.0 * (self.winding.stator.stacklength +
                                self.winding.axialOverhang)
                # end-winding length of the equivalent coil
                lend = d * math.pi
                return self.usedWindingNumber * (laxial + lend) * self.numberOfMultipleWires
            elif self.headType == headType.straight:
                # axial length of the equivalent coil
                laxial = 2.0 * (self.winding.stator.stacklength +
                                self.winding.axialOverhang)
                # end-winding length of the equivalent coil
                lend = 2.0 * d
                return self.usedWindingNumber * (laxial + lend) * self.numberOfMultipleWires
        else:
            laxial = 2.0 * (self.winding.stator.stacklength +
                            self.winding.axialOverhang+self.axialHeight/3)

            radius = point(0, 0).distance(
                getCentroidDict(self.wireSingleCoordinates))

            angle = (360 / self.winding.stator.slotNumber) * \
                self.winding.coilSpan
            d = angle * math.pi / 180.0 * radius

            lend = 2.0 * d

            return self.usedWindingNumber * (laxial + lend) * self.numberOfMultipleWires

    @ property
    def axialHeight(self):
        """Calculates the axial height of the resulting coil (mm)."""
        return self.wire.gauge["Isolation Diameter (mm)"] * self.layers * self.winding.numberOfCrossings

    @ property
    def resistance(self):
        """ Calculates the resistance of a coil (Ohm). """
        surface = self.wire.surface * \
            (1 - self.wireStreching / 100.0) * self.numberOfMultipleWires
        if surface != 0:
            return 1.04 * (1e3 * self.wire.material.resistivity) * self.wirelength / surface / self.numberOfMultipleWires
        else:
            return 1e15

    def getResistance(self, length):
        """ Calculates the resistance of a coil for a given length (Ohm). """

        # Due to multiple wires
        length = length * self.numberOfMultipleWires

        surface = self.wire.surface * \
            (1 - self.wireStreching / 100.0) * self.numberOfMultipleWires
        if surface != 0:
            return 2 * self.usedWindingNumber * (1e3 * self.wire.material.resistivity) * length / surface / self.numberOfMultipleWires
        else:
            return 1e15

    def getWireLeftCoordinates(self, terminalCoordinates):
        """
        Calculates the coordinates of the wires inside the left terminal.

        :param int position: Position of the slot. Used to rotate the coordinates to the corresponding position.
        :return: dictionary: {'coordinates' : (p0, p1, p2, ..., pn), 'layers', n}
        """
        t = terminalCoordinates
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * \
            (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l1 = line.__pointANDpoint__(t[1], t[2])
        l2 = line.__pointANDpoint__(t[1], t[0])
        l3 = line.__slopeANDpoint__(
            360 / self.winding.stator.slotNumber / 2, t[2])
        l1.moveParallel(a / 2)
        l2.moveParallel(-a / 2)
        pc = l1.lineIntersection(l2)
        # pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)
        output = (pc, )
        layers = 1
        i = 0
        newLayer = True
        while (pc.X < -self.winding.phaseSeparation / 2):
            while (pc.Y > (self.winding.stator.innerDiameter - self.winding.stator.sector.slot.yokeThickness - self.winding.slotIsolation) / 2):
                pc = l1.movePoint(pc, -ah)

                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(
                    pc, -e * a / 2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)

                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (newLayer == True and len(output) <= self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires):
                        layers += 1
                        newLayer = False
                else:
                    if (pc.Y < l1.lineIntersection(l2).Y):
                        newLayer = True
                        break
            i += 1
            pc = l1.lineIntersection(l2)
            pc = l1.movePoint(pc, ah * (1 + 0.5 * (i % 2)))
            pc = l3.movePoint(pc, i * h)
            # pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (0 + 0.5) * 360 /
                        self.winding.stator.slotNumber), )

        if self.winding.coil.totalNumberOfWindings < len(output):
            coordinates = routput[:self.winding.coil.totalNumberOfWindings]
        else:
            coordinates = routput

        self.layers = layers

        # return (coordinates, routput, layers)
        return ([{"x": p.X, "y": p.Y} for p in coordinates], [{"x": p.X, "y": p.Y} for p in routput], layers)

    def getWireRightCoordinates(self, terminalCoordinates):
        """
        Calculates the coordinates of the wires inside the left terminal.

        :param int position: Position of the slot. Used to rotate the coordinates to the corresponding position.
        :return: dictionary: {'coordinates' : (p0, p1, p2, ..., pn), 'layers', n}
        """
        t = terminalCoordinates
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * \
            (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l1 = line.__pointANDpoint__(t[1], t[2])
        l2 = line.__pointANDpoint__(t[1], t[0])
        l3 = line.__slopeANDpoint__(-360 /
                                    self.winding.stator.slotNumber / 2, t[2])
        l1.moveParallel(a / 2)
        l2.moveParallel(-a / 2)
        pc = l1.lineIntersection(l2)
        # pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)
        output = (pc, )
        layers = 1
        i = 0
        newLayer = True
        while (pc.X > self.winding.phaseSeparation / 2):
            while (pc.Y > (self.winding.stator.innerDiameter - self.winding.stator.sector.slot.yokeThickness - self.winding.slotIsolation) / 2):
                pc = l1.movePoint(pc, -ah)
                # output += (pc, )

                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(
                    pc, -e * a / 2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)

                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (newLayer == True and len(output) <= self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires):
                        layers += 1
                        newLayer = False
                else:
                    if (pc.Y < l1.lineIntersection(l2).Y):
                        newLayer = True
                        break
            i += 1
            pc = l1.lineIntersection(l2)
            pc = l1.movePoint(pc, ah * (1 + 0.5 * (i % 2)))
            pc = l3.movePoint(pc, i * h)
            # pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (0 + 0.5) * 360 /
                        self.winding.stator.slotNumber), )

        if self.winding.coil.totalNumberOfWindings < len(output):
            coordinates = routput[:self.winding.coil.totalNumberOfWindings]
        else:
            coordinates = routput

        self.layers = layers

        # return (coordinates, routput, layers)
        return ([{"x": p.X, "y": p.Y} for p in coordinates], [{"x": p.X, "y": p.Y} for p in routput], layers)

    def getSingleWireCoordinates(self, terminalCoordinates):
        """Calculates the coordinates of the wires inside the left terminal."""
        t = terminalCoordinates
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * \
            (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l0 = line.__slopeANDpoint__(90, t[0])
        l1 = line.__pointANDpoint__(t[0], t[1])
        l2 = line.__pointANDpoint__(t[1], t[2])
        # l3 = line.__pointANDpoint__(t[3], t[4])
        l4 = line.__pointANDpoint__(t[5], t[6])
        l3 = line.__slopeANDpoint__(
            360 / self.winding.stator.slotNumber / 2, t[1])
        l1.moveParallel(a / 2)
        l2.moveParallel(-a / 2)
        pc = l1.lineIntersection(l2)

        output = (pc, )
        i, layers, newLayer = 0, 0, True
        while ((pc.X < t[4].X)):
            while ((pc.Y > t[0].Y)):
                pc = l1.movePoint(pc, -ah)
                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(
                    pc, -e * a / 2), l2.movePoint(pc, e * a / 2), l2.movePoint(pc, -e * a / 2)
                # output += (pc, )
                # print(pc)
                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (newLayer == True and int(len(output) / 2) <= self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires):
                        layers += 1
                        newLayer = False
            i += 1
            newLayer = True

            pc = l1.lineIntersection(l2)
            pc = l1.movePoint(pc, ah * (5 + 0.5 * (i % 2)))
            pc = l2.movePoint(pc, i * h)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (0.5) * 360 /
                        self.winding.stator.slotNumber), )

        if self.winding.coil.totalNumberOfWindings * 2 < len(output):
            coordinates = routput[:self.totalNumberOfWindings * 2]
        else:
            coordinates = routput

        # self.layers = layers

        # return (coordinates, routput, layers)
        return ([{"x": p.X, "y": p.Y} for p in coordinates], [{"x": p.X, "y": p.Y} for p in routput], layers)

    def getCoordinates(self):
        axialPointsLeftTop = [
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, self.winding.stator.outerDiameter / 2),
            point(-self.winding.stator.stacklength / 2,
                  self.winding.stator.outerDiameter / 2),
            point(-self.winding.stator.stacklength / 2,
                  self.winding.stator.innerDiameter / 2),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, self.winding.stator.innerDiameter / 2),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight,
                  self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang,
                  self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang,
                  self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight,
                  self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, self.winding.stator.outerDiameter / 2),

        ]
        axialPointsLeftBottom = [
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, -(self.winding.stator.outerDiameter / 2)),
            point(-self.winding.stator.stacklength / 2, -
                  (self.winding.stator.outerDiameter / 2)),
            point(-self.winding.stator.stacklength / 2, -
                  (self.winding.stator.innerDiameter / 2)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, -(self.winding.stator.innerDiameter / 2)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight, -
                  (self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang, -
                  (self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang, -
                  (self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight,  -
                  (self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness)),
            point(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight, -(self.winding.stator.outerDiameter / 2))
        ]
        axialPointsRightTop = [
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), self.winding.stator.outerDiameter / 2),
            point(-(-self.winding.stator.stacklength / 2),
                  self.winding.stator.outerDiameter / 2),
            point(-(-self.winding.stator.stacklength / 2),
                  self.winding.stator.innerDiameter / 2),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), self.winding.stator.innerDiameter / 2),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight),
                  self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang),
                  self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang),
                  self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight),
                  self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), self.winding.stator.outerDiameter / 2),

        ]
        axialPointsRightBottom = [
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), -(self.winding.stator.outerDiameter / 2)),
            point(-(-self.winding.stator.stacklength / 2), -
                  (self.winding.stator.outerDiameter / 2)),
            point(-(-self.winding.stator.stacklength / 2), -
                  (self.winding.stator.innerDiameter / 2)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), -(self.winding.stator.innerDiameter / 2)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight), -
                  (self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang), -
                  (self.winding.stator.innerDiameter / 2 + self.winding.stator.sector.slot.tipHeight)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang), -
                  (self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang - self.axialHeight),  -
                  (self.winding.stator.outerDiameter / 2 - self.winding.stator.sector.slot.yokeThickness)),
            point(-(-self.winding.stator.stacklength / 2 - self.winding.axialOverhang -
                  self.axialHeight), -(self.winding.stator.outerDiameter / 2))
        ]

        return {
            # "Wires Left": self.winding.layout.coils[0]["input"].getWireCoordinates(),
            # "Wires Right": self.winding.layout.coils[0]["output"].getWireCoordinates(),
            # "Axial Isolation": {"axialPlotPoints": [axialPointsLeftTop, axialPointsLeftBottom, axialPointsRightTop, axialPointsRightBottom]}
        }
