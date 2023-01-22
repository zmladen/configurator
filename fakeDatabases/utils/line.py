import math
from .point import point


class line:
    """ A line object based on the model Ax + By = C """

    def __init__(self, A, B, C):
        """ Defines A, B and C variables """
        self.A = A
        self.B = B
        self.C = C

    @classmethod
    def __pointANDpoint__(cls, p1, p2):
        """ points in mm """
        if p2.X - p1.X != 0:
            m = (p2.Y - p1.Y) / (p2.X - p1.X)
            A = -m
            B = 1
            C = p1.Y - m * p1.X
        else:
            A = 1
            B = 0
            C = p1.X

        return cls(A, B, C)

    @classmethod
    def __slopeANDpoint__(cls, slope, p=point(0, 0)):
        """ point in mm slope in deg """
        if abs(slope) == 90 or abs(slope) == 270:
            A = 1
            B = 0
            C = p.X
        else:
            A = -math.tan(slope * math.pi / 180)
            B = 1
            C = p.Y - math.tan(slope * math.pi / 180) * p.X

        return cls(A, B, C)

    @classmethod
    def __kANDpoint__(cls, k, p=point(0, 0)):
        """ point in mm slope in deg """
        A = -k
        B = 1
        C = p.Y - k * p.X

        return cls(A, B, C)

    @property
    def k(self):
        """ Calculates the slope of the line """
        try:
            if self.B != 0:
                return -self.A / self.B
            else:
                return -self.A

        except ZeroDivisionError as e:
            print("Calculating slope error:", e)

    @property
    def l(self):
        """ Calculates the slope of the line """
        try:
            if self.B != 0:
                return self.C / self.B
            else:
                return self.C

        except ZeroDivisionError as e:
            print("Calculating slope error:", e)

    def __str__(self):
        """ Prints the coordinates of the object"""
        return "Point(%s, %s, %s)" % (self.A, self.B, self.C)

    def __Plot__(self, ax, label="line"):

        x = range(-60, 60)
        if self.B != 0:
            y = [-self.A / self.B * x + self.C / self.B for x in range(-60, 60)]
        else:
            x = [self.C / self.A for x in range(-60, 60)]
            y = range(-60, 60)

        ax.plot(x, y, "-", label=label)

    def intersectionListOfPoints(self, points):
        # points must be uniform and x-coordinate hast to increase
        for i in range(len(points) - 1):

            p0 = points[i]
            p1 = points[i + 1]
            pi = self.lineIntersection(line.__pointANDpoint__(p0, p1))

            xmin = p0.X if p0.X <= p1.X else p1.X
            xmax = p1.X if p0.X <= p1.X else p0.X
            ymin = p0.Y if p0.Y <= p1.Y else p1.Y
            ymax = p1.Y if p0.Y <= p1.Y else p0.Y

            if pi.X >= xmin and pi.X <= xmax and pi.Y >= ymin and pi.Y <= ymax:
                return pi
            else:
                if i == len(points) - 1:
                    return None

    def intersectionLineSegments(self, segments):
        for i in range(len(segments) - 1):
            p0 = segments[i]
            p1 = segments[i + 1]
            pi = self.lineIntersection(line.__pointANDpoint__(p0, p1))

            xmin = p0.X if p0.X <= p1.X else p1.X
            xmax = p1.X if p0.X <= p1.X else p0.X
            ymin = p0.Y if p0.Y <= p1.Y else p1.Y
            ymax = p1.Y if p0.Y <= p1.Y else p0.Y

            if pi.X >= xmin and pi.X <= xmax and pi.Y >= ymin and pi.Y <= ymax:
                return pi
            else:
                if i == len(segments) - 1:
                    return None

    def xAxisIntersection(self):
        """ Determines the intersection point of the line and the xAxis"""
        return self.C / self.A

    def yAxisIntersection(self):
        """ Determines the intersection point of the line and the yAxis"""
        return self.C / self.B

    def lineIntersection(self, line):
        """ Determines the intersection point of the line with another line """
        D = self.A * line.B - self.B * line.A

        if D == 0:
            return point(None, None)
        else:
            return point(
                (line.B * self.C - self.B * line.C) / D,
                (line.C * self.A - self.C * line.A) / D,
            )

    def moveParallel(self, delta):
        """ Moves line parallel to a distance delta """
        self.C = self.C + delta * math.sqrt(self.A ** 2 + self.B ** 2)

    def moveParallelyAxis(self, delta):
        """ Moves line parallel to yAxis """
        self.C = self.C + delta

    def moveParallelxAxis(self, delta):
        """ Moves line parallel to xAxis """
        self.C = self.C + self.A * delta

    def moveParallelThroughPoint(self, p):
        """ Moves line parallel through a point """
        self.C = self.B * (p.Y - p.X * math.tan(self.getSlope() * math.pi / 180))

    def orthogonalThroughPoint(self, p):
        """ Makes the orthogonal line through the point """
        try:
            if self.B != 0:
                mp = self.B / self.A
                self.A = -mp
                self.B = 1.0
                self.C = p.Y - mp * p.X
            else:
                self.A = 0
                self.B = 1
                self.C = p.Y
        except ZeroDivisionError as e:
            print("orthogonality error:", e)

    def mirrorPoint(self, p):
        """ Mirrors a point across a line """
        lo = line(self.A, self.B, self.C)
        lo.orthogonalThroughPoint(p)
        l = line(self.A, self.B, self.C)
        pi = l.lineIntersection(lo)
        d = p.distance(pi)

        pi = lo.movePoint(pi, -d)

        return pi

    def movePoint(self, p, distance):
        """ Moves the point for a distance along the line """
        x = p.X + distance * math.cos(self.getSlope() * math.pi / 180.0)
        y = p.Y + distance * math.sin(self.getSlope() * math.pi / 180.0)
        return point(x, y)

    def getSlope(self):
        """ Calculates the slope of the line """
        try:
            if self.B != 0:
                return (math.atan(-self.A / self.B) * 180.0 / math.pi + 180.0) % 180.0
            else:
                return 90
        except ZeroDivisionError as e:
            print("Calculating slope error:", e)
