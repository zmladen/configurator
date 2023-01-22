import math


class magnet(object):
    """Magnet class that holds all important parameters and methods needed to characterize the magnet material."""

    def __init__(self, isLinear=True, eddyLosses=False, data={}, temperature=25):

        self.data = data
        self.temperature = temperature
        self.density = 0
        self.conductivity_ref = 0
        self.br_min = 0
        self.br_max = 0
        self.hcb_min = 1
        self.hcb_max = 1
        self.hcj_min = 1
        self.hcj_max = 1
        self.bh_min = 0
        self.bh_max = 0
        self.tc_br = 0
        self.tc_hcb = 0
        self.tc_sigma = 0
        self.j_ref = []
        self.h_ref = []
        self.eddyLosses = eddyLosses
        self.isLinear = isLinear
        self.__tempRef = 25
        self.possibleMagnetisation = []
        self.remanenceScaleFactor = 100
        self.ur_theory = None
        self.id = None
        self.intrinsicDemagnetizationCurves = []

        if not self.data == {}:
            self.readJSON(self.data)

        try:
            self.infoName = '%s (%s, %s)' % (
                self.name, "T" + str(self.temperature) + "C", "RCF" + str(self.remanenceScaleFactor))
        except AttributeError:
            print("name not found")

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        data = data.get("Used", data)

        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "Density (kg/m3)" in data:
            self.density = data["Density (kg/m3)"]
        if "Conductivity (S/m)" in data:
            self.conductivity_ref = data["Conductivity (S/m)"]
        if "Br min. (T)" in data:
            self.br_min = data["Br min. (T)"]
        if "Br max. (T)" in data:
            self.br_max = data["Br max. (T)"]
        if "Hcb min. (A/m)" in data:
            self.hcb_min = data["Hcb min. (A/m)"]
        if "Hcb max. (A/m)" in data:
            self.hcb_max = data["Hcb max. (A/m)"]
        if "Hcj min. (A/m)" in data:
            self.hcj_min = data["Hcj min. (A/m)"]
        if "Hcj max. (A/m)" in data:
            self.hcj_max = data["Hcj max. (A/m)"]
        if "BH min. (J/m3)" in data:
            self.bh_min = data["BH min. (J/m3)"]
        if "BH max. (J/m3)" in data:
            self.bh_max = data["BH max. (J/m3)"]
        if "Tc Br (%/C)" in data:
            self.tc_br = data["Tc Br (%/C)"]
        if "Tc Hcb (%/C)" in data:
            self.tc_hcb = data["Tc Hcb (%/C)"]
        if "Tc Sigma (%/C)" in data:
            self.tc_sigma = data["Tc Sigma (%/C)"]
        if "J (T)" in data:
            self.j_ref = data["J (T)"]
        if "Hcj (A/m)" in data:
            self.h_ref = data["Hcj (A/m)"]
        if "Calculate Eddy Current Losses" in data:
            self.eddyLosses = data["Calculate Eddy Current Losses"]
        if "Possible Magnetisation" in data:
            self.possibleMagnetisation = data["Possible Magnetisation"]
        if "Remanence Scale Factor (%)" in data:
            self.remanenceScaleFactor = data["Remanence Scale Factor (%)"]
        if "ur" in data:
            self.ur_theory = data["ur"]
        if "Intrinsic Demagnetization Curves" in data:
            self.intrinsicDemagnetizationCurves = data["Intrinsic Demagnetization Curves"]

    def reprJSON(self):
        """Creates json representation of the object."""

        return {
            "Used": {
                "id": self.id,
                "name": self.name,
                "Density (kg/m3)": self.density,
                "Possible Magnetisation": self.possibleMagnetisation,
                "Conductivity (S/m)": self.conductivity_ref,
                "Br min. (T)": self.br_min,
                "Br max. (T)": self.br_max,
                "Hcb min. (A/m)": self.hcb_min,
                "Hcb max. (A/m)": self.hcb_max,
                "Hcj min. (A/m)": self.hcj_min,
                "Hcj max. (A/m)": self.hcj_max,
                "BH min. (J/m3)": self.bh_min,
                "BH max. (J/m3)": self.bh_max,
                "Tc Br (%/C)": self.tc_br,
                "Tc Hcb (%/C)": self.tc_hcb,
                "Tc Sigma (%/C)": self.tc_sigma,
                "J (T)": self.j_ref,
                "Hcj (A/m)": self.h_ref,
                "Remanence Scale Factor (%)": self.remanenceScaleFactor,
                "Intrinsic Demagnetization Curves": self.intrinsicDemagnetizationCurves
            },
            "Options": self.data.get("Options", [])
        }

    def __findNearestIndex(self, array, value):
        n = [abs(i-value) for i in array]
        idx = n.index(min(n))
        return idx

    def getDemagnetizationCurve(self):
        # Find data nearest to 20deg. The thermal coefficents are given for this reference temperature
        idx = self.__findNearestIndex(
            [i["Temperature (C)"] for i in self.intrinsicDemagnetizationCurves], 20)

        curves = self.intrinsicDemagnetizationCurves[idx]

        J_ref = curves["J (T)"]
        H_ref = curves["H (A/m)"]
        T_ref = curves["Temperature (C)"]

        j = []
        for item in J_ref:
            j.append(item * (1 + self.tc_br / 100.0 *
                     (self.temperature - T_ref)))

        h = []
        for item in H_ref:
            h.append(item * (1 + self.tc_hcb / 100.0 *
                     (self.temperature - T_ref)))

        return {
            "Temperature (C)": self.temperature,
            "H (A/m)": h,
            "J (T)": j
        }

    @property
    def j(self):
        """ Calculates the magnetization strength of the non-linear magnet material at given temperature. """
        j = []
        for item in self.j_ref:
            j.append(item * (1 + self.tc_br / 100.0 *
                     (self.temperature - self.__tempRef)))
        return j

    @property
    def b(self):
        """ Calculates the magentic flux density for non-linear magnet material at given temperature. """
        b = []
        for index, j in enumerate(self.j):
            b.append(j + self.u0 * self.h[index])
        return b

    @property
    def h(self):
        """ Calculates the hardmagnetic field strength of the non-linear magnet material at ambient temperature. """
        h = []
        for item in self.h_ref:
            h.append(item * (1 + self.tc_hcj / 100.0 *
                     (self.temperature - self.__tempRef)))
        return h

    @property
    def resistivity(self):
        """ Calculates electrical resistivity of the magnet at ambient temperature. """
        try:
            return (1.0 / self.conductivity_ref) * (1 - (self.tc_sigma / 100.0) * (self.temperature - self.__tempRef))
        except:
            return 1e12

    @property
    def br(self):
        """Calculates the remanence of the linear magnet material at ambient temperature. Maximal overhang (ratio of the rotor and stator stack length)."""
        return (self.remanenceScaleFactor / 100.0) * self.br_min * (1 + self.tc_br / 100.0 * (self.temperature - self.__tempRef))

    @property
    def ur(self):
        """ Calculates the relative permeability of the linear magnet material. It is not depending on the ambient temperature. """
        if self.ur_theory == None:
            return self.br_min / abs(self.hcb_min) / (4.0 * math.pi * 1e-7)
        else:
            return self.ur_theory

    @property
    def hcb(self):
        """ Calculates the relative permeability of the linear magnet material. It is not depending on the ambient temperature. """
        return -self.br / self.ur / (4.0 * math.pi * 1e-7)
