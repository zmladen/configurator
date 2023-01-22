import math


class point:
    """ Point object on a Cartesian coordinate plane with values x and y."""

    def __init__(self, x, y):
        """Defines x and y variables"""
        self.X = x
        self.Y = y

    def __Plot__(self, ax, label='point'):
        """ Plots the point on the graph """
        ax.scatter(self.X, self.Y)
        ax.annotate(label, (self.X, self.Y))

    def __str__(self):
        """ Prints the coordinates of the object"""
        return "Point(%s,%s)" % (self.X, self.Y)

    def reprJSON(self):
        return {"x": self.X, "y": self.Y}

    def getX(self):
        return self.X

    def getY(self):
        return self.Y

    def move(self, dx, dy):
        """Determines where x and y move"""
        self.X = self.X + dx
        self.Y = self.Y + dy

    def rotateArroundPoint(self, p, angle):
        """ Rotates the point for a given angle [deg] """
        x = self.X
        y = self.Y
        self.X = (x - p.X) * math.cos(angle * math.pi / 180) - (y - p.Y) * math.sin(angle * math.pi / 180) + p.X
        self.Y = (x - p.X) * math.sin(angle * math.pi / 180) + (y - p.Y) * math.cos(angle * math.pi / 180) + p.Y

    def rotateArroundPointCopy(self, p, angle):
        """ Rotates the point for a given angle [deg] """
        x = (self.X - p.X) * math.cos(angle * math.pi / 180.0) - (self.Y - p.Y) * math.sin(angle * math.pi / 180.0) + p.X
        y = (self.X - p.X) * math.sin(angle * math.pi / 180.0) + (self.Y - p.Y) * math.cos(angle * math.pi / 180.0) + p.Y

        return point(x, y)

    def rotate(self, angle):
        """ Rotates the point for a given angle [deg] """
        x = self.X
        y = self.Y
        self.X = x * math.cos(angle * math.pi / 180) - y * math.sin(angle * math.pi / 180)
        self.Y = x * math.sin(angle * math.pi / 180) + y * math.cos(angle * math.pi / 180)

    def rotateCopy(self, angle):
        """ Rotates the point for a given angle [deg] """
        x = self.X
        y = self.Y
        X = x * math.cos(angle * math.pi / 180) - y * math.sin(angle * math.pi / 180)
        Y = x * math.sin(angle * math.pi / 180) + y * math.cos(angle * math.pi / 180)
        return point(X, Y)

    def distance(self, other):
        dx = self.X - other.X
        dy = self.Y - other.Y
        return math.sqrt(dx**2 + dy**2)

    def getSlope(self):
        """ Get slope of the point with respect to the xAxis """
        return (math.atan(self.Y / self.X) * 180 / math.pi + 180) % 180

    def getRelativeSlope(self, p):
        """ Get slope of the point with respect to the xAxis """
        if (self.Y >= p.Y):
            return (math.atan((self.Y - p.Y) / (self.X - p.X)) * 180.0 / math.pi + 180.0) % 180.0
        else:
            """ if center of the circle is over the point """
            return (math.atan((self.Y - p.Y) / (self.X - p.X)) * 180.0 / math.pi + 180.0) % 180.0 + 180.0

    def getRelativeSlope360(self, p):
        """ Get slope of the point with respect to the xAxis """

        x = self.X - p.X
        y = self.Y - p.Y

        if (round(x, 6) == 0 and round(y, 6) == 0):
            return 0
        if (round(y, 6) == 0 and not round(x, 6) == 0):
            if (x > 0):
                return 0.0
            else:
                return 180.0
        if (round(x, 6) == 0 and not round(y, 6) == 0):
            if (y > 0):
                return 90.0
            else:
                return 270.0

        if (y > 0):
            return (math.atan(y / x) * 180 / math.pi + 180) % 180
        else:
            return (math.atan(y / x) * 180 / math.pi + 180) % 180 + 180

    def mirrorArroundYAxis(self):
        """ Get slope of the point with respect to the xAxis """
        self.X = -self.X

    def mirrorArroundXAxis(self):
        """ Get slope of the point with respect to the xAxis """
        self.Y = -self.Y

    def isEqual(self, p):
        """ Returns True of False is two points are equal """
        if (self.X == p.X and self.Y == p.Y):
            return True
        else:
            return False

    def isInsidePolygon(self, polygon):
        """ Cchecks if point is within the polygon """
        xmin, xmax, ymin, ymax = polygon[0].X, polygon[0].X, polygon[0].Y, polygon[0].Y
        output = False

        for p in polygon:
            xmin, xmax, ymin, ymax = min(p.X, xmin), max(p.X, xmax), min(p.Y, ymin), max(p.Y, ymax)

        if (self.X < xmin or self.X > xmax or self.Y < ymin or self.Y > ymax):
            return output
        else:
            """ http://www.ecse.rpi.edu/Homepages/wrf/Research/Short_Notes/pnpoly.html """
            j = len(polygon) - 1
            for i in range(0, len(polygon)):
                if ((polygon[i].Y > self.Y) != (polygon[j].Y > self.Y) and self.X < (polygon[j].X - polygon[i].X) * (self.Y - polygon[i].Y) / (polygon[j].Y - polygon[i].Y) + polygon[i].X):
                    output = not output
                j = i

        return output
