import math
from .point import point
from .line import line


class circle:

    """ Circle object based on the model (x - x0)**2 + (y - y0)**2 = r.
        The center of the circle is given by point(X0, y0) """

    def __init__(self, radius, center=point(0, 0)):
        """ Defines radius and center of the circle """
        self.radius = radius
        self.center = center

    @classmethod
    def __3points__(cls, p1, p2, p3):
        """ Calculates center and and the radius of the circle defined by 3 points. Approach based on determinant calculation.
            https://math.stackexchange.com/questions/213658/get-the-equation-of-a-circle-when-given-3-points """
        M11 = (
            p1.X * p2.Y * 1
            + p1.Y * 1 * p3.X
            + 1 * p2.X * p3.Y
            - p3.X * p2.Y * 1
            - p3.Y * 1 * p1.X
            - 1 * p2.X * p1.Y
        )
        M12 = (
            (p1.X ** 2 + p1.Y ** 2) * p2.Y * 1
            + p1.Y * 1 * (p3.X ** 2 + p3.Y ** 2)
            + 1 * (p2.X ** 2 + p2.Y ** 2) * p3.Y
            - (p3.X ** 2 + p3.Y ** 2) * p2.Y * 1
            - p3.Y * 1 * (p1.X ** 2 + p1.Y ** 2)
            - 1 * (p2.X ** 2 + p2.Y ** 2) * p1.Y
        )
        M13 = (
            (p1.X ** 2 + p1.Y ** 2) * p2.X * 1
            + p1.X * 1 * (p3.X ** 2 + p3.Y ** 2)
            + 1 * (p2.X ** 2 + p2.Y ** 2) * p3.X
            - (p3.X ** 2 + p3.Y ** 2) * p2.X * 1
            - p3.X * 1 * (p1.X ** 2 + p1.Y ** 2)
            - 1 * (p2.X ** 2 + p2.Y ** 2) * p1.X
        )
        M14 = (
            (p1.X ** 2 + p1.Y ** 2) * p2.X * p3.Y
            + p1.X * p2.Y * (p3.X ** 2 + p3.Y ** 2)
            + p1.Y * (p2.X ** 2 + p2.Y ** 2) * p3.X
            - (p3.X ** 2 + p3.Y ** 2) * p2.X * p1.Y
            - p3.X * p2.Y * (p1.X ** 2 + p1.Y ** 2)
            - p3.Y * (p2.X ** 2 + p2.Y ** 2) * p1.X
        )

        if M11 != 0:
            x0 = 1.0 / 2.0 * M12 / M11
            y0 = -1.0 / 2.0 * M13 / M11
            radius = math.sqrt(x0 ** 2 + y0 ** 2 + M14 / M11)
            center = point(x0, y0)
        else:
            """ Points are on the same line """
            center = point(0, 0)
            radius = sys.float_info.max

        return cls(radius, center)

    def __Plot__(self, ax, label="circle"):
        """ Plots the circle on a figure """

        angles = self.frange(0, 360, 0.25)
        x, y = [], []
        for angle in angles:
            x.append(self.center.X + self.radius * math.cos(angle * math.pi / 180))
            y.append(self.center.Y + self.radius * math.sin(angle * math.pi / 180))

        ax.plot(x, y, linestyle="-", label=label)

    def __plotArc__(self, ax, anglestart, anglestop, label="circle"):
        """ Plots the circle on a figure """

        angles = self.frange(anglestart, anglestop, 0.25)
        x, y = [], []
        for angle in angles:
            x.append(self.center.X + self.radius * math.cos(angle * math.pi / 180))
            y.append(self.center.Y + self.radius * math.sin(angle * math.pi / 180))

        ax.plot(x, y, linestyle="-", label=label)

    def getArcCoordinates(self, anglestart, anglestop, Npoints=15):
        # anglestart < anglestop
        angles = self.frange(anglestart, anglestop, (anglestop - anglestart) / Npoints)
        coordinates = []
        for angle in angles:
            coordinates.append(self.pointOnCircle(angle))

        return coordinates

    def getArcAngle(self, s):
        return s * 360 / (2 * math.pi * self.radius)

    def getChordAngle(self, c):
        return 2 * math.asin(c / (2 * self.radius)) * 180 / math.pi

    def getChordLenght(self, angle):
        return 2 * self.radius * math.sin(angle / 2 * 180 / math.pi)

    def getArcLength(self, angle):
        return math.pi * self.radius * angle / 180

    def getArea(self):
        """ Calculates area of the circle """
        return self.radius ** 2 * math.pi

    def circle_intersection_right(self, c2):

        pR2_1 = self.circle_intersection(c2)[0]
        pR2_2 = self.circle_intersection(c2)[1]

        pR2 = pR2_1 if pR2_1.X > pR2_2.X else pR2_2

        return pR2

    def circle_intersection_left(self, c2):

        pR2_1 = self.circle_intersection(c2)[0]
        pR2_2 = self.circle_intersection(c2)[1]

        pR2 = pR2_1 if pR2_1.X < pR2_2.X else pR2_2

        return pR2

    def circle_intersection(self, c):
        '''
        @summary: calculates intersection points of two circles
        @param circle1: tuple(x,y,radius)
        @param circle2: tuple(x,y,radius)
        @result: tuple of intersection points (which are (x,y) tuple)
        '''
        # return self.circle_intersection_sympy(circle1,circle2)
        x1, y1, r1 = self.center.X, self.center.Y, self.radius
        x2, y2, r2 = c.center.X, c.center.Y, c.radius
        # http://stackoverflow.com/a/3349134/798588
        dx, dy = x2 - x1, y2 - y1
        d = math.sqrt(dx * dx + dy * dy)
        if d > r1 + r2:
            print("#1")
            return None  # no solutions, the circles are separate
        if d < abs(r1 - r2):
            print("#2")
            return None  # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            print("#3")
            return None  # circles are coincident and there are an infinite number of solutions

        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        h = math.sqrt(r1 * r1 - a * a)
        xm = x1 + a * dx / d
        ym = y1 + a * dy / d
        xs1 = xm + h * dy / d
        xs2 = xm - h * dy / d
        ys1 = ym - h * dx / d
        ys2 = ym + h * dx / d

        return (point(xs1, ys1), point(xs2, ys2))

    def circle_intersection_sympy(self, c):
        from sympy.geometry import Circle, Point
        c1 = Circle(Point(self.center.X, self.center.Y), self.radius)
        c2 = Circle(Point(c.center.X, c.center.Y), c.radius)
        intersection = c1.intersection(c2)
        if len(intersection) == 1:
            intersection.append(intersection[0])
        p1 = intersection[0]
        p2 = intersection[1]
        return [point(p1.x, p1.y), point(p2.x, p2.y)]

    def pointOnCircle(self, alpha, direction="ccw"):
        """ Calculates the coordinates of the point on the circle at angle alpha"""
        if direction=="ccw":
            return point(
                self.center.X + self.radius * math.cos(alpha * math.pi / 180),
                self.center.Y + self.radius * math.sin(alpha * math.pi / 180),
            )
        else:
            return point(
                self.center.X - self.radius * math.cos(alpha * math.pi / 180),
                self.center.Y + self.radius * math.sin(alpha * math.pi / 180),
            )

    def lineIntersection(self, line):
        """ Calculates the intersection points of a circle with the line. Point above
            is the first point in a tuple """
        if line.B == 0:
            if self.radius < abs(line.C / line.A):
                return (point(None, None), point(None, None))
            else:
                p1 = point(
                    line.C / line.A,
                    self.center.Y
                    + math.sqrt(
                        self.radius ** 2 - (line.C / line.A - self.center.X) ** 2
                    ),
                )
                p2 = point(
                    line.C / line.A,
                    self.center.Y
                    - math.sqrt(
                        self.radius ** 2 - (line.C / line.A - self.center.X) ** 2
                    ),
                )
                return (p1, p2)
        else:
            """ http://www.ambrsoft.com/TrigoCalc/Circles2/circlrLine_.htm """
            m = -line.A / line.B
            d = line.C / line.B

            A = 1 + m ** 2
            B = 2 * (-self.center.X + m * d - m * self.center.Y)
            C = (
                self.center.X ** 2
                + d ** 2
                - 2 * self.center.Y * d
                + self.center.Y ** 2
                - self.radius ** 2
            )
            D = B ** 2 - 4 * A * C

            if D < 0:
                return (point(None, None), point(None, None))
            else:
                x1 = (-B + math.sqrt(D)) / 2 / A
                x2 = (-B - math.sqrt(D)) / 2 / A
                y1 = m * x1 + d
                y2 = m * x2 + d

                if y1 >= y2:
                    return (point(x1, y1), point(x2, y2))
                else:
                    return (point(x2, y2), point(x1, y1))

    def frange(self, start, end=None, inc=None):
        "A range function, that does accept float increments..."

        if end == None:
            end = start + 0.0
            start = 0.0

        if inc == None:
            inc = 1.0

        L = []
        while 1:
            next = start + len(L) * inc
            if inc > 0 and next >= end:
                L.append(next)
                break
            elif inc < 0 and next <= end:
                L.append(next)
                break
            L.append(next)

        return L

    def findTangentThroughPoint(self, p):
        # http://www.ambrsoft.com/TrigoCalc/Circles2/circlrLine_.htm
        # Line equation: a*x + b*y = c
        xt = p.X
        yt = p.Y
        a = self.center.X
        b = self.center.Y
        r = self.radius

        if (b != yt):
            m = (xt - a) / (b - yt)
            k = -m * xt + yt
            return line(-m, 1, k)

        else:
            # x = xt
            return line(1, 0, xt)

    def tagnentPointsThroughPoint(self, p):
        # Returns the tangent points on the circle whose tangent passes through outer point p
        # Example from:
        # https://math.stackexchange.com/questions/543496/how-to-find-the-equation-of-a-line-tangent-to-a-circle-that-passes-through-a-g

        r = self.radius
        Px, Py, Cx, Cy = p.X, p.Y, self.center.X, self.center.Y
        dx, dy = Px - Cx, Py - Cy
        dxr, dyr = -dy, dx
        d = math.sqrt(dx**2 + dy**2)
        if d >= r:
            rho = r / d
            ad = rho**2
            bd = rho * math.sqrt(1 - rho**2)
            T1x = Cx + ad * dx + bd * dxr
            T1y = Cy + ad * dy + bd * dyr
            T2x = Cx + ad * dx - bd * dxr
            T2y = Cy + ad * dy - bd * dyr

            # print('The tangent points:')
            return (point(T1x, T1y), point(T2x, T2y))
            if (d / r - 1) < 1E-8:
                print('P is on the circumference')
                return (p, p)
            else:
                return (point(T1x, T1y), point(T2x, T2y))

        else:
            print("Point P=(%s,%s) is inside the circle with centre C=(%s,%s) and radius r=%s. No tangent is possible..." % (Px, Py, Cx, Cy, r))

    def getCoordinates(self, resolution=8):
        # Circle coordinates
        coordinates = []
        for psi in self.frange(0, 360, 1 / resolution):
            coordinates.append(self.pointOnCircle(psi))
        return coordinates
