import math
from motorStudio.pmMachine import *
from motorStudio.utilities import *
from scipy import interpolate
from scipy.interpolate import UnivariateSpline
from scipy.misc import derivative
import numpy as np
import copy

cdef double DEG2RAD = math.pi / 180
cdef double RAD2DEG = 180 / math.pi

cdef class blckModel(object):
    """This model calculates the motor performace in the so-called dq-coordinate system."""

    cdef int pp, numberOfPoints, totalTimeSteps, parallelCoils
    cdef str coilConnection
    cdef double timeStep, zeta, temperature
    cdef double Ia_phase, Ib_phase, Ic_phase
    cdef double Ia_phase0, Ib_phase0, Ic_phase0
    cdef double dIa_phase, dIb_phase, dIc_phase
    cdef Ia_phase_off, Ib_phase_off, Ic_phase_off
    cdef double Ua_phase, Ub_phase, Uc_phase, Um
    cdef int Q1, Q2, Q3, Q4, Q5, Q6
    cdef int D1, D2, D3, D4, D5, D6
    cdef double Ea, Eb, Ec, Lg0, Lg2
    cdef double Laa, Lbb, Lcc, Lab, Lbc, Lca
    cdef double Laa0, Lbb0, Lcc0, Lab0, Lbc0, Lca0
    cdef double dLaa, dLbb, dLcc, dLab, dLbc, dLca

    cdef dict nameplate, inducedVoltage, inductances, data, settings, controlcircuit, winding
    cdef double Vdc, frictionTorque, momentOfInertia, damping, refSpeed, R, maxTorque, minTorque, maxSpeed, minSpeed
    cdef useReluctance, machine, cn_EMF, cn_L, cn_M
    cdef list loads

    def __init__(self, data={"variation": {}, "loads": []}):

        self.data = copy.deepcopy(data)
        self.loads = self.data["loads"]
        self.settings = data["variation"].get("calculationSettings", None)

        # Help variables
        self.timeStep, self.zeta = 0, 0
        self.Ia_phase, self.Ib_phase, self.Ic_phase = 0, 0, 0
        self.Ia_phase0, self.Ib_phase0, self.Ic_phase0 = 0, 0, 0
        self.dIa_phase, self.dIb_phase, self.dIc_phase = 0, 0, 0
        self.Ia_phase_off, self.Ib_phase_off, self.Ic_phase_off = True, True, True
        self.Ua_phase, self.Ub_phase, self.Uc_phase, self.Um = 0, 0, 0, 0
        self.Q1, self.Q2, self.Q3, self.Q4, self.Q5, self.Q6 = 0, 0, 0, 0, 0, 0
        self.D1, self.D2, self.D3, self.D4, self.D5, self.D6 = 0, 0, 0, 0, 0, 0
        self.Ea, self.Eb, self.Ec = 0, 0, 0
        self.Laa, self.Lbb, self.Lcc, self.Lab, self.Lbc, self.Lca = 0, 0, 0, 0, 0, 0
        self.Laa0, self.Lbb0, self.Lcc0, self.Lab0, self.Lbc0, self.Lca0 = 0, 0, 0, 0, 0, 0
        self.dLaa, self.dLbb, self.dLcc, self.dLab, self.dLbc, self.dLca = 0, 0, 0, 0, 0, 0

    def __initializeVariables(self, temperature):
        self.temperature = float(temperature)
        self.data["variation"]["design"]["Environment"]["Ambient Temperature (C)"] = self.temperature
        useECUTemperature = self.data["variation"]["design"].get("changeECUTemperature", False)
        if not useECUTemperature:
            self.data["variation"]["design"]["Control Circuit"]["Used"]["Temperature (C)"] = self.temperature

        validation = validate(pmMachine(self.data["variation"], recomputeGeometry=False), pmMachine(self.data["variation"]['reference'], recomputeGeometry=False))

        # Get the new nameplate data
        self.data["variation"]["design"]["Nameplate"] = validation["design"]["Nameplate"]
        self.machine = pmMachine(self.data["variation"], recomputeGeometry=False)
        self.machine.applyTemperature(self.temperature)

        self.controlcircuit = self.data["variation"]["design"]["Control Circuit"]['Used']
        self.winding = self.data["variation"]["design"]["Winding"]
        self.nameplate = self.data["variation"]["design"]["Nameplate"]
        self.Vdc = self.machine.controlcircuit.Vdc
        self.pp = int(self.data["variation"]["design"]["Rotor"]["Pole Number"]) / 2
        self.useReluctance = True
        self.frictionTorque = self.data["variation"]["design"]["Mechanics"]["Friction Torque (Nm)"]
        self.momentOfInertia = self.data["variation"]["design"]["Mechanics"]["Moment of Inertia (kg*m^2)"]
        self.damping = self.data["variation"]["design"]["Mechanics"]["Damping (Nm*s/rad)"]
        self.coilConnection = self.winding['Coil Connection']['Used']['name']
        self.parallelCoils = self.winding['Parallel Coils']

        self.R = self.nameplate['Resistance (Ohm)'] + 2 * self.machine.controlcircuit.Rtransistor + self.machine.controlcircuit.Rcable
        self.inducedVoltage = self.nameplate["Induced Voltage"]
        self.refSpeed = self.inducedVoltage["speed (rpm)"]
        # See "Speed Motor Theory (page. 2.54)"
        self.Lg0 = (self.nameplate['Ld (H)'] + self.nameplate['Lq (H)']) / 3.0
        self.Lg2 = (self.nameplate['Ld (H)'] - self.nameplate['Lq (H)']) / 3.0
        self.cn_EMF = self.nameplate["Fourier Coefficients EMF"]
        # maxSpeed defines the speed-torque curve limits
        self.maxSpeed = self.nameplate["Maximal Speed (rpm)"]

        if (self.settings):
            if "Number of Points" in self.settings:
                self.numberOfPoints = self.settings["Number of Points"]
            if "Total Time Steps" in self.settings:
                self.totalTimeSteps = self.settings["Total Time Steps"]
            if "Maximal Torque (Nm)" in self.settings:
                self.maxTorque = self.settings["Maximal Torque (Nm)"]
            if "Minimal Torque (Nm)" in self.settings:
                self.minTorque = self.settings["Minimal Torque (Nm)"]
        else:
            self.totalTimeSteps = 9000
            self.numberOfPoints = 20
            self.maxTorque = self.nameplate['Maximal Torque (Nm)']
            self.minTorque = self.nameplate['Minimal Torque (Nm)']

        self.maxSpeed = self.nameplate['Maximal Speed (rpm)']
        self.minSpeed = self.nameplate['Minimal Speed (rpm)']

    def calculatePerformance(self):
        results = []

        if not len(self.loads):
            self.__initializeVariables(self.data["variation"]["design"]["Environment"]["Ambient Temperature (C)"])
            results.append({
                "Temperature (C)": self.temperature,
                "Load Points": [],
                "Performance": self.__getPerformance()
            })
        else:
            for load in self.loads:
                self.__initializeVariables(load["temperature"])
                performance = self.__getPerformance()
                loadPoints = self.__getLoadPoints(performance, load["loadPoints"])

                results.append({
                    "Temperature (C)": load["temperature"],
                    "Load Points": self.__filterLoadPointsOnSourceVoltageLimit(loadPoints, performance),
                    "Performance": performance
                })

        return results

    def __getPerformance(self):
        data = []

        for speed in np.linspace(self.maxSpeed, self.minSpeed, self.numberOfPoints):
            result = self.__calculateMotorData(loadSpeed=speed, loadTorque=None)

            if result:
              if result["Torque (Nm)"] < self.minTorque:
                pass
              elif result["Torque (Nm)"] < self.maxTorque:
                data.append(result)
              else:
                return data

        return data

    def __getLoadPoints(self, performance, loadPoints):
        data = []
        for loadPoint in loadPoints:
            index = self.__getIndexOfLargerLoadPoint(loadPoint, performance)

            if index == None:
                data.append({"Speed (rpm)": loadPoint["speed"], "Torque (Nm)": loadPoint["torque"], "Possible": False})
            else:
                result = self.__getInterpolatedData(loadPoint["speed"], loadPoint["torque"], performance, index)
                result['Possible'] = True
                data.append(result)

        return data

    def __filterLoadPointsOnSourceVoltageLimit(self, loadPoints, performance):
        # Gets the load point where the voltage drop on the source resistance is larger than 45%.
        torqueLimit = None
        sortedPerformance = sorted(performance, key=lambda item: item['U0 (V)'], reverse=False)
        for item in sortedPerformance:
            if item['U0 (V)'] / self.machine.controlcircuit.Vdc < 0.45:
                torqueLimit = item['Torque (Nm)']

        if not torqueLimit:
            return loadPoints

        filteredLoadPoints = []
        for item in loadPoints:
            if item['Torque (Nm)'] < torqueLimit:
                filteredLoadPoints.append(item)
            else:
                filteredLoadPoints.append({"Speed (rpm)": item["Speed (rpm)"], "Torque (Nm)": item["Torque (Nm)"], "Voltage Limit": True})

        return filteredLoadPoints

    def __calculateMotorData(self, loadSpeed=None, loadTorque=None):
      i, Nmax, epsilon, etaECU0, etaECU, delta = 0, 10, 1E-2, 1, 100, 100
      PlossesMotor, PlossesECU = 0, 0

      # To include the effects of electronic. Results in the speed reduction!
      while (i < Nmax and delta > epsilon):
          self.Vdc = self.controlcircuit["Power Source"]['Supply Voltage (V)'] * etaECU / 100
          speed = loadSpeed * etaECU / 100

          if speed<=self.minSpeed:
              return None

          (Isource, Imax, Iavg, Irms, Iripple, Tshaft) = self.solveSpeed(loadSpeed=speed, numberOfPeriods=2, totalTimeSteps=self.totalTimeSteps)
          if Tshaft <= 0:
            etaECU = 100
          Pout = Tshaft * 2 * math.pi * speed / 60.0
          PAdditionallossesECU = self.machine.controlcircuit.getLosses(Isource, Irms, Iripple)["Additional Losses (W)"]
          PFakelossesMotor = self.__getFakeMotorLosses(speed, Irms)
          etaECU = 100 * (Pout + PFakelossesMotor) / (Pout + PFakelossesMotor + PAdditionallossesECU)
          delta = 100 * abs(etaECU - etaECU0) / etaECU0
          etaECU0 = etaECU
          i += 1

      PlossesECU = self.machine.controlcircuit.getLosses(Isource, Irms, Iripple)["Total Losses (W)"]
      PlossesMotor = self.__getRealMotorLosses(speed, Irms)
      Isource = (Pout + PlossesMotor + PlossesECU) / self.machine.controlcircuit.Vdc
      electronic = self.machine.controlcircuit.getLosses(Isource, Irms, Iripple)
      etaMotor = 100 * Pout / (Pout + PlossesMotor)
      etaContacts = 100 * (Pout + PlossesMotor) / (Pout + PlossesMotor + electronic["Contacts Losses (W)"])
      etaPowerStage = 100 * (Pout + PlossesMotor + electronic["Contacts Losses (W)"]) / (Pout + PlossesMotor + electronic["Contacts Losses (W)"] + electronic["Power Stage Losses (W)"])
      etaSource = 100 * (Pout + PlossesMotor + electronic["Contacts Losses (W)"] + electronic["Power Stage Losses (W)"]) / (Pout + PlossesMotor + electronic["Total Losses (W)"])
      etaECU = etaPowerStage * etaContacts / 100
      etaTotal = etaSource * etaECU * etaMotor / 1E4

      if self.coilConnection == "star":
          IcoilRMS = Irms / self.parallelCoils
      else:
          IcoilRMS = Irms / math.sqrt(3) / self.parallelCoils

      if Tshaft >= 0:
        return {
            'Electronic': electronic,
            'Efficiency Total (%)': etaTotal,
            'Efficiency Motor (%)': etaMotor,
            'Efficiency Electronics (%)': etaECU,
            'Efficiency Source (%)': etaSource,
            'Efficiency Power Source (%)': etaPowerStage,
            'Efficiency Contacts (%)': etaContacts,
            'Total Losses (W)': PlossesMotor + PlossesECU,
            'Speed (rpm)': speed,
            'Torque (Nm)': Tshaft,
            "Temperature (C)": self.temperature,
            'Inner Torque (Nm)': self.__getInnerTorqueFromShaftTorque(speed, Tshaft),
            'Iq (A)': None,
            'Id (A)': None,
            'Ud (V)': None,
            'Uq (V)': None,
            'Coil Current Density RMS (A/mm2)': IcoilRMS / self.machine.winding.coil.wire.surface,
            'Line Current MAX (A)': Imax,
            'Line Current AVG (A)': Iavg,
            'Line Current RMS (A)': Irms,
            'Line Voltage MAX (V)': None,
            'Line Voltage AVG (V)': None,
            'Line Voltage RMS (V)': None,
            'Source Current (A)': Isource,
            'Source Voltage (V)': self.controlcircuit["Power Source"]['Supply Voltage (V)'],
            'U0 (V)': self.machine.controlcircuit.Vdc - self.machine.controlcircuit.Rsource * Isource,
            'Capacitor Ripple Current (A)': Iripple,
            'Cos(phi)': None,
            'Input Power (W)': Pout + PlossesMotor + PlossesECU,
            'Output Power (W)': Pout,
            'Delta (deg)': None,
            'Core Losses (W)': self.coreLosses(speed),
            'Friction Losses (W)': self.frictionLosses(speed),
            'Damping Losses (W)': self.dampingLosses(speed),
            'Conduction Losses (W)': self.conductionLosses(Irms=Imax / math.sqrt(2)),
        }
      else:
        return None

    def __getIndexOfLargerLoadPoint(self, loadPoint, performance):
        """Takes into account the speed related losses. This is why the inner torque is used as a reference."""

        torque, speed = loadPoint['torque'], loadPoint['speed']
        __innerTorque = self.__getInnerTorqueFromShaftTorque(speed, torque)

        innerTorques = []
        for i in range(len(performance)):
            innerTorques.append(performance[i]['Inner Torque (Nm)'])

        t = np.array(innerTorques)
        index = np.argmax(t >= __innerTorque)  # returns 0 if condiction is not fulfilled.

        if index == 0:
            return None
        else:
            __speed = np.interp(__innerTorque, [performance[index - 1]['Inner Torque (Nm)'], performance[index - 1]['Inner Torque (Nm)']], [performance[index]['Speed (rpm)'], performance[index]['Speed (rpm)']])

            if speed > __speed:
                return None
            else:
                return index

    def __getInterpolatedData(self, speed, torque, performance, index):
        # Speed related losses are calculated again
        # DC current calculated iteratively
        p0, p1 = performance[index - 1], performance[index]
        __innerTorque = self.__getInnerTorqueFromShaftTorque(speed, torque)
        __speed = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Speed (rpm)'], p1['Speed (rpm)']])
        Imax = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Line Current MAX (A)'], p1['Line Current MAX (A)']])
        Iavg = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Line Current AVG (A)'], p1['Line Current AVG (A)']])
        Irms = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Line Current RMS (A)'], p1['Line Current RMS (A)']])
        Iripple = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Capacitor Ripple Current (A)'], p1['Capacitor Ripple Current (A)']])
        __sourceCurrent = np.interp(__innerTorque, [p0['Inner Torque (Nm)'], p1['Inner Torque (Nm)']], [p0['Source Current (A)'], p1['Source Current (A)']])
        dutyCycle = speed / __speed
        Pout = torque * 2 * math.pi * speed / 60.0

        i, Nmax, epsilon, Isource0, delta  = 0, 10, 1E-2, __sourceCurrent * dutyCycle, 100
        # Somehow helps convergence by hig DC currents and high source resistance losses
        ratio = 1#__sourceCurrent / Isource0

        while (delta > 0.01):
          PAdditionallossesECU = self.machine.controlcircuit.getLosses(Isource0, Irms, Iripple)["Additional Losses (W)"]
          PFakelossesMotor = self.__getFakeMotorLosses(speed, Irms)
          Isource = (Pout + PFakelossesMotor + PAdditionallossesECU * ratio) / self.machine.controlcircuit.Vdc
          delta = abs(Isource - Isource0) / Isource0
          Isource0 = Isource
          ratio = 1#__sourceCurrent / Isource0

        PlossesECU = self.machine.controlcircuit.getLosses(Isource, Irms, Iripple)["Total Losses (W)"]
        PlossesMotor = self.__getRealMotorLosses(speed, Irms)
        electronic = self.machine.controlcircuit.getLosses(Isource, Irms, Iripple)
        etaMotor = 100 * Pout / (Pout + PlossesMotor)
        etaContacts = 100 * (Pout + PlossesMotor) / (Pout + PlossesMotor + electronic["Contacts Losses (W)"])
        etaPowerStage = 100 * (Pout + PlossesMotor + electronic["Contacts Losses (W)"]) / (Pout + PlossesMotor + electronic["Contacts Losses (W)"] + electronic["Power Stage Losses (W)"])
        etaSource = 100 * (Pout + PlossesMotor + electronic["Contacts Losses (W)"] + electronic["Power Stage Losses (W)"]) / (Pout + PlossesMotor + electronic["Total Losses (W)"])
        etaECU = etaPowerStage * etaContacts / 100
        etaTotal = etaSource * etaECU * etaMotor / 1E4

        # Correct the current so that the input power corresponds to voltage and total efficiency.
        # Otherwise small deviation can occure due to interpolation accuracy.
        Isource = Pout / etaTotal * 100 / self.controlcircuit["Power Source"]['Supply Voltage (V)']
        
        if self.coilConnection == "star":
            IcoilRMS = Irms / self.parallelCoils
        else:
            IcoilRMS = Irms / math.sqrt(3) / self.parallelCoils

        return {
            'Electronic': electronic,
            'Efficiency Total (%)': etaTotal,
            'Efficiency Motor (%)': etaMotor,
            'Efficiency Electronics (%)': etaECU,
            'Efficiency Source (%)': etaSource,
            'Efficiency Power Source (%)': etaPowerStage,
            'Efficiency Contacts (%)': etaContacts,
            'Total Losses (W)': PlossesMotor + PlossesECU,
            'Speed (rpm)': speed,
            'Torque (Nm)': torque,
            "Temperature (C)": self.temperature,
            'Inner Torque (Nm)': self.__getInnerTorqueFromShaftTorque(speed, torque),
            'Iq (A)': None,
            'Id (A)': None,
            'Ud (V)': None,
            'Uq (V)': None,
            'Coil Current Density RMS (A/mm2)': IcoilRMS / self.machine.winding.coil.wire.surface / self.machine.winding.coil.numberOfMultipleWires,
            'Line Current MAX (A)': Imax,
            'Line Current AVG (A)': Iavg,
            'Line Current RMS (A)': Irms,
            'Line Voltage MAX (V)': None,
            'Line Voltage AVG (V)': None,
            'Line Voltage RMS (V)': None,
            'Source Current (A)': Isource,
            'Source Voltage (V)': self.controlcircuit["Power Source"]['Supply Voltage (V)'],
            'U0 (V)': self.machine.controlcircuit.Vdc - self.machine.controlcircuit.Rsource * Isource,
            'Capacitor Ripple Current (A)': Iripple,
            'Cos(phi)': None,
            'Input Power (W)': Pout + PlossesMotor + PlossesECU,
            'Output Power (W)': Pout,
            'Delta (deg)': None,
            'Core Losses (W)': self.coreLosses(speed),
            'Friction Losses (W)': self.frictionLosses(speed),
            'Damping Losses (W)': self.dampingLosses(speed),
            'Conduction Losses (W)': self.conductionLosses(Irms=Irms),
            'Duty Cycle (%)': dutyCycle * 100
        }

    cdef solveTorque(self, dict electronic, double loadTorque, int numberOfPeriods, int totalTimeSteps):

        self.timeStep = 1e-5
        test1, test2, test3 = [], [], []
        test4, test5, test6 = [], [], []
        time, speed, angleElectric, angleMechanic, phaseCurrentA = [], [], [], [], []
        phaseCurrentB, phaseCurrentC, innerTorque, shaftTorque, sourceCurrent = [], [], [], [], []

        cdef int n = 0
        cdef double __time = 0
        cdef double __speed = 0
        cdef double __position = 0
        cdef __innerTorque = 0

        cdef int Nskip = 10  # No need to reaf emf so fine! Only derivatives!

        __speedPrev = 1E15
        i = 0
        while (i < 1E6):

            __time += self.timeStep
            __position += RAD2DEG * 2 * self.pp * math.pi * __speed / 60 * self.timeStep
            self.zeta = __position % 360

            if n % Nskip == 0:
                self.Ea = self.__Ea(__speed, __position)
                self.Eb = self.__Eb(__speed, __position)
                self.Ec = self.__Ec(__speed, __position)

            self.Laa = self.__Laa(__speed, __time)
            self.Lbb = self.__Lbb(__speed, __time)
            self.Lcc = self.__Lcc(__speed, __time)
            self.Lab = self.__Lab(__speed, __time)
            self.Lbc = self.__Lbc(__speed, __time)
            self.Lca = self.__Lca(__speed, __time)

            # if n % Nskip == 0:
            # self.dLaa = self.__dLaa(__speed, __time)
            # self.dLbb = self.__dLbb(__speed, __time)
            # self.dLcc = self.__dLcc(__speed, __time)
            # self.dLab = self.__dLab(__speed, __time)
            # self.dLbc = self.__dLbc(__speed, __time)
            # self.dLca = self.__dLca(__speed, __time)

            self.dLaa = self.__dLaa()
            self.dLbb = self.__dLbb()
            self.dLcc = self.__dLcc()
            self.dLab = self.__dLab()
            self.dLbc = self.__dLbc()
            self.dLca = self.__dLca()

            self.getState()
            (self.Ua_phase, self.Ub_phase, self.Uc_phase, self.Um) = self.Un(__time)

            self.Ia_phase = self.Ianr()
            self.Ib_phase = self.Ibnr()
            self.Ic_phase = self.Icnr()
            self.dIa_phase = self.dIan()
            self.dIb_phase = self.dIbn()
            self.dIc_phase = self.dIcn()

            self.Ia_phase0 = self.Ia_phase
            self.Ib_phase0 = self.Ib_phase
            self.Ic_phase0 = self.Ic_phase
            self.Laa0 = self.Laa
            self.Lbb0 = self.Lbb
            self.Lcc0 = self.Lcc
            self.Lab0 = self.Lab
            self.Lbc0 = self.Lbc
            self.Lca0 = self.Lca

            __innerTorque = self.__getInnerTorque(__speed, __time)
            __shaftTorque = self.__getShaftTorque(__speed, __innerTorque)
            __speed = abs(self.__getSpeed(__speed, loadTorque, __shaftTorque))
            i += 1

            N1 = int(len(time) / 8)
            N2 = len(time)
            speedAvg = avg(speed, limits=(N1, N2))
            if abs(100.0 * (__speedPrev - speedAvg) / speedAvg) < 0.001 and i > 2000:
                # print(i, abs(100.0 * (__speedPrev - speedAvg) / speedAvg))
                break
            else:
                __speedPrev = speedAvg

            phaseCurrentA.append(self.Ia_phase)
            phaseCurrentB.append(self.Ib_phase)
            phaseCurrentC.append(self.Ic_phase)
            sourceCurrent.append(self.Is())
            angleElectric.append(self.__getElectricalAngle(__speed, __time))
            angleMechanic.append(self.__getMechanicalAngle(__speed, __time))
            innerTorque.append(__innerTorque)
            shaftTorque.append(__shaftTorque)
            speed.append(__speed)
            time.append(__time)

            # test1.append(__speed)
            # test2.append(self.Ia_phase)
            # test3.append(self.Lcc)
            #
            # # test1.append(self.Ea)
            # # test2.append(self.Eb)
            # # test3.append(self.Ec)
            #
            # test4.append(self.Ea * 15)
            # test5.append(self.Eb * 15)
            # test6.append(self.Ec * 15)

            # __time += self.timeStep

            n += 1

        # plt.plot(time, phaseCurrentA, '-b')
        # plt.plot(time, phaseCurrentB, '-y')
        # plt.plot(time, phaseCurrentC, '-k')
        # plt.plot(time, sourceCurrent, '--b')
        # plt.plot(time, speed, '--b')
        #
        # plt.show()

        return self.__getOutput(electronic, time, speed, sourceCurrent,  phaseCurrentA, phaseCurrentB, phaseCurrentC, innerTorque, shaftTorque, angleElectric, angleMechanic)

    cdef solveSpeed(self, double loadSpeed, int numberOfPeriods, int totalTimeSteps):

        simTime = self.__getSimulationTime(loadSpeed, numberOfPeriods)
        self.timeStep = simTime / totalTimeSteps
        time, speed, angleElectric, angleMechanic = [], [], [], []
        phaseCurrentA, phaseCurrentB, phaseCurrentC, innerTorque, shaftTorque, sourceCurrent = [], [], [], [], [], []
        electronicLosses, FETA, FETB, FETC, CONTA, CONTB, CONTC, FETAS, FETBS, FETCS = [], [], [], [], [], [], [], [], [], []
        PSource, PIND, PRPP = [], [], []
        cdef int n = 0
        cdef double __time = 0
        cdef double __position = 0
        cdef __innerTorque = 0

        cdef int Nskip = 10  # No need to reaf emf so fine! Only derivatives!
        for __time in np.linspace(0, self.__getSimulationTime(loadSpeed, numberOfPeriods), totalTimeSteps):

            __position += RAD2DEG * 2 * self.pp * math.pi * loadSpeed / 60 * self.timeStep
            self.zeta = __position % 360

            if n % Nskip == 0:
                self.Ea = self.__Ea(loadSpeed, __position)
                self.Eb = self.__Eb(loadSpeed, __position)
                self.Ec = self.__Ec(loadSpeed, __position)

            self.Laa = self.__Laa(loadSpeed, __time)
            self.Lbb = self.__Lbb(loadSpeed, __time)
            self.Lcc = self.__Lcc(loadSpeed, __time)
            self.Lab = self.__Lab(loadSpeed, __time)
            self.Lbc = self.__Lbc(loadSpeed, __time)
            self.Lca = self.__Lca(loadSpeed, __time)

            # if n % Nskip == 0:
            # self.dLaa = self.__dLaa(loadSpeed, __time)
            # self.dLbb = self.__dLbb(loadSpeed, __time)
            # self.dLcc = self.__dLcc(loadSpeed, __time)
            # self.dLab = self.__dLab(loadSpeed, __time)
            # self.dLbc = self.__dLbc(loadSpeed, __time)
            # self.dLca = self.__dLca(loadSpeed, __time)

            self.dLaa = self.__dLaa()
            self.dLbb = self.__dLbb()
            self.dLcc = self.__dLcc()
            self.dLab = self.__dLab()
            self.dLbc = self.__dLbc()
            self.dLca = self.__dLca()

            self.getState()
            (self.Ua_phase, self.Ub_phase, self.Uc_phase, self.Um) = self.Un(__time)

            self.Ia_phase = self.Ianr()
            self.Ib_phase = self.Ibnr()
            self.Ic_phase = self.Icnr()
            self.dIa_phase = self.dIan()
            self.dIb_phase = self.dIbn()
            self.dIc_phase = self.dIcn()

            self.Ia_phase0 = self.Ia_phase
            self.Ib_phase0 = self.Ib_phase
            self.Ic_phase0 = self.Ic_phase
            self.Laa0 = self.Laa
            self.Lbb0 = self.Lbb
            self.Lcc0 = self.Lcc
            self.Lab0 = self.Lab
            self.Lbc0 = self.Lbc
            self.Lca0 = self.Lca

            __innerTorque = self.__getInnerTorque(loadSpeed, __time)
            phaseCurrentA.append(self.Ia_phase)
            phaseCurrentB.append(self.Ib_phase)
            phaseCurrentC.append(self.Ic_phase)
            sourceCurrent.append(self.Is())

            angleElectric.append(self.__getElectricalAngle(loadSpeed, __time))
            angleMechanic.append(self.__getMechanicalAngle(loadSpeed, __time))
            innerTorque.append(__innerTorque)
            shaftTorque.append(self.__getShaftTorque(loadSpeed, __innerTorque))
            speed.append(loadSpeed)
            time.append(__time)

            n += 1

        # plt.plot(time, shaftTorque, '-r')
        # plt.plot(time, phaseCurrentB, '-g')
        # plt.plot(time, phaseCurrentC, '-b')
        # plt.plot(time, sourceCurrent, '--r')
        N1 = int(len(time) / 2)
        N2 = len(time)

        Tshaft = avg(shaftTorque, limits=(N1, N2))
        Imax = maximum(phaseCurrentA, limits=(N1, N2))
        Iavg = avg_abs(phaseCurrentA, limits=(N1, N2))
        Irms = rms(phaseCurrentA, limits=(N1, N2))
        Iripple = Irms / 2
        Isource = avg(sourceCurrent, limits=(N1, N2))

        # plt.title("i=%s, speed=%s,Vdc=%s,Irms=%s,Is=%s" %(i, round(loadSpeed), self.Vdc, round(Irms*100)/100, round(Isource*100)/100))
        # plt.show()
        return (Isource, Imax, Iavg, Irms, Iripple, Tshaft)
        # return self.__getOutput(time, speed, sourceCurrent,  phaseCurrentA, phaseCurrentB, phaseCurrentC, innerTorque, shaftTorque, angleElectric, angleMechanic)

    cdef double L(self, double speed, double time, double initangle, double phaseadvance):
        cdef double w = self.pp * 2 * math.pi * speed / 60.0 * time
        cdef double delta = (initangle - phaseadvance) * DEG2RAD
        return self.Lg0 + self.Lg2 * math.cos(2 * w + delta)

    cdef double dL(self, double speed, double time, double initangle, double phaseadvance):
        cdef double w = self.pp * 2 * math.pi * speed / 60.0 * time
        cdef double delta = (initangle - phaseadvance) * DEG2RAD
        return -(2 * self.pp * 2 * math.pi * speed / 60.0) * self.Lg2 * math.sin(w + delta)

    cdef double M(self, double speed, double time, double initangle, double phaseadvance):
        cdef double w = self.pp * 2 * math.pi * speed / 60.0 * time
        cdef double delta = (initangle - phaseadvance) * DEG2RAD
        return -self.Lg0 / 2 + self.Lg2 * math.cos(2 * w + delta)

    cdef double dM(self, double speed, double time, double initangle, double phaseadvance):
        cdef double w = self.pp * 2 * math.pi * speed / 60.0 * time
        cdef double delta = (initangle - phaseadvance) * DEG2RAD
        return -(2 * self.pp * 2 * math.pi * speed / 60.0) * self.Lg2 * math.sin(w + delta)

    cdef double ke(self, double position, double initangle, double phaseadvance):
        # 0 - Real, 1 - Imaginary
        # a0 = 2.0 * self.cn_EMF[0][0]
        cdef double Ampl = 0
        cdef int ii = 1
        cdef double an, bn
        cdef double delta = (initangle - phaseadvance) * DEG2RAD
        position = position * DEG2RAD

        for ii in range(1, len(self.cn_EMF)):
            an = 2.0 * self.cn_EMF[ii]["real"]
            bn = -2.0 * self.cn_EMF[ii]["imag"]
            Ampl += an * math.cos(ii * position + ii * delta) + bn * math.sin(ii * position + ii * delta)

        return 30 * Ampl / (math.pi * self.refSpeed)

    cdef double __Ea(self, double speed, double position):
        return math.pi * speed / 30 * self.ke(position, 0, self.machine.controlcircuit.phaseAdvance)

    cdef double __Eb(self, double speed, double position):
        return math.pi * speed / 30 * self.ke(position, -120, self.machine.controlcircuit.phaseAdvance)

    cdef double __Ec(self, double speed, double position):
        return math.pi * speed / 30 * self.ke(position, -240, self.machine.controlcircuit.phaseAdvance)

    cdef double __Laa(self, double speed, double time):
        return self.L(speed, time, 0, self.machine.controlcircuit.phaseAdvance)

    cdef double __Lbb(self, double speed, double time):
        return self.L(speed, time, -240, self.machine.controlcircuit.phaseAdvance)

    cdef double __Lcc(self, double speed, double time):
        return self.L(speed, time, -120, self.machine.controlcircuit.phaseAdvance)

    cdef double __Lab(self, double speed, double time):
        return self.M(speed, time, -120, self.machine.controlcircuit.phaseAdvance)

    cdef double __Lbc(self, double speed, double time):
        return self.M(speed, time, -0, self.machine.controlcircuit.phaseAdvance)

    cdef double __Lca(self, double speed, double time):
        return self.M(speed, time, -240, self.machine.controlcircuit.phaseAdvance)

    # cdef double __dLaa(self, double speed, double time):
    #   return self.dL(speed, time, 0, self.machine.controlcircuit.phaseAdvance)
    #
    # cdef double __dLbb(self, double speed, double time):
    #   return self.dL(speed, time, -240, self.machine.controlcircuit.phaseAdvance)
    #
    # cdef double __dLcc(self, double speed, double time):
    #   return self.dL(speed, time, -240, self.machine.controlcircuit.phaseAdvance)

    # cdef double __dLab(self, double speed, double time):
    #   return self.dM(speed, time, -120, self.machine.controlcircuit.phaseAdvance)
    #
    # cdef double __dLbc(self, double speed, double time):
    #   return self.dM(speed, time, -0, self.machine.controlcircuit.phaseAdvance)
    #
    # cdef double __dLca(self, double speed, double time):
    #   return self.dM(speed, time, -240, self.machine.controlcircuit.phaseAdvance)

    cdef double __dLaa(self):
        return (self.Laa - self.Laa0) / self.timeStep

    cdef double __dLbb(self):
        return (self.Lbb - self.Lbb0) / self.timeStep

    cdef double __dLcc(self):
        return (self.Lcc - self.Lcc0) / self.timeStep

    cdef double __dLab(self):
        return (self.Lab - self.Lab0) / self.timeStep

    cdef double __dLbc(self):
        return (self.Lbc - self.Lbc0) / self.timeStep

    cdef double __dLca(self):
        return (self.Lca - self.Lca0) / self.timeStep

    cdef Un(self, time):
        # va, vb, vc, vm = None, None, None, None
        # region AB (Q1 = 1, Q5 = PWM
        cdef double va, vb, vc, vm
        if (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D6 == 1):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = self.Vdc
            vb = (1 - self.__PWM(time)) * self.Vdc
            vc = 0
            return (va, vb, vc, vm)

        elif (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D6 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb
                  - self.Ia_phase * (self.dLaa + self.dLab) - self.Ib_phase * (self.dLbb + self.dLab) - 0 * (self.dLca + self.dLbc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab) - self.dIb_phase * (self.Lbb + self.Lab) - 0 * (self.Lca + self.Lbc)
                  ) / 2.0
            va = self.Vdc
            vb = (1 - self.__PWM(time)) * self.Vdc
            vc = self.Ec + vm  # doubleing
            return (va, vb, vc, vm)

        elif (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D6 == -1):
            vm = (3 * self.Vdc - self.Ea - self.Eb - self.Ec) / 3.0
            va = self.Vdc
            vb = self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)
        # endregion
        # region AC (Q1 = 1, Q6 = PWM)
        elif (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D2 == 1):
            vm = ((3 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = self.Vdc
            vb = self.Vdc
            vc = (1 - self.__PWM(time)) * self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D2 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLca) - 0 * (self.dLab + self.dLbc) - self.Ic_phase * (self.dLca + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lca) - 0 * (self.Lab + self.Lbc) - self.dIc_phase * (self.Lcc + self.Lca)
                  ) / 2.0
            va = self.Vdc
            vb = self.Eb + vm  # doubleing because Ib = 0
            vc = (1 - self.__PWM(time)) * self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 1 and self.Q2 == 0 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D2 == -1):
            vm = (-self.Ea - self.Eb - self.Ec) / 3.0
            va = 0
            vb = 0
            vc = 0
            return (va, vb, vc, vm)

        # endregion
        # region BC (Q2 = 1, Q6 = PWM)
        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D4 == 1):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = 0
            vb = self.Vdc
            vc = (1 - self.__PWM(time)) * self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D4 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Eb - self.Ec
                  - 0 * (self.dLab + self.dLca) - self.Ib_phase * (self.dLbb + self.dLbc) - self.Ic_phase * (self.dLbc + self.dLcc)
                  - (self.dIa_phase - self.dIc_phase) * (self.Lbb + self.Lbc) - self.dIc_phase * (self.Lcc + self.Lbc)
                  ) / 2.0
            va = self.Ea + vm  # doubleing
            vb = self.Vdc
            vc = (1 - self.__PWM(time)) * self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == 0 and self.Q5 == 0 and self.Q6 == -1 and self.D4 == -1):
            vm = (3 * self.Vdc - self.Ea - self.Eb - self.Ec) / 3.0
            va = self.Vdc
            vb = self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)

        # endregion
        # region BA (Q2 = 1, Q4 = PWM)
        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D3 == 1):
            vm = ((3 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = (1 - self.__PWM(time)) * self.Vdc
            vb = self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D3 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb
                  - self.Ia_phase * (self.dLaa + self.dLab) - self.Ib_phase * (self.dLab + self.dLbb) - 0 * (self.dLca + self.dLbc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab) - self.dIb_phase * (self.Lbb + self.Lab)
                  ) / 2.0
            va = (1 - self.__PWM(time)) * self.Vdc
            vb = self.Vdc
            vc = self.Ec + vm  # doubleing
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 1 and self.Q3 == 0 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D3 == -1):
            vm = (-self.Ea - self.Eb - self.Ec) / 3.0
            va = 0
            vb = 0
            vc = 0
            return (va, vb, vc, vm)

        # endregion
        # region CA (Q3 = 1, Q4 = PWM)
        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D5 == 1):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = (1 - self.__PWM(time)) * self.Vdc
            vb = 0
            vc = self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D5 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Ec - self.Ea
                  - self.Ia_phase * (self.dLaa + self.dLca) - 0 * (self.dLab + self.dLbc) - self.Ic_phase * (self.dLca + self.dLcc)
                  - self.dIc_phase * (self.Lcc + self.Lca) - (-self.dIc_phase - self.dIb_phase) * (self.Laa + self.Lca)
                  ) / 2.0
            va = (1 - self.__PWM(time)) * self.Vdc
            vb = self.Eb + vm
            vc = self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == -1 and self.Q6 == 0 and self.Q5 == 0 and self.D5 == -1):
            vm = (3 * self.Vdc - self.Ea - self.Eb - self.Ec) / 3.0
            va = self.Vdc
            vb = self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)

        # endregion
        # region CB (Q3 = 1, Q5 = PWM)
        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D1 == 1):
            vm = ((3 - self.__PWM(time)) * self.Vdc - self.Ea - self.Eb - self.Ec
                  - self.Ia_phase * (self.dLaa + self.dLab + self.dLca) - self.Ib_phase * (self.dLab + self.dLbb + self.dLbc) - self.Ic_phase * (self.dLca + self.dLbc + self.dLcc)
                  - (-self.dIb_phase - self.dIc_phase) * (self.Laa + self.Lab + self.Lca) - self.dIb_phase * (self.Lab + self.Lbb + self.Lbc) - self.dIc_phase * (self.Lca + self.Lbc + self.Lcc)
                  ) / 3.0
            va = self.Vdc
            vb = (1 - self.__PWM(time)) * self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D1 == 0):
            vm = ((2 - self.__PWM(time)) * self.Vdc - self.Eb - self.Ec
                  - 0 * (self.dLab + self.dLca) - self.Ib_phase * (self.dLbb + self.dLbc) - self.Ic_phase * (self.dLbc + self.dLcc)
                  - (-self.dIa_phase - self.dIc_phase) * (self.Lbb + self.Lbc) - self.dIc_phase * (self.Lcc + self.Lbc)
                  ) / 2.0
            va = self.Ea + vm
            vb = (1 - self.__PWM(time)) * self.Vdc
            vc = self.Vdc
            return (va, vb, vc, vm)

        elif (self.Q1 == 0 and self.Q2 == 0 and self.Q3 == 1 and self.Q4 == 0 and self.Q5 == -1 and self.Q6 == 0 and self.D1 == -1):
            vm = (-self.Ea - self.Eb - self.Ec) / 3.0
            va = 0
            vb = 0
            vc = 0
            return (va, vb, vc, vm)
        # endregion
        else:
            print("oops. state not found")
            return (None, None, None, None)

    cdef getState(self):
        #  When PWM value is -1!
        if self.zeta >= 30 and self.zeta < 90:
            self.Q1 = 1
            self.Q2 = 0
            self.Q3 = 0
            self.Q4 = 0
            self.Q5 = -1
            self.Q6 = 0
            self.D6 = 1  # Q3 off
            self.Ia_phase_off = False
            if self.Ic_phase <= 0:
                self.D6 = 0
                self.Ic_phase_off = True

        elif self.zeta >= 90 and self.zeta < 150:
            self.Q1 = 1
            self.Q2 = 0
            self.Q3 = 0
            self.Q4 = 0
            self.Q5 = 0
            self.Q6 = -1
            self.D2 = 1  # Q5 off
            self.Ic_phase_off = False
            if self.Ib_phase >= 0:
                self.D2 = 0
                self.Ib_phase_off = True

        elif self.zeta >= 150 and self.zeta < 210:
            self.Q1 = 0
            self.Q2 = 1
            self.Q3 = 0
            self.Q4 = 0
            self.Q5 = 0
            self.Q6 = -1
            self.D4 = 1  # Q1 off
            self.Ib_phase_off = False
            if self.Ia_phase <= 0:
                self.D4 = 0
                self.Ia_phase_off = True

        elif self.zeta >= 210 and self.zeta < 270:
            self.Q1 = 0
            self.Q2 = 1
            self.Q3 = 0
            self.Q4 = -1
            self.Q5 = 0
            self.Q6 = 0
            self.D3 = 1
            self.Ia_phase_off = False
            if self.Ic_phase >= 0:
                self.D3 = 0
                self.Ic_phase_off = True

        elif self.zeta >= 270 and self.zeta < 330:
            self.Q1 = 0
            self.Q2 = 0
            self.Q3 = 1
            self.Q4 = -1
            self.Q5 = 0
            self.Q6 = 0
            self.D5 = 1  # Q2 off
            self.Ic_phase_off = False
            if self.Ib_phase <= 0:
                self.D5 = 0
                self.Ib_phase_off = True

        elif (self.zeta >= 330 and self.zeta < 360):
            self.Q1 = 0
            self.Q2 = 0
            self.Q3 = 1
            self.Q4 = 0
            self.Q5 = -1
            self.Q6 = 0
            self.D1 = 1
            self.Ib_phase_off = False
            if (self.Ia_phase >= 0):
                self.D1 = 0
                self.Ia_phase_off = True

        elif (self.zeta >= 0 and self.zeta < 30):
            self.Q1 = 0
            self.Q2 = 0
            self.Q3 = 1
            self.Q4 = 0
            self.Q5 = -1
            self.Q6 = 0
            self.D1 = 1
            self.Ib_phase_off = False
            if (self.Ia_phase >= 0):
                self.D1 = 0
                self.Ia_phase_off = True

        else:
            print("hey")
            self.Q1 = -1
            self.Q2 = -1
            self.Q3 = -1
            self.Q4 = -1
            self.Q5 = -1
            self.Q6 = -1

    cdef double Ianr(self):
        if (self.Ia_phase_off):
            return 0
        else:
            return self.Ia_phase + (self.timeStep / self.Laa) * (self.Ua_phase - self.Ea - self.Um - self.R * self.Ia_phase - self.Ia_phase * self.dLaa - self.Ib_phase * self.dLab - self.Ic_phase * self.dLca - self.Lab * self.dIb_phase - self.Lca * self.dIc_phase)

    cdef double Ibnr(self):
        if (self.Ib_phase_off):
            return 0
        else:
            return self.Ib_phase + (self.timeStep / self.Lbb) * (self.Ub_phase - self.Eb - self.Um - self.R * self.Ib_phase - self.Ia_phase * self.dLab - self.Ib_phase * self.dLbb - self.Ic_phase * self.dLbc - self.Lab * self.dIa_phase - self.Lbc * self.dIc_phase)

    cdef double Icnr(self):
        if (self.Ic_phase_off):
            return 0
        else:
            return self.Ic_phase + (self.timeStep / self.Lcc) * (self.Uc_phase - self.Ec - self.Um - self.R * self.Ic_phase - self.Ia_phase * self.dLca - self.Ib_phase * self.dLbc - self.Ic_phase * self.dLcc - self.Lca * self.dIa_phase - self.Lbc * self.dIb_phase)

    cdef double dIan(self):
        if (self.Ia_phase_off):
            return 0
        else:
            return (self.Ia_phase - self.Ia_phase0) / self.timeStep

    cdef double dIbn(self):
        if (self.Ib_phase_off):
            return 0
        else:
            return (self.Ib_phase - self.Ib_phase0) / self.timeStep

    cdef double dIcn(self):
        if (self.Ic_phase_off):
            return 0
        else:
            return (self.Ic_phase - self.Ic_phase0) / self.timeStep

    cdef double Is(self):
        #  When PWM value is -1!
        if (self.zeta >= 30 and self.zeta < 90):
            return self.Ia_phase
        elif (self.zeta >= 90 and self.zeta < 150):
            return -self.Ic_phase
        elif (self.zeta >= 150 and self.zeta < 210):
            return self.Ib_phase
        elif (self.zeta >= 210 and self.zeta < 270):
            return -self.Ia_phase
        elif (self.zeta >= 270 and self.zeta < 330):
            return self.Ic_phase
        elif (self.zeta >= 330 and self.zeta < 360):
            return -self.Ib_phase
        elif (self.zeta >= 0 and self.zeta < 30):
            return self.Ic_phase
        else:
            return 0

    cdef double frictionLosses(self, speed):
        return self.frictionTorque * 2 * math.pi * speed / 60.0

    cdef double dampingLosses(self, speed):
        return self.damping * (2.0 * math.pi * speed / 60.0) ** 2

    cdef double conductionLosses(self, Irms):
        return 3 * self.nameplate['Resistance (Ohm)'] * Irms ** 2.0

    cdef double conductionCableTransistorLosses(self, Irms):
        return 3 * self.R * Irms ** 2.0

    cdef double coreLosses(self, speed):
        volumeStator = self.machine.stator.area * self.machine.stator.stacklength
        volumeRotor = self.machine.rotor.area * self.machine.rotor.stacklength
        Bm = (self.nameplate["Btooth (T)"] + self.nameplate["Byoke (T)"]) / 2.0
        Ps = self.machine.stator.material.getSteinmetzLosses(volume=volumeStator, Bm=Bm, frequency=self.pp * speed / 60.0)
        Pr = self.machine.rotor.material.getSteinmetzLosses(volume=volumeRotor, Bm=Bm, frequency=self.pp * speed / 60.0)
        return Ps # + Pr

    cdef double __getSpeed(self, speed, loadTorque, shaftTorque):
        omega = ((shaftTorque - loadTorque) * self.timeStep) / self.momentOfInertia + 2.0 * math.pi * speed / 60.0
        return omega / 2.0 / math.pi * 60

    cdef double __getShaftTorque(self, speed, innerTorque):
        """Calculates shaft torque of the machine (Nm). The electronic losses have to be included here."""
        if speed > 0:
            return innerTorque - (self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed)) / (2.0 * math.pi * speed / 60.0)
        else:
            return innerTorque - self.frictionTorque

    cdef double __getInnerTorqueFromShaftTorque(self, speed, shaftTorque):
        """Calculates inner torque of the machine (Nm)."""
        if (speed > 0):
            return shaftTorque + (self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed)) / (2.0 * math.pi * speed / 60.0)
        else:
            return shaftTorque + self.frictionTorque

    cdef double __getFakeMotorLosses(self, speed, Irms):
        return self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed) + self.conductionCableTransistorLosses(Irms)

    cdef double __getRealMotorLosses(self, speed, Irms):
        # Set real phase resistance
        return self.frictionLosses(speed) + self.dampingLosses(speed) + self.coreLosses(speed) + self.conductionLosses(Irms)

    cdef double __getElectricalAngle(self, speed, time):
        return self.pp * 2 * math.pi * speed / 60.0 * time * RAD2DEG

    cdef double __getMechanicalAngle(self, speed, time):
        return 2 * math.pi * speed / 60.0 * time * RAD2DEG

    cdef double __getInnerTorque(self, speed, time):
        omega_mech = 2.0 * math.pi * speed / 60.0
        if self.useReluctance:
            if speed == 0:
                return 0
            else:
                return ((self.Ea * self.Ia_phase + self.Eb * self.Ib_phase + self.Ec * self.Ic_phase) / omega_mech +
                        0.5 * ((math.pow(self.Ia_phase, 2) * self.dLaa +
                                math.pow(self.Ib_phase, 2) * self.dLbb +
                                math.pow(self.Ic_phase, 2) * self.dLcc) +
                               self.Ia_phase * self.Ib_phase * self.dLab +
                               self.Ib_phase * self.Ic_phase * self.dLbc +
                               self.Ic_phase * self.Ia_phase * self.dLca) / omega_mech / self.pp * 2)
        else:
            if speed == 0:
                return 0
            else:
                return (self.Ea * self.Ia_phase + self.Eb * self.Ib_phase + self.Ec * self.Ic_phase) / omega_mech

    cdef double __PWM(self, time):
        # Get the decimal rest of the time to pwmPeriod ratio in %. This is than compared to Duty Cycle.
        PWMTimePeriod = 1.0 / self.machine.controlcircuit.pwmFrequency
        Rest = (time / PWMTimePeriod - math.floor(time / PWMTimePeriod)) * 100.0

        if (Rest <= self.machine.controlcircuit.dutyCycle):
            return 1
        else:
            return 0

    cdef double __getSimulationTime(self, speed, numberOfPeriods):
        return numberOfPeriods * 60 / speed / self.pp
