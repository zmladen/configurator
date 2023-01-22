import math
import numpy as np
from scipy.interpolate import interp1d
from motorStudio.dcMachine import *
from motorStudio.utilities import *


class dcModel(object):
    """dcModel class which calculates the performance of the DC machine."""

    def __init__(self, data={"variation": {}, "loads": []}):
        self.data = data
        self.loads = data["loads"]
        self.machine = dcMachine(self.data["variation"])
        self.temperature = self.machine.environment.ambientTemperature
        self.__V = self.machine.commutationSystem.powerSupply.voltage
        self.__Vb = self.machine.commutationSystem.commutator.contactVoltageDrop
        self.__Tr = self.machine.mechanics.frictionTorque
        self.__D = self.machine.mechanics.damping

        self.numberOfPoints = self.data["variation"].get(
            "calculationSettings", {}).get("Number of Points", 30)
        self.minTorque = self.data["variation"].get(
            "calculationSettings", {}).get("Minimal Torque (Nm)", 0)
        self.maxTorque = self.data["variation"].get(
            "calculationSettings", {}).get("Maximal Torque (Nm)", self.Ts)

    def __initializeVariables(self, temperature):
        """Initializes the variables at the given temperature defined in the load points."""
        self.temperature = temperature
        self.data["variation"]["design"]["Environment"][
            "Ambient Temperature (C)"] = self.temperature
        validation = validateDC(dcMachine(self.data["variation"], recomputeGeometry=False), dcMachine(
            self.data["variation"]["reference"], recomputeGeometry=False))
        # Get the new nameplate data
        self.data["variation"]["design"]["Nameplate"] = validation["design"]["Nameplate"]
        self.machine = dcMachine(
            self.data["variation"], recomputeGeometry=False)
        self.machine.applyTemperature(self.temperature)

    def calculatePerformance(self):
        """Calculates maximal performance of the motor."""
        results = []

        if len(self.loads):
            for load in self.loads:
                self.__initializeVariables(load["temperature"])
                performance = self.__getPerformance()
                loadPoints = self.__getLoadPoints(load["loadPoints"])
                results.append({
                    "Temperature (C)": self.temperature,
                    "Load Points": loadPoints,
                    "Performance": performance,
                    "Performance Summary": self.__getPerformanceSummary(performance)
                })
        else:
            performance = self.__getPerformance()
            results.append({
                "Temperature (C)": self.temperature,
                "Load Points": [],
                "Performance": performance,
                "Performance Summary": self.__getPerformanceSummary(performance)
            })

        return results

    def __getPerformanceSummary(self, performance):
        maxEfficiencyData = self.__getMaxEfficiencyData(performance)
        maxOutputPowerData = self.__getMaxOutputPowerData(performance)

        torque = [item["Torque (Nm)"] for item in performance]
        speed = [item["Speed (rpm)"] for item in performance]
        current = [item["Source Current (A)"] for item in performance]

        f1 = interp1d(torque, current, fill_value='extrapolate')
        f2 = interp1d(torque, speed, fill_value='extrapolate')
        f3 = interp1d(speed, torque, fill_value='extrapolate')

        I0 = f1(0)
        n0 = f2(0)
        Ts = f3(0)
        Is = f1(Ts)

        # print(I0, n0, Ts, Is, n0 / Ts, Ts / Is)
        #
        # print(type(I0.tolist()))
        return {
            "Max. Total Efficiency (%)": maxEfficiencyData["Efficiency Total (%)"],
            "Opt. Torque (Nm)": maxEfficiencyData["Torque (Nm)"],
            "Opt. Speed (rpm)": maxEfficiencyData["Speed (rpm)"],
            "Source Current @ Max. Efficiency (A)": maxEfficiencyData["Source Current (A)"],
            "Input Power @ Max. Efficiency (W)": maxEfficiencyData["Input Power (W)"],
            "Output Power @ Max. Efficiency (W)": maxEfficiencyData["Output Power (W)"],
            "Max. Output Power": maxOutputPowerData["Output Power (W)"],
            "No-Load Speed (rpm)": n0.tolist(),
            "No-Load Source Current (A)": I0.tolist(),
            "Stall Torque (Nm)": Ts.tolist(),
            "Stall Current (A)": Is.tolist(),
            "Speed Regulation Constant Rm (rpm/Nm)": n0.tolist() / Ts.tolist(),
            "Torque Constant kt (Nm/A)": Ts.tolist() / (Is.tolist() - I0.tolist()),
        }

    def __getMaxOutputPowerData(self, performance):
        maxOutputPower = 0
        maxOutputPowerIndex = -1
        for index, result in enumerate(performance):
            if result["Output Power (W)"] > maxOutputPower:
                maxOutputPower = result["Output Power (W)"]
                maxOutputPowerIndex = index

        if maxOutputPowerIndex > -1:
            return performance[maxOutputPowerIndex]
        else:
            return None

    def __getMaxEfficiencyData(self, performance):
        maxEfficiency = 0
        maxEfficiencyIndex = -1
        for index, result in enumerate(performance):
            if result["Efficiency Total (%)"] > maxEfficiency:
                maxEfficiency = result["Efficiency Total (%)"]
                maxEfficiencyIndex = index

        if maxEfficiencyIndex > -1:
            return performance[maxEfficiencyIndex]
        else:
            return None

    def __getLoadPoints(self, loadPoints=[]):
        """Calculates specific load points"""
        data = []
        for loadPoint in loadPoints:
            speed, torque = loadPoint["speed"], loadPoint["torque"]
            result = self.__calculateMotorData(speed=speed, torque=torque)
            if result:
                result["Possible"] = True
                data.append(result)
            else:
                data.append({
                    "Speed (rpm)": speed,
                    "Torque (Nm)": torque,
                    "Possible": False,
                })

        return data

    def __getPerformance(self):
        data = []
        for speed in np.linspace(self.n0, self.n0 * 0.05, self.numberOfPoints):
            result = self.__calculateMotorData(speed=speed, torque=None)
            if result["Torque (Nm)"] <= self.minTorque:
                pass
            elif result["Torque (Nm)"] <= self.maxTorque:
                data.append(result)
            else:
                return data

        return data

    def __calculateMotorData(self, speed=None, torque=None):
        """Calculates the required motor data. The calculation is based on the  "Speed Motor Theory" (eq. 5.6).
        Trot represet all losses in terms of the additional load torque (Nm)."""

        wm = 2 * math.pi * speed / 60
        Trot = self.getAdditionalLosses(speed) / wm if wm > 0 else self.__Tr
        # Trot += self.machine.commutationSystem.commutator.brushes.frictionLosses(speed) / (2 * math.pi / speed / 60)

        if (torque == None):
            torque = (-wm * self.ke ** 2 + (self.__V - 2 * self.__Vb)
                      * self. ke) / self.Ra - Trot
            Vs = self.__V
        else:
            Vs = 2 * self.__Vb + \
                (self.Ra * (torque + Trot) + wm * self.ke**2) / self.ke

        if (speed == 0):
            return None

        dutyCycle = Vs / self.__V * 100

        if (dutyCycle > 100):
            return None

        Is = (torque + Trot) / self.ke * dutyCycle / 100
        Im = (torque + Trot) / self.ke
        Pout = wm * torque
        Pin = Is * self.__V
        commSystemLosses = self.machine.commutationSystem.getLosses(
            speed, Is, Im)
        PcommSystemTotal = commSystemLosses["Total Losses (W)"]
        Pbrushes = commSystemLosses["Brushes Losses (W)"]
        Pchoke = commSystemLosses["Choke Losses (W)"]
        Pconn = commSystemLosses["Connection Unit Losses (W)"]
        Pcable = commSystemLosses["Cable Losses (W)"]
        Psource = commSystemLosses["Source Resistance Losses (W)"]

        # Plosses = Pout + self.__getMotorLosses(speed, Is)
        # print("Vdc", self.__V, "Vs", Vs, "True Losses", Pout - Pin, "Plosses", Plosses - Pout)

        etaMotor = 100 * Pout / Pin
        etaBrushes = 100 * Pin / (Pin + Pbrushes)
        etaChoke = 100 * (Pin + Pbrushes) / (Pin + Pbrushes + Pchoke)
        etaConnection = 100 * (Pin + Pbrushes + Pchoke) / \
            (Pin + Pbrushes + Pchoke + Pconn)
        etaCable = 100 * (Pin + Pbrushes + Pchoke + Pconn) / \
            (Pin + Pbrushes + Pchoke + Pconn + Pcable)
        etaSource = 100 * (Pin + Pbrushes + Pchoke + Pconn + Pcable) / \
            (Pin + Pbrushes + Pchoke + Pconn + Pcable + Psource)
        etaCommSystem = 100 * etaBrushes / 100 * etaChoke / 100 * \
            etaConnection / 100 * etaSource / 100 * etaCable / 100

        return {
            "Efficiency Total (%)": Pout / Pin * 100,
            "Efficiency Motor (%)": etaMotor,
            "Efficiency Brushes (%)": etaBrushes,
            "Efficiency Choke (%)": etaChoke,
            "Efficiency Connection Unit (%)": etaConnection,
            "Efficiency Cable (%)": etaCable,
            "Efficiency Source (%)": etaSource,
            'Efficiency Commutation System (%)': etaCommSystem,
            "Total Losses (W)": self.__getMotorLosses(speed, Is, Im),
            "Speed (rpm)": speed,
            "Torque (Nm)": torque,
            "Temperature (C)": self.temperature,
            "Brush Current Density (A/mm2)": self.machine.commutationSystem.commutator.brushes.getCurrentDensity(Is),
            "Inner Torque (Nm)": torque + Trot,
            "Source Current (A)": Is,
            "Motor Current (A)": Im,
            "Source Voltage (V)": self.__V,
            "Input Power (W)": Pin,
            "Output Power (W)": Pout,
            "Core Losses (W)": self.coreLosses(speed=speed),
            "Friction Losses (W)": self.frictionLosses(speed=speed),
            "Damping Losses (W)": self.dampingLosses(speed=speed),
            "Conduction Losses (W)": self.conductionLosses(I=Is),
            "Duty Cycle (%)": dutyCycle,
            "Commutation System": commSystemLosses
        }

    @ property
    def ke(self):
        return self.machine.nameplate["ke (V*s/rad)"]

    @ property
    def w0(self):
        """ Theoretical no-load speed"""
        return (self.__V - 2 * self.__Vb) / self.ke - self.Ra / self.ke**2 * self.__Tr

    @ property
    def n0(self):
        """ Theoretical no-load speed (rpm)"""
        return self.w0 * 30 / math.pi

    @ property
    def R(self):
        # Armature resistance only as all other resistances are included in the nameplate!!!
        # Rs = self.machine.commutationSystem.powerSupply.resistance
        # Rc = self.machine.commutationSystem.cable.resistance
        # Rcu = self.machine.commutationSystem.connectionUnit.resistance
        # Rch = self.machine.commutationSystem.choke.equivalentResistance
        # Rb = self.machine.commutationSystem.commutator.brushes.equivalentResistance
        # print(self.machine.winding.armatureResistance)
        # (Rs + 2 * Rc + Rcu + Rch + Rb)
        return self.machine.nameplate["Resistance (Ohm)"] - self.machine.commutationSystem.totalResistance

    @ property
    def Ra(self):
        """Total resistance of the current path."""
        return self.machine.nameplate["Resistance (Ohm)"]

    @ property
    def Ts(self):
        return (self.__V - 2 * self.__Vb) / self.Ra * self.ke

    def __getMotorLosses(self, speed, Is, Im):
        return self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed) + self.conductionLosses(Im) + self.machine.commutationSystem.getLosses(speed, Is, Im)["Total Losses (W)"]

    def coreLosses(self, speed):
        volumeStator = self.machine.stator.area * self.machine.stator.stacklength
        volumeRotor = self.machine.rotor.area * self.machine.rotor.stacklength
        Bm = (self.machine.nameplate["Btooth (T)"] +
              self.machine.nameplate["Byoke (T)"]) / 2.0
        Ps = self.machine.stator.material.getSteinmetzLosses(
            volume=volumeStator, Bm=Bm, frequency=self.machine.rotor.poleNumber / 2 * speed / 60.0)
        Pr = self.machine.rotor.material.getSteinmetzLosses(
            volume=volumeRotor, Bm=Bm, frequency=self.machine.rotor.poleNumber / 2 * speed / 60.0)
        return Ps

    def frictionLosses(self, speed):
        return self.__Tr * 2 * math.pi * speed / 60.0

    def dampingLosses(self, speed):
        return self.__D * (2.0 * math.pi * speed / 60.0) ** 2

    def conductionLosses(self, I):
        return self.R * I ** 2.0

    def getAdditionalLosses(self, speed):
        # frictionLosses here are from bearings only!!!
        return self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed) + self.machine.commutationSystem.commutator.brushes.frictionLosses(speed)
