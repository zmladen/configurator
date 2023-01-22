import math
from .point import point
from .line import line
from scipy.optimize import *
# import sympy


def myFunction(z, *data):
    a, b, x0, y0 = z[0], z[1], z[2], z[3]
    X1, Y1, X2, Y2, m1, m2 = data
    F = [0, 0, 0, 0]
    F[0] = b**2 * X1**2 + a**2 * Y1**2 - 2 * x0 * b**2 * X1 - 2 * y0 * a**2 * Y1 + b**2 * x0**2 + a**2 * y0**2 - a**2 * b**2
    F[1] = b**2 * X2**2 + a**2 * Y2**2 - 2 * x0 * b**2 * X2 - 2 * y0 * a**2 * Y2 + b**2 * x0**2 + a**2 * y0**2 - a**2 * b**2
    F[2] = b ** 2 * X1 + a ** 2 * Y1 * m1 - x0 * b**2 - y0 * a ** 2 * m1
    F[3] = b ** 2 * X2 + a ** 2 * Y2 * m2 - x0 * b**2 - y0 * a ** 2 * m2
    return F


def func2(theta, *data):
    a, b, c, p = data
    r = a * b / math.sqrt((a * math.sin(theta))**2 + (b * math.cos(theta))**2)
    return r - math.sqrt((p.X - c.X)**2 + (p.Y - c.Y)**2)


class ellipse:

    """ Circle object based on the model (x - x0)**2 / A**2 + (y - y0)**2 / B**2 = 1.
        The center of the ellipse is given by point(X0, y0)
        The angle of the ellipse is described with alpha """

    def __init__(self, A, B, center=point(0, 0), inclination=0):
        """ Constructor of the ellipse object """
        self.A = A
        self.B = B
        self.center = center
        self.inclination = inclination

    @classmethod
    def __2pointsAND2tangents__(cls, e0, p1, p2, t1, t2):
        sol, infodict, ier, mesg = fsolve(myFunction, [e0.A, e0.B, e0.center.X, e0.center.Y], args=(p1.X, p1.Y, p2.X, p2.Y, t1.k, t2.k), full_output=True, factor=35,  xtol=1e-6, maxfev=500)
        # print(mesg)
        return cls(sol[0], sol[1], point(sol[2], sol[3]))

    def getAngleAtPoint(self, p):
        z = fsolve(func2, [p.getRelativeSlope360(self.center) * math.pi / 180], (self.A, self.B, self.center, p))
        return z[0] * 180 / math.pi

    def getTangentAtPoint(self, p0):
        if self.B != 0 and (p0.X - self.center.X) != 0:
            k = -(self.B**2 * (p0.X - self.center.X)) / (self.A**2 * (p0.Y - self.center.Y))
            return line.__kANDpoint__(k, p0)
        else:
            return line.__slopeANDpoint__(90, p0)

    def getNormalAtPoint(self, p0):
        if self.B != 0 and (p0.X - self.center.X) != 0:
            k = (self.A**2 * (p0.Y - self.center.Y)) / (self.B**2 * (p0.X - self.center.X))
            return line.__kANDpoint__(k, p0)
        else:
            return line.__slopeANDpoint__(90, p0)

    def getParallelPointAtAngleAndDistance(self, theta, distance):
        theta *= math.pi / 180
        Xp = (self.A + self.B * distance / math.sqrt(self.A**2 * math.sin(theta)**2 + self.B**2 * math.cos(theta)**2)) * math.cos(theta) + self.center.X
        Yp = (self.B + self.A * distance / math.sqrt(self.A**2 * math.sin(theta)**2 + self.B**2 * math.cos(theta)**2)) * math.sin(theta) + self.center.Y

        return point(Xp, Yp)

    def __Plot__(self, ax, label="ellipse"):
        """ Plots the ellipse on a figure """

        angles = range(0, 360, 1)

        x, y = [], []
        for angle in angles:
            xp = self.center.X + self.A * math.cos(angle * math.pi / 180.0)
            yp = self.center.Y + self.B * math.sin(angle * math.pi / 180.0)
            xr = (
                self.center.X
                + (xp - self.center.X) * math.cos(self.inclination * math.pi / 180.0)
                - (yp - self.center.Y) * math.sin(self.inclination * math.pi / 180.0)
            )
            yr = (
                self.center.Y
                + (xp - self.center.X) * math.sin(self.inclination * math.pi / 180.0)
                + (yp - self.center.Y) * math.cos(self.inclination * math.pi / 180.0)
            )
            x.append(xr)
            y.append(yr)

        ax.plot(x, y, "-", label=label)

    def getArea(self):
        """ Calculates area of the ellipse """
        return math.pi * self.A * self.B

    def pointOnEllipse2(self, angle):
        r = self.A * self.B / math.sqrt((self.A * math.sin(angle * math.pi / 180.0))**2 + (self.B * math.cos(angle * math.pi / 180.0))**2)
        xp = self.center.X + r * math.cos(angle * math.pi / 180.0)
        yp = self.center.Y + r * math.sin(angle * math.pi / 180.0)
        return point(xp, yp)

    def getPerimeter(self):
        # https://www.mathsisfun.com/geometry/ellipse-perimeter.html
        # According to Ramanujan's approximation formula of finding perimeter of Ellipse
        perimeter = math.pi * (3 * (self.A + self.B) - math.sqrt((3 * self.A + self.B) * (self.A + 3 * self.B)))
        return perimeter

    def pointOnEllipse(self, alpha):
        """
            Calculates the coordinates of the point on the ellipse at angle alpha
            http://mathforum.org/library/drmath/view/54922.html
            http://math.stackexchange.com/questions/612981/find-angle-at-given-points-in-ellipse
        """
        q = math.atan(self.A * math.tan((alpha - self.inclination) * math.pi / 180.0) / self.B)
        if q < 0:
            q += math.pi

        return point(self.A * math.cos(q) * math.cos(self.inclination * math.pi / 180.0) - self.B * math.sin(q) * math.sin(self.inclination * math.pi / 180.0),
                     self.B * math.sin(q) * math.cos(self.inclination * math.pi / 180.0) + self.A * math.cos(q) * math.sin(self.inclination * math.pi / 180.0))

    def getParallelPointAtPointAndDistance(self, pointOnTheEllipse, distance):
        theta = self.getAngleAtPoint(pointOnTheEllipse)

        Xp = (self.A + self.B * distance / math.sqrt(self.A**2 * math.sin(theta)**2 + self.B**2 * math.cos(theta)**2)) * math.cos(theta) + self.center.X
        Yp = (self.B + self.A * distance / math.sqrt(self.A**2 * math.sin(theta)**2 + self.B**2 * math.cos(theta)**2)) * math.sin(theta) + self.center.Y

        # print("theta", theta * 180 / math.pi)
        # print("(Xp, Yp)", Xp, Yp)

        return point(Xp, Yp)

    def lineIntersection(self, line):
        """ Calculates the intersection points of the ellipse with the line.
            Upper point is the first element in a output tuple """
        if line.B == 0:
            if self.A < abs(line.C / line.A):
                return (point(None, None), point(None, None))
            else:
                x = line.C / line.A
                A = (
                    self.B ** 2 * math.sin(self.inclination * math.pi / 180) ** 2
                    + self.A ** 2 * math.cos(self.inclination * math.pi / 180) ** 2
                )
                B = (
                    2
                    * x
                    * math.cos(self.inclination * math.pi / 180)
                    * math.sin(self.inclination * math.pi / 180)
                    * (self.B ** 2 - self.A ** 2)
                )
                C = (
                    x ** 2
                    * (
                        self.B ** 2 * math.cos(self.inclination * math.PI / 180) ** 2
                        + self.A ** 2 * math.sin(self.inclination * math.PI / 180) ** 2
                    )
                    - self.A ** 2 * self.B ** 2
                )

                y1 = (-B + math.sqrt(B ** 2 - 4 * A * C)) / 2 / A
                y2 = (-B - math.sqrt(B ** 2 - 4 * A * C)) / 2 / A

                if y1 >= y2:
                    return (point(x, y1), point(x, y2))
                else:
                    return (point(x, y2), point(x, y1))

        else:
            """ http://www.ambrsoft.com/TrigoCalc/Circles2/circlrLine_.htm """
            m = -line.A / line.B
            k = line.C / line.B

            A = (
                self.B ** 2 * math.cos(self.inclination * math.pi / 180) ** 2
                + 2
                * self.B ** 2
                * m
                * math.cos(self.inclination * math.pi / 180)
                * math.sin(self.inclination * math.pi / 180)
                + self.B ** 2 * m ** 2 * math.sin(self.inclination * math.pi / 180) ** 2
                + self.A ** 2 * m ** 2 * math.cos(self.inclination * math.pi / 180) ** 2
                - 2
                * self.A ** 2
                * m
                * math.cos(self.inclination * math.pi / 180)
                * math.sin(self.inclination * math.pi / 180)
                + self.A ** 2 * math.sin(self.inclination * math.pi / 180) ** 2
            )
            B = (
                2
                * self.B ** 2
                * k
                * math.cos(self.inclination * math.pi / 180)
                * math.sin(self.inclination * math.pi / 180)
                + 2
                * self.B ** 2
                * m
                * k
                * math.sin(self.inclination * math.pi / 180) ** 2
                + 2
                * self.A ** 2
                * m
                * k
                * math.cos(self.inclination * math.pi / 180) ** 2
                - 2
                * self.A ** 2
                * k
                * math.cos(self.inclination * math.pi / 180)
                * math.sin(self.inclination * math.pi / 180)
            )
            C = (
                self.B ** 2 * k ** 2 * math.sin(self.inclination * math.pi / 180) ** 2
                + self.A ** 2 * k ** 2 * math.cos(self.inclination * math.pi / 180) ** 2
                - self.A ** 2 * self.B ** 2
            )
            D = B ** 2 - 4 * A * C

            if D < 0:
                return (point(None, None), point(None, None))
            else:
                x1 = (-B + math.sqrt(D)) / 2 / A
                x2 = (-B - math.sqrt(D)) / 2 / A
                y1 = m * x1 + k
                y2 = m * x2 + k

                if y1 >= y2:
                    return (point(x1, y1), point(x2, y2))
                else:
                    return (point(x2, y2), point(x1, y1))

    def tangentThroughPoint(self, p):
        """ Calculates the line that represents a tangent on the ellipse that passes through point.
            Algorithm calculates the slope of the tangent using the implicit differentiation. """
        m = -(self.B ** 2 / self.A ** 2) * (p.X - self.center.X) / (p.Y - self.center.Y)
        return line(-m, 1, p.Y - m * p.X)
