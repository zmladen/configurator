import math
from utilities.point import point
from utilities.line import line
from utilities.circle import circle

class terminalTop:
    """ Top terminal object. """

    def __init__(self, stator, winding):
        """ Constructor for the top terminal object. """
        self.stator = stator
        self.winding = winding

    def getCoordinates(self):
        """ Calculates the coordinates for the top terminal """
        p = self.stator.slot.getCoordinates()[1]
        l1 = line.__slopeANDpoint__(0, point(0, self.stator.innerDiameter / 2 + (self.stator.outerDiameter / 2 - self.stator.tooth.yokeThickness - p[1].Y) / 2))
        l2 = line.__pointANDpoint__(p[2], p[3])
        l3 = line.__pointANDpoint__(p[len(p) - 3], p[len(p) - 4])
        l1.moveParallel(self.winding.phaseSeparation / 2)
        l2.moveParallel(self.winding.slotIsolation)
        l3.moveParallel(self.winding.slotIsolation)
        c = circle(self.stator.outerDiameter / 2 - self.stator.tooth.yokeThickness - self.winding.slotIsolation)
        p0 = l1.lineIntersection(l2)
        p1 = c.lineIntersection(l2)[0]
        p2 = c.lineIntersection(l3)[0]
        p3 = l1.lineIntersection(l3)
        mainPoints = (p0, p1, p2, p3)

        allPoints = (p0, p1)
        if (type(self.stator).__name__ == 'stator1'):
            """ rounds the back of the terminal """
            spreadAngle = abs(p1.getSlope() - p2.getSlope())
            for i in range(1, int(spreadAngle)):
                allPoints += (c.pointOnCircle(p1.getSlope() - i * spreadAngle / int(spreadAngle)), )
        allPoints += (p2, p3, point(p0.X, p0.Y))
        return (allPoints, mainPoints)

    def getWireCoordinates(self):
        """ Calculates the coordinates of the wires in the slot. """
        t = self.getCoordinates()[1]
        a = self.winding.coil.wire.isolationDiameter
        h = math.sqrt(3) / 2 * a + (1 - math.sqrt(3) / 2) * a * (1 - self.winding.coil.nestingFactor / 100)
        e, ah = 0.99, 2 / math.sqrt(3) * h

        """ Add initial wire """
        l1 = line.__pointANDpoint__(t[0], t[1])
        l2 = line.__pointANDpoint__(t[1], t[2])
        l3 = line.__slopeANDpoint__(360 / self.stator.slotNumber / 2, t[1])
        l1.moveParallel(a / 2)
        l2.moveParallel(-a / 2)
        pc = l1.lineIntersection(l2)
        pc = l1.movePoint(pc, self.winding.coil.moveFirstWire)
        output = (pc, )

        i = 0
        while (pc.X < t[len(t) - 2].X):
            while (pc.Y > (self.stator.innerDiameter - self.stator.tooth.yokeThickness - self.winding.slotIsolation) / 2):
                pc = l1.movePoint(pc, -ah)
                pt, pb, pr, pl = l1.movePoint(pc, e * a / 2), l1.movePoint(pc, -e * a / 2), l3.movePoint(pc, e * a / 2), l3.movePoint(pc, -e * a / 2)

                if (pt.isInsidePolygon(t) and pb.isInsidePolygon(t) and pl.isInsidePolygon(t) and pr.isInsidePolygon(t)):
                    output += (pc, )
                    if (len(output) > self.winding.coil.windingNumber):
                        return output
                else:
                    if (pc.Y < l1.lineIntersection(l2).Y):
                        break
            i += 1
            pc = l1.lineIntersection(l2)
            pc = l1.movePoint(pc, ah * (1 + 0.5 * (i % 2)))
            pc = l3.movePoint(pc, i * h)
        return output
