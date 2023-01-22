import math
from ...enums import *
from utils import *
from .terminal import terminal
from ...utilities.functions import getPlotPoints


class terminalRight(terminal):

    def __init__(self, stator, winding, phaseLetter='A', position=0, direction=enums.terminalDirection.input):
        terminal.__init__(self, stator, winding, phaseLetter, position, direction)

    def getCoordinates(self, position=0):
        p = self.stator.sector.slot.getCoordinates()['mainPoints']
        pc = point(0, p[3].Y + (p[2].Y - p[3].Y) * self.heightRatio)

        segments = ()
        if (self.stator.type == enums.statorType.stator1):
            l1 = line.__pointANDpoint__(p[1], p[2])
            l2 = line.__pointANDpoint__(p[2], p[3])
            l1.moveParallel(-self.winding.slotIsolation)
            l2.moveParallel(self.winding.slotIsolation)
            l4 = line.__pointANDpoint__(p[3], p[4])
            l4.moveParallel(self.winding.slotIsolation)
            l5 = line.__pointANDpoint__(p[len(p) - 3], p[len(p) - 4])
            l5.moveParallel(self.winding.slotIsolation)

            l6 = line.__slopeANDpoint__(self.windingAngle, point(0, 0))
            l6.moveParallelThroughPoint(pc)
            l6.moveParallel(-self.winding.slotIsolation / 2)

            l7 = line.__slopeANDpoint__(self.windingAngle, point(0, 0))
            l7.orthogonalThroughPoint(p[0])

            p0 = l2.lineIntersection(l6)
            p1 = l2.lineIntersection(l4)
            p2 = l4.lineIntersection(l5)
            p3 = l7.lineIntersection(l5)
            p4 = l7.lineIntersection(l6)

            mainPoints = (p0, p1, p2, p3, p4)
            segments += ({'points': (p0, p1), 'type': enums.segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': enums.segmentType.line}, )
            segments += ({'points': (p2, p3), 'type': enums.segmentType.line}, )
            segments += ({'points': (p3, p4), 'type': enums.segmentType.line}, )
            segments += ({'points': (p4, p0), 'type': enums.segmentType.line}, )

        rsegments = ()
        for segment in segments:
            points = ()
            for p in segment['points']:
                points += (p.rotateCopy(-90 + (position + 0.5) * 360 / self.stator.slotNumber), )
            rsegments += ({'points': points, 'type': segment['type']}, )

        plotPoints = getPlotPoints(segments)
        rPlotPoints = []
        for p in plotPoints:
            rPlotPoints.append(p.rotateCopy(-90 + (position + 0.5) * 360 / self.stator.slotNumber))

        return {
            'polylineSegments': rsegments,
            'mainPoints': mainPoints,
            "radialPlotPoints": rPlotPoints,
        }

    def getWireCoordinates(self, position=0):
        """Calculates the coordinates of the wires inside the right terminal."""
        t = self.getCoordinates()['mainPoints']
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l1 = line.__pointANDpoint__(t[2], t[3])
        l2 = line.__pointANDpoint__(t[2], t[1])
        l3 = line.__slopeANDpoint__(-360 / self.stator.slotNumber / 2, t[2])
        l1.moveParallel(a / 2)
        l2.moveParallel(a / 2)
        pc = l1.lineIntersection(l2)
        pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)
        output = (pc, )
        i, layers, newLayer = 0, 0, True
        while (pc.X > t[0].X):
            while (pc.Y < t[4].Y):
                pc = l1.movePoint(pc, ah)
                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(pc, -e * a / 2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)
                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (newLayer == True and len(output) <= self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires):
                        layers += 1
                        newLayer = False
            i += 1
            newLayer = True

            pc = l1.lineIntersection(l2)
            # pc = l1.movePoint(pc, ah * (-1 + 0.5 * (i % 2)))
            pc = l1.movePoint(pc, ah * (-5 + 0.5 * (i % 2)))
            pc = l3.movePoint(pc, i * h)
            pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (position + 0.5) * 360 / self.stator.slotNumber), )

        if self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires < len(output):
            coordinates = routput[:self.winding.coil.windingNumber * self.winding.coil.numberOfMultipleWires]
        else:
            coordinates = routput

        wires = []
        for c in coordinates:
            wire = []
            N = 10
            for i in range(N + 1):
                p0 = point(c.X + self.winding.coil.wire.gauge["Isolation Diameter (mm)"] / 2, c.Y)
                wire.append(p0.rotateArroundPointCopy(c, i * 360.0 / N))
            wires.append(wire)

        self.layers = layers

        return {
            'coordinates': coordinates,
            'allcoordinates': routput,
            'layers': layers,
            'contourPointsList': wires
        }
