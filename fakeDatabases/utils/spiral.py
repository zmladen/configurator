from .point import point
import math
from scipy.optimize import *

D2R = math.pi / 180.0
R2D = 180.0 / math.pi


def myFunction(z, *data):
    x, y = z[0], z[1]
    A, B, C, a, b, c = data
    F = [0, 0]
    F[0] = A * x + B * y - C
    F[1] = math.sqrt(x**2 + y**2) - (a + b * math.atan(y / x))
    # F[1] = (a + b * math.atan(y / x)) * math.cos(math.atan(y / x)) - x
    return F


class spiral:
    """ A spiral object based on the Archimedean Spiral: r(t) = a + b * math.pow(t, 1 / c)"""

    def __init__(self, a, b, c):
        self.a = a  # starting point of the spiral
        self.b = b  # distance between the loops
        self.c = c

    def lineIntersection(self, line, pguess):
        sol, infodict, ier, mesg = fsolve(myFunction, [pguess.X, pguess.Y], args=(line.A, line.B, line.C, self.a, self.b, self.c), full_output=True)

        return point(sol[0], sol[1])

    def pointOnSpiral(self, theta, epsilon=0, direction="ccw"):
        if direction == "ccw":
            xe = (self.a + self.b * math.pow(theta * D2R, 1 / self.c)) * math.cos((theta + epsilon) * D2R)
        else:
            xe = -(self.a + self.b * math.pow(theta * D2R, 1 / self.c)) * math.cos((theta + epsilon) * D2R)

        ye = (self.a + self.b * math.pow(theta * D2R, 1 / self.c)) * math.sin((theta + epsilon) * D2R)
        return point(xe, ye)

    def r(self, theta, epsilon=0):
        xe = (self.a + self.b * math.pow(theta * D2R, 1 / self.c)) * math.cos((theta + epsilon) * D2R)
        ye = (self.a + self.b * math.pow(theta * D2R, 1 / self.c)) * math.sin((theta + epsilon) * D2R)
        return math.sqrt(xe**2 + ye**2)
