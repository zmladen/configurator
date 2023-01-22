import math
import numpy as np
from motorStudio.pmMachine import *
from motorStudio.utilities import *
from scipy.optimize import brentq
from scipy.optimize import brenth
import copy


def bisection(eq, segment, argument, app=0.3):
    a, b = segment["a"], segment["b"]
    Fa, Fb = eq(a, argument), eq(b, argument)
    if Fa * Fb > 0:
        raise Exception("No change of sign - bisection not possible")
    while b - a > app:
        x = (a + b) / 2.0
        f = eq(x, argument)
        if f * Fa > 0:
            a = x
        else:
            b = x
    return x


class dqModel(object):
    """This model calculates the motor performace in the so-called dq-coordinate system."""

    def __init__(self, data={"variation": {}, "loads": []}):
        # Have to use deep copy. Otherwise the changes on the data will reflect on the variation.
        # E.G. in the variations the last temperature used in the calculations will be shown in the GUI.
        self.data = copy.deepcopy(data)
        self.loads = data["loads"]
        self.settings = self.data["variation"].get("calculationSettings", {})
        self.variation = self.data["variation"]
        self.reference = self.data["variation"]["reference"]
        # print(self.settings)

    def __initializeVariables(self, temperature):
        self.temperature = float(temperature)
        self.variation["design"]["Environment"][
            "Ambient Temperature (C)"] = self.temperature

        useECUTemperature = self.variation["design"].get(
            "changeECUTemperature", False)
        if not useECUTemperature:
            self.variation["design"]["Control Circuit"][
                "Used"]["Temperature (C)"] = self.temperature

        validation = validate(
            pmMachine(self.variation, recomputeGeometry=False),
            pmMachine(self.reference, recomputeGeometry=False),
            settings=self.settings
        )

        # Get the new nameplate data
        self.variation["design"]["Nameplate"] = validation["design"]["Nameplate"]
        self.machine = pmMachine(
            self.variation, recomputeGeometry=False)
        self.machine.applyTemperature(self.temperature)

        # Names should be the same as in the API!
        self.pp = int(self.variation["design"]
                      ["Rotor"]["Pole Number"]) / 2
        self.nameplate = self.variation["design"]["Nameplate"]
        self.controlcircuit = self.variation["design"]["Control Circuit"]["Used"]
        self.winding = self.variation["design"]["Winding"]
        # returns error when friction is 0!
        self.frictionTorque = self.variation["design"][
            "Mechanics"]["Friction Torque (Nm)"] + 1e-17
        self.damping = self.variation[
            "design"]["Mechanics"]["Damping (Nm*s/rad)"]
        self.useNormal = self.controlcircuit["FOC Control Strategy"]["Used"]["name"] == "Normal"
        self.useMTPA = self.controlcircuit["FOC Control Strategy"]["Used"]["name"] == "Maximum Torque per Amper"
        self.useFW = self.controlcircuit["FOC Control Strategy"]["Used"]["name"] == "Flux-Weakening"

        self.R = self.nameplate["Resistance (Ohm)"] + 2 * \
            self.machine.controlcircuit.Rtransistor + self.machine.controlcircuit.Rcable
        self.Ld = self.nameplate["Ld (H)"]
        self.Lq = self.nameplate["Lq (H)"]

        self.ke = self.nameplate["ke (V*s/rad)"]
        self.psi_pm = self.ke / self.pp
        self.Vdc_link = self.controlcircuit["Power Source"]["Supply Voltage (V)"]
        self.coilConnection = self.winding["Coil Connection"]["Used"]["name"]
        self.parallelCoils = self.winding["Parallel Coils"]

        # print("ke", self.ke, "ke_t", self.ke*math.sqrt(3))
        if self.useNormal:
            self.useFW = False
            self.useMTPA = False
            self.Ld = self.Lq

        elif self.useFW:
            self.useNormal = False
            self.useMTPA = False
        else:
            self.useNormal = False
            self.useFW = False

        if self.settings:
            if "Number of Points" in self.settings:
                self.numberOfPoints = self.settings["Number of Points"]
            if "Maximal Torque (Nm)" in self.settings:
                self.maxTorque = self.settings["Maximal Torque (Nm)"]
            if "Minimal Torque (Nm)" in self.settings:
                self.minTorque = self.settings["Minimal Torque (Nm)"]
        else:
            self.numberOfPoints = 30
            self.maxTorque = (3 / math.sqrt(2) * self.ke *
                              self.machine.controlcircuit.ImaxTransistorRMS)
            self.minTorque = 0

    def calculatePerformance(self):
        results = []

        if not len(self.loads):
            self.__initializeVariables(
                self.variation["design"]["Environment"]["Ambient Temperature (C)"])
            results.append({
                "Temperature (C)": self.temperature,
                "Load Points": [],
                "Performance": self.__getPerformance(),
            })
        else:
            for load in self.loads:
                self.__initializeVariables(load["temperature"])
                performance = self.__getPerformance()  # because of the FW
                loadPoints = self.__getLoadPoints(load["loadPoints"])
                results.append({
                    "Temperature (C)": load["temperature"],
                    "Load Points": self.__filterLoadPointsOnSourceVoltageLimit(loadPoints, performance),
                    "Performance": performance,
                })

        return results

    def __getPerformance(self):
        data = []

        for torque in np.linspace(self.minTorque, self.maxTorque, self.numberOfPoints):
            result = self.__calculateMotorData(speed=None, torque=torque)
            if result:
                data.append(result)
        return data

    def __getLoadPoints(self, loadPoints):
        data = []
        for loadPoint in loadPoints:
            try:
                if self.useFW:
                    # Set useFW to false to check it FW has to be used
                    self.useFW = False
                    result = self.__calculateMotorData(
                        speed=float(loadPoint["speed"]),
                        torque=float(loadPoint["torque"]),
                    )
                    if result:
                        result["Possible"] = True
                        data.append(result)
                    else:
                        self.useFW = True
                        result = self.__calculateMotorData(
                            speed=float(loadPoint["speed"]),
                            torque=float(loadPoint["torque"]),
                        )
                        if result:
                            result["Possible"] = True
                            data.append(result)
                        else:
                            data.append(
                                {
                                    "Speed (rpm)": loadPoint["speed"],
                                    "Torque (Nm)": loadPoint["torque"],
                                    "Possible": False,
                                }
                            )
                    # Set useFW to true again the next load point
                    self.useFW = True

                else:
                    result = self.__calculateMotorData(
                        speed=float(loadPoint["speed"]),
                        torque=float(loadPoint["torque"]),
                    )
                    if result:
                        result["Possible"] = True
                        data.append(result)
                    else:
                        data.append(
                            {
                                "Speed (rpm)": loadPoint["speed"],
                                "Torque (Nm)": loadPoint["torque"],
                                "Possible": False,
                            }
                        )
            except:
                print(
                    "Load point (%srpm, %sNm) can not be reached. "
                    % (loadPoint["speed"], loadPoint["torque"])
                )
                data.append(
                    {
                        "Speed (rpm)": loadPoint["speed"],
                        "Torque (Nm)": loadPoint["torque"],
                        "Possible": False,
                    }
                )

        return data

    def __calculateMotorData(self, speed=None, torque=None):
        i, Imax, epsilon, etaECU0, etaECU, delta = 0, 150, 1e-9, 100, 100, 100
        if speed:
            # First calculate the efficiency of the ECU for the point on the performance curve!
            while i < Imax:
                self.Vdc_link = self.machine.controlcircuit.Vdc * etaECU / 100.0
                Imax = math.sqrt(self.Id(speed, torque) **
                                 2 + self.Iq(speed, torque) ** 2)
                Umax = math.sqrt(self.Ud(speed, torque) **
                                 2 + self.Uq(speed, torque) ** 2)
                cosPhi = math.cos(self.phi(speed, torque) * math.pi / 180)
                Pm = 3.0 / 2.0 * Imax * Umax * cosPhi
                Pout = torque * 2 * math.pi * speed / 60.0
                Irms, Isource, Iripple = (
                    Imax / math.sqrt(2), Pm / self.Vdc_link, Imax / math.sqrt(2.0) / 2.0)
                PAdditionallossesECU = self.machine.controlcircuit.getLosses(
                    Isource, Irms, Iripple)["Additional Losses (W)"]
                etaECU = 100 * Pm / (Pm + PAdditionallossesECU)
                delta = 100 * abs(etaECU - etaECU0) / etaECU0
                etaECU0 = etaECU
                i += 1

            maxSpeed = self.speed_max(0, self.InnerTorque(speed, torque))
            if maxSpeed and speed > maxSpeed:
                return None  # Wanted speed above the speed-torque characteristics

        else:
            while i < Imax:
                self.Vdc_link = self.machine.controlcircuit.Vdc * etaECU / 100
                # print(i, speed, torque)
                if speed == None:
                    speed = 0.001
                speed = self.speed_max(0, self.InnerTorque(speed, torque))
                if not speed:
                    return None
                Imax = math.sqrt(self.Id(speed, torque) **
                                 2 + self.Iq(speed, torque) ** 2)
                Umax = math.sqrt(self.Ud(speed, torque) **
                                 2 + self.Uq(speed, torque) ** 2)
                cosPhi = math.cos(self.phi(speed, torque) * math.pi / 180)
                Pm = 3.0 / 2.0 * Imax * Umax * cosPhi
                Pout = torque * 2 * math.pi * speed / 60.0
                Irms, Isource, Iripple = (
                    Imax / math.sqrt(2), Pm / self.Vdc_link, Imax / math.sqrt(2.0) / 2.0)
                PAdditionallossesECU = self.machine.controlcircuit.getLosses(
                    Isource, Irms, Iripple)["Additional Losses (W)"]
                etaECU = 100 * Pm / (Pm + PAdditionallossesECU)
                delta = 100 * abs(etaECU - etaECU0) / etaECU0
                # U0 = self.machine.controlcircuit.Vdc - self.machine.controlcircuit.Rsource * Isource
                # delta = 100 * (U0 - Umax * math.sqrt(3)) / (U0)
                # print("i=", i, "speed=", speed, "Umax", Umax * math.sqrt(3), "U0=", U0, "delta=", delta)
                etaECU0 = etaECU
                i += 1

        # Calculate the DC current again. Otherwise it will take higher values due to ratio scale factor
        PlossesECU = self.machine.controlcircuit.getLosses(
            Isource, Irms, Iripple)["Total Losses (W)"]
        PlossesMotor = self.__getRealMotorLosses(speed, Irms)
        Pm = Pout + PlossesMotor
        Isource = (Pm + PlossesECU) / self.machine.controlcircuit.Vdc
        electronic = self.machine.controlcircuit.getLosses(
            Isource, Irms, Iripple)
        etaMotor = 100 * Pout / Pm
        etaContacts = 100 * Pm / (Pm + electronic["Contacts Losses (W)"])
        etaPowerStage = 100 * (Pm + electronic["Contacts Losses (W)"]) / (
            Pm + electronic["Contacts Losses (W)"] + electronic["Power Stage Losses (W)"])
        etaSource = 100 * (Pm + electronic["Contacts Losses (W)"] +
                           electronic["Power Stage Losses (W)"]) / (Pm + electronic["Total Losses (W)"])
        etaECU = etaPowerStage * etaContacts / 100
        etaTotal = etaSource * etaECU * etaMotor / 1e4

        if self.coilConnection == "star":
            IcoilRMS = Irms / self.parallelCoils
        else:
            IcoilRMS = Irms / math.sqrt(3) / self.parallelCoils

        # The delta motor is calculated using the equivalent star. This means that in order to calculate the correct phase dq values of the
        # motor the dq-values of the equivalent star motor have to be scaled with sqrt(3).
        # The line values are the same as the values of the equivalent star!
        result = {
            "Electronic": electronic,
            "Efficiency Total (%)": etaTotal,
            "Efficiency Motor (%)": etaMotor,
            "Efficiency Electronics (%)": etaECU,
            "Efficiency Source (%)": etaSource,
            "Efficiency Power Stage (%)": etaPowerStage,
            "Efficiency Contacts (%)": etaContacts,
            "Total Losses (W)": PlossesMotor + PlossesECU,
            "Speed (rpm)": speed,
            "Torque (Nm)": torque,
            "Temperature (C)": self.temperature,
            "Inner Torque (Nm)": self.InnerTorque(speed, torque),
            "Iq (A)": self.Iq(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else self.Iq(speed, torque) / math.sqrt(3),
            "Id (A)": self.Id(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else self.Id(speed, torque) / math.sqrt(3),
            "Ud (V)": self.Ud(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else self.Ud(speed, torque) * math.sqrt(3),
            "Uq (V)": self.Uq(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else self.Uq(speed, torque) * math.sqrt(3),
            "Coil Current Density RMS (A/mm2)": IcoilRMS / self.machine.winding.coil.wire.surface / self.machine.winding.coil.numberOfMultipleWires,
            "Line Current MAX (A)": Imax,
            "Line Current AVG (A)": Imax * 2 / math.pi,
            "Line Current RMS (A)": Irms,
            "Line Voltage MAX (V)": Umax * math.sqrt(3),
            "Line Voltage AVG (V)": Umax * math.sqrt(3) * 2 / math.pi,
            "Line Voltage RMS (V)": Umax * math.sqrt(3) / math.sqrt(2),
            "Source Current (A)": Isource,
            "Source Voltage (V)": self.machine.controlcircuit.Vdc,
            "U0 (V)": self.machine.controlcircuit.Vdc - self.machine.controlcircuit.Rsource * Isource,
            "Capacitor Ripple Current (A)": Iripple,
            "Cos(phi)": cosPhi,
            "Input Power (W)": Pm + PlossesECU,
            "Output Power (W)": Pout,
            "Delta (deg)": self.delta(speed, torque),
            "Core Losses (W)": self.coreLosses(speed),
            "Friction Losses (W)": self.frictionLosses(speed),
            "Damping Losses (W)": self.dampingLosses(speed),
            "Conduction Losses (W)": self.conductionLosses(Irms=Imax / math.sqrt(2)),
            # sqrt(3) because of the star connection
            "Duty Cycle (%)": Umax / (self.Vdc_link / math.sqrt(3)) * 100,
            "Line Values": {
                "Iq (A)": self.Iq(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else 1 / math.sqrt(3) * self.Iq(speed, torque),
                "Id (A)": self.Id(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else 1 / math.sqrt(3) * self.Id(speed, torque),
                "Ud (V)": self.Ud(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else math.sqrt(3) * self.Ud(speed, torque),
                "Uq (V)": self.Uq(speed, torque) if self.machine.winding.phaseConnection["name"] == "star" else math.sqrt(3) * self.Uq(speed, torque),
                "Line Voltage MAX (V)": Umax if self.machine.winding.phaseConnection["name"] == "delta" else math.sqrt(3) * Umax,
                "Line Voltage AVG (V)": Umax * 2 / math.pi if self.machine.winding.phaseConnection["name"] == "delta" else math.sqrt(3) * Umax * 2 / math.pi,
                "Line Voltage RMS (V)": Umax / math.sqrt(2) if self.machine.winding.phaseConnection["name"] == "delta" else math.sqrt(3) * Umax / math.sqrt(2),
            }
        }
        return result

    def __filterLoadPointsOnSourceVoltageLimit(self, loadPoints, performance):
        # Gets the load point where the voltage drop on the source resistance is larger than 45%.
        torqueLimit = None
        sortedPerformance = sorted(
            performance, key=lambda item: item["U0 (V)"], reverse=False)
        for item in sortedPerformance:
            if item["U0 (V)"] / self.machine.controlcircuit.Vdc < 0.45:
                torqueLimit = item["Torque (Nm)"]

        if not torqueLimit:
            return loadPoints

        filteredLoadPoints = []
        for item in loadPoints:
            if item["Torque (Nm)"] < torqueLimit:
                filteredLoadPoints.append(item)
            else:
                filteredLoadPoints.append(
                    {
                        "Speed (rpm)": item["Speed (rpm)"],
                        "Torque (Nm)": item["Torque (Nm)"],
                        "Voltage Limit": True,
                    }
                )

        return filteredLoadPoints

    def __getFakeMotorLosses(self, speed, Irms):
        return (
            self.frictionLosses(speed)
            + self.dampingLosses(speed)
            + self.coreLosses(speed)
            + self.conductionCableTransistorLosses(Irms)
        )

    def __getRealMotorLosses(self, speed, Irms):
        return (
            self.frictionLosses(speed)
            + self.dampingLosses(speed)
            + self.coreLosses(speed)
            + self.conductionLosses(Irms)
        )

    def coreLosses(self, speed):
        volumeStator = self.machine.stator.area * self.machine.stator.stacklength
        volumeRotor = self.machine.rotor.area * self.machine.rotor.stacklength
        Bm = (self.nameplate["Btooth (T)"] + self.nameplate["Byoke (T)"]) / 2.0
        Ps = self.machine.stator.material.getSteinmetzLosses(
            volume=volumeStator, Bm=Bm, frequency=self.pp * speed / 60.0)
        Pr = self.machine.rotor.material.getSteinmetzLosses(
            volume=volumeRotor, Bm=Bm, frequency=self.pp * speed / 60.0)
        return Ps  # + Pr

    def frictionLosses(self, speed):
        return self.frictionTorque * 2 * math.pi * speed / 60.0

    def dampingLosses(self, speed):
        return self.damping * (2.0 * math.pi * speed / 60.0) ** 2

    def conductionLosses(self, Irms):
        return 3 * self.nameplate["Resistance (Ohm)"] * Irms ** 2.0

    def conductionCableTransistorLosses(self, Irms):
        return 3 * self.R * Irms ** 2.0

    def InnerTorque(self, speed, shafttorque):
        """Calculates inner torque of the machine (Nm)."""
        # print(speed, shafttorque)
        if speed > 0:
            # print(speed, shafttorque, shafttorque + (self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed)) / (2.0 * math.pi * speed / 60.0))
            return shafttorque + (self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed)) / (2.0 * math.pi * speed / 60.0)
        else:
            # return shafttorque + (self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed)) / (2.0 * math.pi * speed / 60.0)
            return shafttorque + self.frictionTorque

    def f(self, Iq_mtpa, Tn):
        return (
            math.pow(Iq_mtpa, 4) * math.pow(self.Lq - self.Ld, 2)
            + Tn * Iq_mtpa * self.psi_pm
            - math.pow(Tn, 2)
        )

    def f_prim(self, Iq_mtpa, Tn):
        return (
            4 * math.pow(Iq_mtpa, 3) * math.pow(self.Lq -
                                                self.Ld, 2) + Tn * self.psi_pm
        )

    def Iq_mtpa(self, speed, shafttorque):
        # Determined iteratively with Newton’s method
        Tn = self.InnerTorque(speed, shafttorque) / (1.5 * self.pp)
        Iq_mtpa_prev = self.InnerTorque(speed, shafttorque) / (
            1.5 * self.pp * self.psi_pm
        )
        Iq_mtpa = 0
        epsilon = 1e-6
        delta = 1
        i = 1

        while delta > epsilon and i < 10:
            Iq_mtpa = Iq_mtpa_prev - self.f(Iq_mtpa_prev, Tn) / self.f_prim(
                Iq_mtpa_prev, Tn
            )
            delta = abs(Iq_mtpa - Iq_mtpa_prev)
            Iq_mtpa_prev = Iq_mtpa
            i += 1

        return Iq_mtpa

    def Id_mtpa(self, speed, shafttorque):
        # Calculate d-current component for the MTPA approach
        e1 = self.psi_pm - math.sqrt(
            math.pow(self.psi_pm, 2)
            + 4
            * math.pow(self.Lq - self.Ld, 2)
            * math.pow(self.Iq_mtpa(speed, shafttorque), 2)
        )
        e2 = 2 * (self.Lq - self.Ld)

        if self.Lq != self.Ld:
            return e1 / e2
        else:
            return 0

    def Iq_fw(self, speed, shafttorque):
        # M_mtpa = M_fw
        # double e1 = (self.Lq - self.Ld) * (Id_fw(speed, shafttorque) - Id_mtpa(speed, shafttorque)) * Iq_mtpa(speed, shafttorque);
        # double e2 = self.psi_pm + (self.Ld - self.Lq) * Id_fw(speed, shafttorque);
        # double deltaIq = e1 / e2;
        # return Iq_mtpa(speed, shafttorque) + deltaIq;
        return self.InnerTorque(speed, shafttorque) / (
            1.5
            * self.pp
            * (self.psi_pm + (self.Ld - self.Lq) * self.Id_fw(speed, shafttorque))
        )

    def Id_fw(self, speed, shafttorque):
        # Calculate d-current component for the Flux Weakning (FW) approach.
        # The Iq current is from the mtpa approach!

        p1 = self.omega(speed)
        p2 = self.Ld * self.omega(speed) * self.psi_pm
        p3 = self.R * self.Iq_mtpa(speed, shafttorque) * (self.Ld - self.Lq)
        p4 = math.pow(self.R, 2) + math.pow(self.omega(speed) * self.Ld, 2)
        p = p1 * (p2 + p3) / p4

        q1 = self.psi_pm * (
            2 * self.R * self.Iq_mtpa(speed, shafttorque) * self.omega(speed)
            + math.pow(self.omega(speed), 2) * self.psi_pm
        )
        q2 = math.pow(self.omega(speed) * self.Lq, 2) + math.pow(self.R, 2)
        q3 = math.pow(self.Iq_mtpa(speed, shafttorque), 2)
        q4 = math.pow(
            self.Vdc_link / math.sqrt(3), 2
        )  # divided by sqrt(3) because of the star connection of the motor. Can be wrong!!!
        q5 = math.pow(self.R, 2) + math.pow(self.omega(speed) * self.Ld, 2)
        q = (q1 + q2 * q3 - q4) / q5

        Id1 = -p + math.sqrt(abs(math.pow(p, 2) - q))
        Id2 = -p - math.sqrt(abs(math.pow(p, 2) - q))

        if abs(Id1) <= abs(Id2):
            return Id1
        else:
            return Id2

        return Id1

    def Iq(self, speed, shafttorque):
        if self.useMTPA:
            return self.Iq_mtpa(speed, shafttorque)
        elif self.useFW:
            return self.Iq_fw(speed, shafttorque)
        else:
            return self.InnerTorque(speed, shafttorque) / (1.5 * self.pp * self.psi_pm)

    def Id(self, speed, shafttorque):
        if self.useMTPA:
            return self.Id_mtpa(speed, shafttorque)
        elif self.useFW:
            return self.Id_fw(speed, shafttorque)
        else:
            return 0

    def Urd(self, speed, shafttorque):
        # Peak value in [V]
        return self.R * self.Id(speed, shafttorque)

    def Urq(self, speed, shafttorque):
        # Peak value in [V]
        return self.R * self.Iq(speed, shafttorque)

    def Uld(self, speed, shafttorque):
        # Peak value in [V]
        return (
            self.pp
            * 2.0
            * math.pi
            * speed
            / 60.0
            * self.Ld
            * self.Id(speed, shafttorque)
        )

    def Ulq(self, speed, shafttorque):
        # Peak value in [V]
        return (
            self.pp
            * 2.0
            * math.pi
            * speed
            / 60.0
            * self.Lq
            * self.Iq(speed, shafttorque)
        )

    def Ud(self, speed, shafttorque):
        return self.Urd(speed, shafttorque) - self.Ulq(speed, shafttorque)

    def Uq(self, speed, shafttorque):
        return self.Urq(speed, shafttorque) + self.Uld(speed, shafttorque) + self.Uemf(speed)

    def Uemf(self, speed):
        return self.pp * 2.0 * math.pi * speed / 60.0 * self.psi_pm

    def U(self, speed, shafttorque):
        # Peak phase voltage in [v]
        return math.sqrt(
            math.pow(self.Ud(speed, shafttorque), 2)
            + math.pow(self.Uq(speed, shafttorque), 2)
        )

    def I(self, speed, shafttorque):
        # Peak phase current in [v]
        return math.sqrt(
            math.pow(self.Id(speed, shafttorque), 2)
            + math.pow(self.Iq(speed, shafttorque), 2)
        )

    def gamma(self, speed, shafttorque):
        # Angle of the phase current, relative to the EMF (q-Axis) [deg]
        return (
            math.atan(self.Id(speed, shafttorque) /
                      self.Iq(speed, shafttorque))
            * 180.0
            / math.pi
        )

    def delta(self, speed, shafttorque):
        # Angle of the phase voltage, relative to the EMF (q-Axis) [deg]
        # return math.asin((Urd(speed, shafttorque) - Ulq(speed, shafttorque)) / math.sqrt(math.pow(Ud(speed, shafttorque), 2) + math.pow(Uq(speed, shafttorque), 2))) * 180 / math.pi

        if self.Uq(speed, shafttorque) >= 0:
            return (
                math.atan(self.Ud(speed, shafttorque) /
                          self.Uq(speed, shafttorque))
                * 180
                / math.pi
            )
        else:
            return (
                -180
                + math.atan(self.Ud(speed, shafttorque) /
                            self.Uq(speed, shafttorque))
                * 180
                / math.pi
            )

    def phi(self, speed, shafttorque):
        # Angle between phase voltage and phase current [deg]. Important for the power factor calculation.
        return self.delta(speed, shafttorque) - self.gamma(speed, shafttorque)

    def omega(self, speed):
        return self.pp * 2.0 * math.pi * speed / 60

    def f_D(self, speed, shafttorque):
        # Calculates the determinant of the Id current for the flux weakning control
        # Used to determin the max speed in the fw control.
        p1 = self.omega(speed)
        p2 = self.Ld * self.omega(speed) * self.psi_pm
        p3 = self.R * self.Iq_mtpa(speed, shafttorque) * (self.Ld - self.Lq)
        p4 = math.pow(self.R, 2) + math.pow(self.omega(speed) * self.Ld, 2)
        p = p1 * (p2 + p3) / p4

        q1 = self.psi_pm * (
            2 * self.R * self.Iq_mtpa(speed, shafttorque) * self.omega(speed)
            + math.pow(self.omega(speed), 2) * self.psi_pm
        )
        q2 = math.pow(self.omega(speed) * self.Lq, 2) + math.pow(self.R, 2)
        q3 = math.pow(self.Iq_mtpa(speed, shafttorque), 2)
        q4 = math.pow(self.Vdc_link / math.sqrt(3), 2)
        q5 = math.pow(self.R, 2) + math.pow(self.omega(speed) * self.Ld, 2)
        q = (q1 + q2 * q3 - q4) / q5

        return math.pow(p, 2) - q

    def omega_max_mtpa(self, speed, shafttorque):
        # Calculates the maximal electrical speed of the motor [rad/s]
        p1 = self.R * self.Iq_mtpa(speed, shafttorque)
        p2 = self.Ld * self.Id_mtpa(speed, shafttorque) + self.psi_pm
        p3 = (
            self.R
            * self.Id_mtpa(speed, shafttorque)
            * self.Lq
            * self.Iq_mtpa(speed, shafttorque)
        )
        p4 = math.pow(self.Lq * self.Iq_mtpa(speed, shafttorque), 2)
        p5 = math.pow(self.Ld * self.Id_mtpa(speed,
                      shafttorque) + self.psi_pm, 2)
        p = (p1 * p2 - p3) / (p4 + p5)

        q1 = math.pow(self.R, 2) * (
            math.pow(self.Id_mtpa(speed, shafttorque), 2)
            + math.pow(self.Iq_mtpa(speed, shafttorque), 2)
        ) - math.pow(self.Vdc_link / math.sqrt(3), 2)
        q = q1 / (p4 + p5)

        w1 = -p + math.sqrt(math.pow(p, 2) - q)
        w2 = -p - math.sqrt(math.pow(p, 2) - q)

        if w1 >= 0:
            return w1
        else:
            return w2

    def omega_max_fw1(self, speed, shafttorque):
        # Currently not used
        # simplified approach from Armin (see eq. 6 in IPM DCT Grote Mayer)
        id0 = -self.psi_pm / self.Ld
        return (
            (self.Vdc_link / math.sqrt(3) + self.R * id0)
            / self.Lq
            / self.Iq_mtpa(speed, shafttorque)
        )

    def omega_max_fw(self, speed, shafttorque):
        # speed = brenth(self.f_D, 0, 100e3, args=shafttorque, xtol=1e-3, rtol=1e-3, maxiter=15)
        speed = bisection(self.f_D, {"a": 0, "b": 100e3}, shafttorque, 0.01)
        return 1 * 2.0 * math.pi * speed / 60.0 * self.pp

    def speed_max(self, speed, shafttorque):

        try:
            if self.useFW:
                speed = (
                    self.omega_max_fw(speed, shafttorque)
                    / self.pp
                    * 60.0
                    / (2.0 * math.pi)
                )
            else:
                speed = (
                    self.omega_max_mtpa(speed, shafttorque)
                    / self.pp
                    * 60.0
                    / (2.0 * math.pi)
                )

            if speed < 0:
                return None
            else:
                return speed
        except:
            print("An exception occurred when calculating maximal speed of the motor.")
            return None
