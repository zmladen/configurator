import math


class metal(object):
    """Metal class. Holds all important parameters and methods needed to characterize the metal material."""

    def __init__(self, eddyLosses=False, magnLosses=True, data={}, temperature=25):

        self.data = data
        self.id = ""
        self.temperature = temperature
        self.eddyLosses = eddyLosses
        self.magnLosses = magnLosses
        self.stackingFactor = 100
        self.density = 0
        self.conductivity_ref = 1
        self.__tempRef = 25
        self.tc_sigma = 0
        self.ur = 1
        self.kh = 0
        self.ke = 0
        self.ka = 0
        self.kdc = 0
        self.cut_depth = 0
        self.b_ref = []
        self.h_ref = []
        self.losses = []
        self.u0 = 4.0 * math.pi * 1E-7
        self.permeabilityReduction = 0
        self.magnetizationLossesIncrease = 0
        self.linearizeInitialPermeability = True
        self.tcle = data.get("Used", {}).get(
            "Thermal Coefficient of Linear Expansion (1/C)", 0)

        self.name = "test"
        if not data == {}:
            self.readJSON(data)

        self.infoName = '%s (%s)' % (
            self.name, "SF" + str(self.stackingFactor) + "%")
        self.linear = True if (len(self.b_ref) == 0) else False

    @property
    def permeability(self):
        """ Calculates the hardmagnetic field strength of the non-linear magnet material at ambient temperature. """

        ur = []
        for i in range(0, len(self.h_ref)):
            if self.h_ref[i] != 0:
                ur.append(float(self.b_ref[i]) /
                          float(self.h_ref[i]) / self.u0)

        if (self.linearizeInitialPermeability and len(ur) > 0):
            maxValue = max(ur)
            maxIndex = ur.index(maxValue)
            for index, value in enumerate(ur):
                if index <= maxIndex:
                    ur[index] = maxValue

        return ur

    @property
    def permeability_red(self):
        """ Calculates the hardmagnetic field strength of the non-linear magnet material at ambient temperature. """
        ur = []
        for item in self.permeability:
            ur.append(item / (1.0 + self.permeabilityReduction / 100.0))
        return ur

    @property
    def ur_max(self):
        # If material has empty H, B values it is conidered to be linear with ur = 1
        # Otherwise max value is used
        return 1 if (len(self.permeability) == 0) else max(self.permeability)

    @property
    def ur_max_red(self):
        return 1 if (len(self.permeability_red) == 0) else max(self.permeability_red)

    @property
    def resistivity(self):
        """ Calculates electrical resistivity of the magnet at ambient temperature. """
        try:
            return (1.0 / self.conductivity_ref) * (1 - (self.tc_sigma / 100.0) * (self.temperature - self.__tempRef))
        except:
            return 1e12

    @property
    def b(self):
        """ Calculates the magnetization strength of the non-linear magnet material at ambient temperature. """
        return self.b_ref

    @property
    def h(self):
        """ Calculates the hardmagnetic field strength of the non-linear magnet material at ambient temperature. """
        h = [0]
        for i in range(0, len(self.permeability)):
            if self.permeability[i] != 0:
                h.append(self.b_ref[i+1] / self.u0 / self.permeability[i])

        return h

    @property
    def b_sf(self):
        """ Calculates the magnetization strength of the non-linear magnet material at ambient temperature. """
        b = []
        for item in self.b_ref:
            b.append(item * self.stackingFactor / 100.0)
        return b

    @property
    def h_red(self):
        """ Calculates the hardmagnetic field strength of the non-linear magnet material at the ambient temperature. """
        h = [0]

        # print(self.name)
        # print("bref")
        # print(self.b_ref)
        for i in range(0, len(self.permeability_red)):
            h_next = self.b_ref[i+1] / self.u0 / self.permeability_red[i]
            h.append(h_next)

        # Version 1

        # for i in range(1, len(self.permeability_red)):
        #     if self.permeability_red[i] != 0:
        #         h_next = self.b_ref[i] / self.u0 / self.permeability_red[i]
        #         h_prev = h[i - 1]
        #         ur = (self.b_ref[i] - self.b_ref[i - 1]) / \
        #             (h_next - h_prev) / self.u0

        #         # if the slope of the BH curve between two poont is smaller than 1 ansys gives an error!
        #         if ur >= 1:
        #             h.append(h_next)
        #         else:
        #             # Stackingfactor is needed, otherwise ur is equal to 1*self.stackingFactor/100
        #             ur = 1.006 / (self.stackingFactor / 100)
        #             h.append(
        #                 h_prev + (self.b_ref[i] - self.b_ref[i - 1]) / ur / self.u0)

        # Version 2

        # if len(self.permeability_red) < len(self.b_ref):
        #     # This is the case when b_ref and h_ref starts with 0 which should always be the case
        #     h = [0]
        #     for i in range(1, len(self.permeability_red)):
        #         if self.permeability_red[i] != 0:
        #             h_next = self.b_ref[i] / self.u0 / self.permeability_red[i]
        #             h_prev = h[i - 1]
        #             ur = (self.b_ref[i] - self.b_ref[i - 1]) / (h_next - h_prev) / self.u0
        #             # if the slope of the BH curve between two poont is smaller than 1 ansys gives an error!
        #             if ur >= 1:
        #                 h.append(h_next)
        #             else:
        #                 # Stackingfactor is needed, otherwise ur is equal to 1*self.stackingFactor/100
        #                 ur = 1.006 / (self.stackingFactor / 100)
        #                 h.append(h_prev + (self.b_ref[i] - self.b_ref[i - 1]) / ur / self.u0)
        # else:
        #     h = []
        #     for i in range(0, len(self.permeability_red)):
        #         if self.permeability_red[i] != 0:
        #             h.append(self.b_ref[i] / self.u0 / self.permeability_red[i])

        # return self.h_ref
        return h

    def getSteinmetzLosses(self, volume=0, Bm=0, frequency=0):
        """Calculates the magnetization losses based on the Steinmetz formula. It is considered that the flux-density is uniform over the whole volume of the part (Bavg).
        Part is described with the volume variable in [mm2]."""
        return (self.kh * frequency * Bm ** 2.0 + self.ke * (frequency * Bm) ** 2.0 + self.ka * (frequency * Bm) ** 1.5) * volume * 1e-9

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        data = data["Used"]

        if "id" in data:
            self.id = data["id"]
        if "name" in data:
            self.name = data["name"]
        if "linear" in data:
            self.linear = data["linear"]
        if "Stacking Factor (%)" in data:
            self.stackingFactor = float(data["Stacking Factor (%)"])
        if "kh (W/m3)" in data:
            self.kh = data["kh (W/m3)"]
        if "ke (W/m3)" in data:
            self.ke = data["ke (W/m3)"]
        if "ka (W/m3)" in data:
            self.ka = data["ka (W/m3)"]
        if "Density (kg/m3)" in data:
            self.density = data["Density (kg/m3)"]
        if "Conductivity (S/m)" in data:
            self.conductivity_ref = data["Conductivity (S/m)"]
        if "Tc Conductivity (%/C)" in data:
            self.tc_sigma = data["Tc Conductivity (%/C)"]
        if "H (A/m)" in data:
            self.h_ref = data["H (A/m)"]
        if "B (T)" in data:
            self.b_ref = data["B (T)"]
        if "Calculate Eddy Current Losses" in data:
            self.eddyLosses = data["Calculate Eddy Current Losses"]
        if "Calculate Core Losses" in data:
            self.coreLosses = data["Calculate Core Losses"]
        if "Permeability Reduction (%)" in data:
            self.permeabilityReduction = data["Permeability Reduction (%)"]
        if "Magnetization Losses Increase (%)" in data:
            self.magnetizationLossesIncrease = data[
                "Magnetization Losses Increase (%)"]
        if "Linearize Initial Permeability" in data:
            self.linearizeInitialPermeability = data["Linearize Initial Permeability"]
        if "Losses" in data:
            self.losses = data["Losses"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        # print(self.ur_linear, self.ur_linear_red)

        # To check the permeablity slope that should be > 1
        # zipped = list(zip(self.b_sf, self.h_red))
        # for i in range(len(zipped) - 1):
        #     b1 = zipped[i][0]
        #     h1 = zipped[i][1]
        #     b2 = zipped[i + 1][0]
        #     h2 = zipped[i + 1][1]
        #     print((b2 - b1) / (h2 - h1) / self.u0)

        return {
            "Used": {
                "id": self.id,
                "name": self.name,
                "Stacking Factor (%)": self.stackingFactor,
                "Permeability Reduction (%)": self.permeabilityReduction,
                "Magnetization Losses Increase (%)": self.magnetizationLossesIncrease,
                "kh (W/m3)": self.kh,
                "ke (W/m3)": self.ke,
                "ka (W/m3)": self.ka,
                "Density (kg/m3)": self.density,
                "Conductivity (S/m)": self.conductivity_ref,
                "Tc Conductivity (%/C)": self.tc_sigma,
                "H (A/m)": self.h_ref,
                "B (T)": self.b_ref,
                "test": self.h,
                "H* (A/m)": self.h_red,
                "B* (T)": self.b_sf,
                "ur_max": self.ur_max,
                "ur_max*": self.ur_max_red,
                "ur": self.permeability,
                "ur*": self.permeability_red,
                "Losses": self.losses,
                "linear": self.linear,
                "Linearize Initial Permeability": self.linearizeInitialPermeability,
                "Thermal Coefficient of Linear Expansion (1/C)": self.tcle
            },
            "Options": self.data.get("Options", {})
        }
