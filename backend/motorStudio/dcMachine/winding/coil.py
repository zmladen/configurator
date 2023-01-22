from utils import *
from .wire import wire
from ...enums import headType, terminalType


class coil:
    """
     DC machines have coils that do not have the same parameters. This class
     holds the functions for calculating the equivalent coil parameters needed for
     the calculation of the winding resistance, end-winding length, ...
    """

    def __init__(self, winding, data={}):
        self.winding = winding
        self.nestingFactor = data.get("Nesting Factor (%)", 100)
        self.wireStreching = data.get("Wire Streching (%)", 0)
        self.headType = data.get("Head Type", headType.round)
        self.terminalType = data.get("Terminal Type", terminalType.topbottom)
        self.numberOfMultipleWires = data.get("Number of Multiple Wires", 1)
        self.wire = wire(data["Wire"]) if data.get("Wire") else wire()
        self.windingNumber = data.get("Winding Number", 16)
        self.wireCoordinates = data.get("Wire Coordinates", None)
        self.wireCoordinatesMax = data.get("Wire Coordinates Max", None)
        self.totalNumberOfWindings = self.windingNumber * self.numberOfMultipleWires
        self.moveFirstWire = 0
        self.kov = 1.35  # overhang factor
        # self.slotCentroid = None
        self.layers = None

    @property
    def slotCentroid(self):
        height = self.winding.stator.sector.slot.yokeThickness + \
            (self.winding.stator.outerDiameter - (self.winding.stator.innerDiameter - self.winding.stator.sector.slot.yokeThickness * 2)) / \
            4
        return point(0, height)

    # def setSlotCentroid(self):
    #     self.slotCentroid = functions.getCentroid(
    #         self.winding.stator.geometry.getSlotCoordinates())

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
        return int(len(self.wireCoordinates) / 2 / self.numberOfMultipleWires)

    @property
    def maxWindingNumber(self):
        """Used number of windings."""
        return int(len(self.wireCoordinatesMax) / 2)

    @property
    def wirelength(self):
        """Calculates the length of the equivalent coil (mm)."""
        # p = self.winding.stator.sector.slot.getCoordinates()['mainPoints']
        # r = p[3].Y + (p[2].Y - p[3].Y) / 2
        r = self.slotCentroid.Y

        # Ellipse diameters. Axial height is devided by two because of the equivalent coil which is somewhere in the middle!
        e = ellipse(A=r * math.sin(360.0 / self.winding.numberOfCoils * self.winding.coilSpan /
                    2 * math.pi / 180), B=self.axialHeight / 2, center=point(0, 0))
        Lend = e.getPerimeter() / 2
        L = (self.winding.stator.stacklength + self.winding.axialOverhang) / \
            math.cos(self.winding.stator.skewAngle * math.pi / 180)
        totalLenght = 2 * (L + Lend) * self.usedWindingNumber * \
            self.numberOfMultipleWires

        # print(self.usedWindingNumber)
        return totalLenght

    @property
    def axialHeight(self):
        """Calculates the axial height of the equivalent coil (mm)."""
        # coil = self.winding.layout.coils[0]
        # layers1 = coil["input"].getWireCoordinates()["layers"]
        # layers2 = coil["output"].getWireCoordinates()["layers"]
        # dw = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        # return self.kov * dw * max(layers1, layers2) * (self.winding.coilSpan - 1)
        if self.layers and self.layers:
            dw = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
            return self.kov * dw * self.layers / 2 * (self.winding.coilSpan - 1)
        else:
            # In order to geometry to work.
            return self.winding.stator.outerDiameter / 2

    @property
    def resistance(self):
        """ Calculates the resistance of a coil (Ohm). """
        surface = self.wire.surface * \
            (1 - self.wireStreching / 100.0) * self.numberOfMultipleWires
        if surface != 0:
            # The length has to be devided by self.numberOfMultipleWires because the wire length
            return 1.0 * (1e3 * self.wire.material.resistivity) * (self.wirelength) / surface / self.numberOfMultipleWires
        else:
            return 1e15

    def getResistance(self, length):
        """ Calculates the resistance of a coil (Ohm). """
        surface = self.wire.surface * \
            (1 - self.wireStreching / 100.0) * self.numberOfMultipleWires
        if surface != 0:
            # The length has to be devided by self.numberOfMultipleWires because the wire length
            return 1.0 * (1e3 * self.wire.material.resistivity) * (self.wirelength) / surface / self.numberOfMultipleWires
        else:
            return 1e15

    def getCoordinates(self):
        c1 = point(-self.winding.stator.stacklength / 2,
                   self.winding.stator.innerDiameter / 2)
        e1 = ellipse(A=self.axialHeight, B=(
            self.winding.stator.outerDiameter - self.winding.stator.innerDiameter) / 2, center=c1)
        c2 = point(-self.winding.stator.stacklength / 2, -
                   self.winding.stator.innerDiameter / 2)
        e2 = ellipse(A=self.axialHeight, B=(
            self.winding.stator.outerDiameter - self.winding.stator.innerDiameter) / 2, center=c2)

        axialPointsTopLeft = [e1.pointOnEllipse2(angle) for angle in range(
            90, 181)] + [c1, e1.pointOnEllipse2(90)]
        axialPointsBottomLeft = [e2.pointOnEllipse2(angle) for angle in range(
            180, 271)] + [c2, e2.pointOnEllipse2(180)]
        axialPointsTopRight = [point(-p.X, p.Y) for p in axialPointsTopLeft]
        axialPointsBottomRight = [point(-p.X, p.Y)
                                  for p in axialPointsBottomLeft]

        return {
            "Wires Left": self.winding.layout.coils[0]["input"].getWireCoordinates(),
            "Wires Right": self.winding.layout.coils[0]["output"].getWireCoordinates(),
            "Axial Isolation": {"axialPlotPoints": [axialPointsTopLeft, axialPointsBottomLeft, axialPointsTopRight, axialPointsBottomRight]}
        }

    def getWireCoordinates(self, terminalCoordinates):
        """Calculates the coordinates of the wires inside the left terminal."""
        t = terminalCoordinates
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * \
            (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l0 = line.__slopeANDpoint__(90, t[0])
        l1 = line.__pointANDpoint__(t[1], t[2])
        l2 = line.__slopeANDpoint__(0, t[2])
        l3 = line.__pointANDpoint__(t[3], t[4])
        l4 = line.__pointANDpoint__(t[5], t[0])

        l1.moveParallel(a / 2)
        l2.moveParallel(a / 2)
        pc = l1.lineIntersection(l2)

        output = (pc, )
        i, layers, newLayer = 0, 0, True
        while ((pc.Y < t[0].Y)):
            # print(pc.Y, t[0].Y)
            while ((pc.X < t[4].X)):
                pc = l2.movePoint(pc, ah)
                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(
                    pc, -e * a / 2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)
                # output += (pc, )
                # print(pc)
                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    # if (newLayer == True and len(output) <= self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires):
                    if (newLayer == True and len(output) <= self.winding.coil.windingNumber):
                        layers += 1
                        newLayer = False

            i += 1
            newLayer = True
            pc = l1.lineIntersection(l2)
            pc = l2.movePoint(pc, ah * (-5 + 0.5 * (i % 2)))
            pc = l0.movePoint(pc, i * h)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (0.5) * 360 /
                        self.winding.stator.slotNumber), )

        # # self.layers = layers
        #
        # # print(len(output), self.windingNumber * 2 * self.numberOfMultipleWires, self.maxWindingNumber)
        # if self.windingNumber * 2 * self.numberOfMultipleWires < len(output):
        #     coordinates = routput[:self.windingNumber * 2 * self.numberOfMultipleWires]
        # else:
        #     coordinates = routput

        if self.winding.coil.totalNumberOfWindings * 2 < len(output):
            coordinates = routput[:self.totalNumberOfWindings * 2]
        else:
            coordinates = routput

        # self.layers = layers

        # return (coordinates, routput, layers)
        return ([{"x": p.X, "y": p.Y} for p in coordinates], [{"x": p.X, "y": p.Y} for p in routput], layers)

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Winding Number": self.usedWindingNumber,
            "Wire Surface (mm2)": self.usedWireSurface,
            "Total Number of Windings": self.totalNumberOfWindings,
            "Maximal Wire Surface (mm2)": self.maxWireSurface,
            "Maximal Winding Number": self.maxWindingNumber,
            "Number of Multiple Wires": self.numberOfMultipleWires,
            "Nesting Factor (%)": self.nestingFactor,
            "Wire Streching (%)": self.wireStreching,
            "Head Type": self.headType,
            "Terminal Type": self.terminalType,
            "Resistance (Ohm)": self.resistance,
            "Wire": self.wire,
            "Wire Coordinates": self.wireCoordinates,
            "Wire Coordinates Max": self.wireCoordinatesMax,
        }
