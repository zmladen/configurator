import math
import numpy as np
from .point import point


class cycloid():
    """
    Source
    -------------
    https://github.com/mikedh/cycloidal

    Return a (n,2) curve representing a cyloidal gear profile.

    Parameters
    -------------
    Zb:         int, number of pins in the radial pattern
    Zg:         int, number of lobes on the disc. For a regular disc, equal to count_pin-1
    e:          float, magnitude of eccentricity
    rz:         float, radius of individual pin
    Rz:         float, radius of pin centers
    resolution:     float, number of points per degree

    Returns
    ------------
    profile: (n,2) float, ordered points on curve in 2D space
    """

    def __init__(self, Rz, rz, e, Zb, Zg):
        self.Rz = Rz
        self.rz = rz
        self.e = e
        self.Zb = Zb
        self.Zg = Zg

    @classmethod
    def __gerotor__(cls, e, Z):
        Rz = (e * 2 * (Z + 1) + e * 2) / 2
        rz = 2 * e
        Zb = (Z + 1)
        Zg = Z
        return cls(Rz, rz, e, Zb, Zg)

    def __rotate_via_numpy(self, x, y, radians, origin=(0, 0)):
        """Use numpy to build a rotation matrix and take the dot product."""
        ox, oy = origin

        xx = ox + (x - ox) * math.cos(radians) + (y - oy) * math.sin(radians)
        yy = oy + -(x - ox) * math.sin(radians) + (y - oy) * math.cos(radians)

        return (xx, yy)

    def getCoordinates(self, resolution=8):
        # Rz = L
        # r2 = e * Zb
        # e = a
        Ze = self.Zb / (self.Zb - self.Zg)
        Zd = self.Zg / (self.Zb - self.Zg)
        K1 = (self.e * self.Zb) / (self.Rz * (self.Zb - self.Zg))
        print(self.Rz, K1)
        # in the paper they say you should calculate this numerically...
        psi = np.linspace(0, np.pi * 2, int(resolution * 360))

        denom_B = np.sqrt(1 + K1**2 - 2 * K1 * np.cos(Zd * psi))
        cos_B = np.sign(self.Zb - self.Zg) * ((K1 * np.sin(Ze * psi)) - np.sin(psi)) / denom_B
        sin_B = np.sign(self.Zb - self.Zg) * ((-K1 * np.cos(Ze * psi)) + np.cos(psi)) / denom_B

        x = self.Rz * np.sin(psi) - self.e * np.sin(Ze * psi) + self.rz * cos_B
        y = self.Rz * np.cos(psi) - self.e * np.cos(Ze * psi) - self.rz * sin_B

        # Rotate so that the inner gear always have the same initial orientation
        initAngle = -np.pi / 2 + np.pi / self.Zg if self.Zg % 2 else -np.pi / 2
        (xx, yy) = self.__rotate_via_numpy(x, y,  initAngle)

        profile = np.column_stack((xx, yy))

        coordinates = [point(p[0], p[1]) for p in profile]

        return coordinates
