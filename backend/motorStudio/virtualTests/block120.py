import os
from motorStudio.enums import *
from fractions import gcd
from utils import exportSolutionCSV


class block120(object):
    """Calculates the natural performance curve of the motor controlled by the so-called 120deg block-commutation (also known as the 6-step control)."""

    def __init__(self, machine=None, speeds=[1000], temperatures=[25], numberofPeriods=1, numberofTimeSteps=120):
        self.machine = machine
        self.speed = 1000
        self.numberofPeriods = numberofPeriods
        self.numberofTimeSteps = numberofTimeSteps
        self.speeds = speeds
        self.temperatures = temperatures
        self.currentspeed = self.speeds[0]
        self.caption = "Performance Virtual Test (120 Degrees Six-Step Block Commutation)"
        self.description = ""

        if self.machine != None:
            self.__poleNumber = self.machine["design"]["Rotor"]["Pole Number"]
            self.__initialPosition = self.machine["design"]["Initial Position (deg)"]
            self.__frictionTorque = self.machine["design"][
                "Mechanics"]["Friction Torque (Nm)"]
            self.__phaseNumber = self.machine["design"]["Winding"]["Phase Number"]
            self.__phaseLetters = self.machine["design"]["Winding"]["Phase Letters"]
            self.__phaseResistance = self.machine["design"][
                "Winding"]["Phase Resistance (Ohm)"]
            self.__phaseConnection = self.machine["design"]["Winding"]["Phase Connection"]["Used"]["name"]

    def run(self, oDesktop=None, materials=None, definitions=None, createNewMaterials=True):
        oProject = oDesktop.GetActiveProject()
        oDesign = oProject.GetActiveDesign()

        for temperature in self.temperatures:
            if createNewMaterials:
                materials.createAll(oProject, temperature)
                materials.assignAll(oProject, temperature)

                for speed in self.speeds:
                    self.speed = speed
                    definitions.applyAll(oProject)

                    oDesktop.AddMessage("", "", 1, "Running block120 test...")

                    oDesign.AnalyzeAll()

                    path = oProject.GetPath() + "/Results/block120/" + str(temperature) + \
                        "C" + "/" + str(speed) + "rpm"
                    if not os.path.exists(path):
                        os.makedirs(path)

                    exportSolutionCSV(
                        oDesign,
                        oDesktop,
                        self.getOutputVariableDefinitions(
                            partNames=definitions.geometries.partNames),
                        self.simulationTime(),
                        self.timeStep(),
                        path
                    )

                    oDesktop.AddMessage(
                        "", "", 1, "Finished! Please check the \"%s\" directory in the current project folder. " % (path))
                    oDesign.DeleteFullVariation("All", False)

                    # When finished delete all reports
                    oModule = oDesign.GetModule("ReportSetup")
                    oModule.DeleteAllReports()

                    oProject.Save()
                    oDesktop.AddMessage(
                        "", "", 1, "Project saved. This increases the speed of the calculations.")

    def simulationTime(self):
        return round(60.0 / self.speed * self.numberofPeriods / self.__poleNumber * 2, 8)

    def timeStep(self):
        return round(60.0 / self.speed * self.numberofPeriods / self.__poleNumber * 2 / self.numberofTimeSteps, 8)

    def getOutputVariableDefinitions(self, partNames={}):
        """ Defines the ouput variables in form of tuple of dictionaries: ({'name':'variableName', 'equation':'variableEquation', 'type':'variableType'}). """

        if self.__initialPosition >= 0:
            initialPosition = "-" + str(self.__initialPosition)
        else:
            initialPosition = "+" + str(abs(self.__initialPosition))

        outputVariables = [
            {'name': 'Shaft_Torque', 'unit': 'NewtonMeter', 'equation': 'Moving1.Torque',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Friction_Torque', 'unit': 'NewtonMeter', 'equation': "%s*1NewtonMeter" % (
                self.__frictionTorque), 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Friction_Losses', 'unit': 'W', 'equation': "(2*pi*Moving1.Speed/60rpm)*%s" % (
                self.__frictionTorque), 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Simulation_Time', 'unit': 's', 'equation': 'Time',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Position', 'unit': 'deg',
                'equation': '(2*pi*Moving1.Speed/60rpm)*time * 180/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Speed', 'unit': 'rpm', 'equation': 'Moving1.Speed/1rpm',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Tooth_Flux_Density', 'unit': 'tesla',
                'equation': 'Btooth', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Yoke_Flux_Density', 'unit': 'tesla', 'equation': 'Byoke',
                'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Eddy_Current_Losses_Housing', 'unit': 'W',
                'equation': 'PeddyHousing', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Eddy_Current_Losses_Separationcan', 'unit': 'W',
                'equation': 'PeddySeparationcan', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Eddy_Current_Losses_Magnet', 'unit': 'W',
                'equation': 'PeddyMagnet', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Shaft_Power', 'unit': 'W',
                'equation': '(2*pi*Moving1.Speed/60rpm)*Moving1.Torque', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Source_Current', 'unit': 'A',
                'equation': 'BranchCurrent(VIs)', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Core_Losses', "unit": "W", 'equation': "CoreLoss",
                'type': 'Transient', 'integration factor': 0.5}
        ]

        equation = "EddyCurrentLoss(%s)+ExcessLoss(%s)+HysteresisLoss(%s)" % (
            partNames["Stator"], partNames["Stator"], partNames["Stator"])
        # # equation += "+EddyCurrentLoss(__stator)+ExcessLoss(__stator)+HysteresisLoss(__stator)"
        outputVariables.append({'name': 'Core_Losses_Stator', "unit": "W",
                               'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        equation = "EddyCurrentLoss(%s)+ExcessLoss(%s)+HysteresisLoss(%s)" % (
            partNames["Rotor"], partNames["Rotor"], partNames["Rotor"])
        # # equation += "+EddyCurrentLoss(__rotor)+ExcessLoss(__rotor)+HysteresisLoss(__rotor)"
        outputVariables.append({'name': 'Core_Losses_Rotor', "unit": "W",
                               'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        for i in range(self.__phaseNumber):
            for j in range(self.__phaseNumber):
                name = "L_%s%s" % (
                    self.__phaseLetters[i], self.__phaseLetters[j])
                equation = "L(%s,%s)" % (
                    self.__phaseLetters[i], self.__phaseLetters[j])
                outputVariables.append(
                    {'name': name, 'unit': 'H', 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        for i in range(self.__phaseNumber):
            name = 'Induced_Voltage_%s' % (self.__phaseLetters[i])
            equation = 'InducedVoltage(%s)' % (self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "V", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        for i in range(self.__phaseNumber):
            name = 'Flux_Linkage_%s' % (self.__phaseLetters[i])
            equation = 'FluxLinkage(%s)' % (self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "Wb", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        if (self.__phaseNumber == 3):
            name = 'Ld'
            angle = "(Moving1.Position/1deg %s)*%s*pi/180" % (initialPosition,
                                                              float(self.__poleNumber) / 2.0)
            L11 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[0], angle, self.__phaseLetters[1], self.__phaseLetters[0], angle, self.__phaseLetters[2], self.__phaseLetters[0])
            L12 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[1], angle, self.__phaseLetters[1], self.__phaseLetters[1], angle, self.__phaseLetters[2], self.__phaseLetters[1])
            L13 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[2], angle, self.__phaseLetters[1], self.__phaseLetters[2], angle, self.__phaseLetters[2], self.__phaseLetters[2])
            equation = '2/3 * (cos(%s) * %s + cos(%s-2*pi/3) * %s + cos(%s+2*pi/3) * %s)'\
                % (angle, L11, angle, L12, angle, L13)
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        if (self.__phaseNumber == 3):
            name = 'Lq'
            angle = "(Moving1.Position/1deg %s)*%s*pi/180" % (initialPosition,
                                                              float(self.__poleNumber) / 2.0)
            L11 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[0], angle, self.__phaseLetters[1], self.__phaseLetters[0], angle, self.__phaseLetters[2], self.__phaseLetters[0])
            L12 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[1], angle, self.__phaseLetters[1], self.__phaseLetters[1], angle, self.__phaseLetters[2], self.__phaseLetters[1])
            L13 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))'\
                % (angle, self.__phaseLetters[0], self.__phaseLetters[2], angle, self.__phaseLetters[1], self.__phaseLetters[2], angle, self.__phaseLetters[2], self.__phaseLetters[2])
            equation = '2/3 * (sin(%s) * %s + sin(%s-2*pi/3) * %s + sin(%s+2*pi/3) * %s)'\
                % (angle, L11, angle, L12, angle, L13)
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        for i in range(self.__phaseNumber):
            name = 'Phase_Current_%s' % (self.__phaseLetters[i])
            equation = 'Current(%s)' % (self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "A", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        name = 'Copper_Losses'
        equation = ''
        for i in range(self.__phaseNumber):
            equation += '+%s*Current(%s)*Current(%s)' % (self.__phaseResistance,
                                                         self.__phaseLetters[i], self.__phaseLetters[i])
        outputVariables.append({'name': name, "unit": "W", 'equation': equation,
                               'type': 'Transient', 'integration factor': 0.5})

        for i in range(self.__phaseNumber):
            name = 'Phase_Voltage_%s' % (self.__phaseLetters[i])
            equation = '%s*Current(%s)+InducedVoltage(%s)' % (
                self.__phaseResistance, self.__phaseLetters[i], self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "V", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        if self.__phaseConnection == "delta":
            for i in range(self.__phaseNumber):
                name = 'Line_Current_%s' % (self.__phaseLetters[i])
                equation = 'Current(%s)-Current(%s)' % (
                    self.__phaseLetters[i], self.__phaseLetters[(i + 1) % self.__phaseNumber])
                outputVariables.append(
                    {'name': name, "unit": "A", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

            for i in range(self.__phaseNumber):
                name = 'Line_Voltage_%s%s' % (
                    self.__phaseLetters[i], self.__phaseLetters[(i + 1) % self.__phaseNumber])
                equation = '%s*Current(%s)+InducedVoltage(%s)' % (self.__phaseResistance,
                                                                  self.__phaseLetters[i].strip(), self.__phaseLetters[i].strip())
                outputVariables.append(
                    {'name': name, "unit": "V", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        else:
            for i in range(self.__phaseNumber):
                name = 'Line_Current_%s' % (self.__phaseLetters[i])
                equation = 'Current(%s)' % (self.__phaseLetters[i])
                outputVariables.append(
                    {'name': name, "unit": "A", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

            for i in range(self.__phaseNumber):
                name = 'Line_Voltage_%s%s' % (
                    self.__phaseLetters[i], self.__phaseLetters[(i + 1) % self.__phaseNumber])
                equation = '%s * Current(%s)+InducedVoltage(%s)-%s*Current(%s)-InducedVoltage(%s)' % (self.__phaseResistance, self.__phaseLetters[i], self.__phaseLetters[i],
                                                                                                      self.__phaseResistance, self.__phaseLetters[(
                                                                                                          i + 1) % self.__phaseNumber],
                                                                                                      self.__phaseLetters[(i + 1) % self.__phaseNumber])
                outputVariables.append(
                    {'name': name, "unit": "V", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        return outputVariables
