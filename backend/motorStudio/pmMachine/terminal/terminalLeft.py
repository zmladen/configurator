import math
from utils import *
from .terminal import terminal
from ...enums import statorType, segmentType, terminalDirection
from ...utilities.functions import getPlotPoints


class terminalLeft(terminal):

    def __init__(self, stator, winding, phaseLetter='A', position=0, direction=terminalDirection.input):
        terminal.__init__(self, stator, winding, phaseLetter, position, direction)

    def getCoordinates(self, position=0):
        p = self.stator.sector.slot.getCoordinates()['mainPoints']
        l1 = line.__pointANDpoint__(p[1], p[2])
        l2 = line.__pointANDpoint__(p[2], p[3])
        l1.moveParallel(self.winding.slotIsolation)
        l2.moveParallel(self.winding.slotIsolation)
        l3 = line.__slopeANDpoint__(90, point(-self.winding.phaseSeparation / 2.0, 0))
        l4 = line.__pointANDpoint__(p[3], p[4])
        l4.moveParallel(-self.winding.slotIsolation)

        segments = ()
        if (self.stator.type == statorType.stator1):
            c = circle(self.stator.outerDiameter / 2.0 - self.stator.sector.slot.yokeThickness - self.winding.slotIsolation)
            p0 = l1.lineIntersection(l3)
            p1 = l1.lineIntersection(l2)
            p2 = c.lineIntersection(l2)[0]
            p3 = c.lineIntersection(l3)[0]
            mainPoints = (p0, p1, p2, p3)
            segments += ({'points': (p0, p1), 'type': segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': segmentType.line}, )
            pt = p2.rotateArroundPointCopy(c.center, -abs(p2.getRelativeSlope(c.center) - p3.getRelativeSlope(c.center)) / 2.0)
            segments += ({'points': (p2, pt, p3), 'type': segmentType.arccircle}, )
            segments += ({'points': (p3, p0), 'type': segmentType.line}, )

        elif(self.stator.type == statorType.stator2 or self.stator.type == statorType.stator3 or self.stator.type == statorType.stator6):
            c = circle(self.stator.outerDiameter / 2.0 - self.stator.sector.slot.yokeThickness - self.winding.slotIsolation)
            p0 = l1.lineIntersection(l3)
            p1 = l1.lineIntersection(l2)
            p2 = l4.lineIntersection(l2)
            p3 = c.lineIntersection(l4)[0]
            p4 = c.lineIntersection(l3)[0]

            if p3.X >= p4.X:
                p3 = l3.lineIntersection(l4)
                p4 = l3.lineIntersection(l4)

            mainPoints = (p0, p1, p2, p3, p4)
            segments += ({'points': (p0, p1), 'type': segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': segmentType.line}, )
            segments += ({'points': (p2, p3), 'type': segmentType.line}, )
            segments += ({'points': (p3, p4), 'type': segmentType.line}, )
            segments += ({'points': (p4, p0), 'type': segmentType.line}, )
        elif (self.stator.type == statorType.stator4):
            c = circle(self.stator.sector.slot.slotDiameter / 2.0 - self.winding.slotIsolation, point(0, self.stator.outerDiameter / 2.0 - self.stator.sector.slot.yokeThickness - self.stator.sector.slot.slotDiameter / 2))
            p0 = l1.lineIntersection(l3)
            p1 = l1.lineIntersection(l2)
            p2 = c.lineIntersection(l2)[0]
            p3 = c.lineIntersection(l3)[0]
            mainPoints = (p0, p1, p2, p3)
            segments += ({'points': (p0, p1), 'type': segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': segmentType.line}, )
            pt = p2.rotateArroundPointCopy(
                c.center, -abs(p2.getRelativeSlope(c.center) - p3.getRelativeSlope(c.center)) / 2.0)
            segments += ({'points': (p2, pt, p3), 'type': segmentType.arccircle}, )
            segments += ({'points': (p3, p0), 'type': segmentType.line}, )
        elif(self.stator.type == statorType.stator5):
            l1 = line.__pointANDpoint__(p[1], p[2])
            l2 = line.__pointANDpoint__(p[2], p[3])
            l1.moveParallel(-self.winding.slotIsolation)
            l2.moveParallel(self.winding.slotIsolation)
            l3 = line.__slopeANDpoint__(90, point(-self.winding.phaseSeparation / 2.0, 0))
            l4 = line.__pointANDpoint__(p[3], p[4])
            l4.moveParallel(self.winding.slotIsolation)
            l5 = line.__slopeANDpoint__(0, p[1])
            l5.moveParallel(-self.winding.slotIsolation)

            p0 = l1.lineIntersection(l3)
            p1 = l1.lineIntersection(l2)
            p2 = l4.lineIntersection(l2)
            p3 = l4.lineIntersection(l3)
            p4 = l5.lineIntersection(l3)

            if p0.Y >= p4.Y:
                p0 = l1.lineIntersection(l5)

            mainPoints = (p3, p2, p1, p0)
            segments += ({'points': (p0, p1), 'type': segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': segmentType.line}, )
            segments += ({'points': (p2, p3), 'type': segmentType.line}, )
            segments += ({'points': (p3, p4), 'type': segmentType.line}, )
            segments += ({'points': (p4, p0), 'type': segmentType.line}, )
        elif(self.stator.type == statorType.stator7):
            c = circle(self.stator.outerDiameter / 2.0 - self.stator.sector.slot.yokeThickness - self.winding.slotIsolation)
            l1 = line.__pointANDpoint__(p[1], p[2])
            l2 = line.__pointANDpoint__(p[2], p[3])
            l1.moveParallel(self.winding.slotIsolation)
            l2.moveParallel(self.winding.slotIsolation)
            l3 = line.__slopeANDpoint__(90, point(-self.winding.phaseSeparation / 2.0, 0))
            l4 = line.__pointANDpoint__(p[6], p[7])
            l4.moveParallel(-self.winding.slotIsolation)

            p0 = l1.lineIntersection(l3)
            p1 = l1.lineIntersection(l2)
            p2 = l4.lineIntersection(l2)
            p3 = c.lineIntersection(l4)[0]
            p4 = c.lineIntersection(l3)[0]

            mainPoints = (p0, p1, p2, p3, p4)
            segments += ({'points': (p0, p1), 'type': segmentType.line}, )
            segments += ({'points': (p1, p2), 'type': segmentType.line}, )
            segments += ({'points': (p2, p3), 'type': segmentType.line}, )
            segments += ({'points': (p3, p4), 'type': segmentType.line}, )
            segments += ({'points': (p4, p0), 'type': segmentType.line}, )

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
        """
        Calculates the coordinates of the wires inside the left terminal.

        :param int position: Position of the slot. Used to rotate the coordinates to the corresponding position.
        :return: dictionary: {'coordinates' : (p0, p1, p2, ..., pn), 'layers', n}
        """
        t = self.getCoordinates()['mainPoints']
        a = self.winding.coil.wire.gauge["Isolation Diameter (mm)"]
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        # Add initial wire
        l1 = line.__pointANDpoint__(t[1], t[2])
        l2 = line.__pointANDpoint__(t[2], t[3])
        l3 = line.__slopeANDpoint__(360 / self.stator.slotNumber / 2, t[1])
        l1.moveParallel(a / 2)
        l2.moveParallel(-a / 2)
        pc = l1.lineIntersection(l2)
        pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)
        output = (pc, )
        layers = 0
        i = 0
        newLayer = True
        while (pc.X < -self.winding.phaseSeparation / 2):
            while (pc.Y > (self.stator.innerDiameter - self.stator.sector.slot.yokeThickness - self.winding.slotIsolation) / 2):
                pc = l1.movePoint(pc, -ah)

                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(pc, -e * a /
                                                                           2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)

                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (newLayer == True and len(output) < self.winding.coil.windingNumber):
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
            pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)

        routput = ()
        for p in output:
            routput += (p.rotateCopy(-90 + (position + 0.5) * 360 / self.stator.slotNumber), )

        if self.winding.coil.windingNumber < len(output):
            coordinates = routput[:self.winding.coil.windingNumber]
        else:
            coordinates = routput

        wires = []
        for c in coordinates:
            wire = []
            N = 15
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
