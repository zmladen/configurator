import os
from motorStudio.enums import *
from fractions import gcd
from utils import exportSolutionCSV


class noload(object):
    """Calculates the no-Load parameters, i.e. the induced voltage and the inductance matrix of of the machine."""

    def __init__(self, machine=None, speeds=[1000], temperatures=[25], numberofPeriods=1, numberofTimeSteps=120):
        self.machine = machine
        self.speed = 1000
        self.numberofPeriods = numberofPeriods
        self.numberofTimeSteps = numberofTimeSteps
        self.speeds = speeds
        self.temperatures = temperatures
        self.caption = "No-Load Virtual Test"
        self.description = ""

        if self.machine != None:
            self.__poleNumber = self.machine["design"]["Rotor"]["Pole Number"]
            self.__initialPosition = self.machine["design"]["Initial Position (deg)"]
            self.__phaseNumber = self.machine["design"]["Winding"]["Phase Number"]
            self.__phaseLetters = self.machine["design"]["Winding"]["Phase Letters"]

    def run(self, oDesktop=None, materials=None, definitions=None, createNewMaterials=True):
        oProject = oDesktop.GetActiveProject()
        oDesign = oProject.GetActiveDesign()

        for temperature in self.temperatures:
            if createNewMaterials:
                materials.createAll(oProject, temperature)
                materials.assignAll(oProject, temperature)

                for speed in self.speeds:
                    self.speed = speed
                    definitions.geometries.setBandSegments(
                        oProject=oProject, numberOfSegments=self.numberofTimeSteps)
                    definitions.applyAll(oProject)

                    oDesktop.AddMessage("", "", 0, "Running no-load test...")

                    oDesign.AnalyzeAll()

                    oDesktop.ClearMessages(oDesktop.GetActiveProject(
                    ).GetName(), oProject.GetActiveDesign().GetName(), 1)

                    path = oProject.GetPath() + "/Results/noload/" + str(temperature) + \
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
                        "", "", 0, "Finished! Please check the \"%s\" directory in the current project folder. " % (path))
                    oDesign.DeleteFullVariation("All", False)

                    # When finished delete all reports
                    oModule = oDesign.GetModule("ReportSetup")
                    oModule.DeleteAllReports()

                    oProject.Save()
                    oDesktop.AddMessage(
                        "", "", 0, "Project saved. This increases the speed of the calculations.")

    def simulationTime(self):
        return round(60.0 / self.speed * self.numberofPeriods / self.__poleNumber * 2, 8)

    def timeStep(self):
        return round(60.0 / self.speed * self.numberofPeriods / self.__poleNumber * 2 / self.numberofTimeSteps, 8)

    def getOutputVariableDefinitions(self, partNames):
        """ Defines the ouput variables in form of tuple of dictionaries: ({'name':'variableName', 'equation':'variableEquation', 'type':'variableType'}). """

        if self.__initialPosition >= 0:
            initialPosition = "-" + str(self.__initialPosition)
        else:
            initialPosition = "+" + str(abs(self.__initialPosition))

        outputVariables = [
            {'name': 'Simulation_Time', 'unit': 's', 'equation': 'Time',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Position', 'unit': 'deg',
                'equation': '(2*pi*Moving1.Speed/60rpm)*time * 180/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Speed', 'unit': 'rpm',
                'equation': 'deriv(Moving1.Position*1rad)*60/2/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Tooth_Flux_Density', 'unit': 'tesla',
                'equation': 'Btooth', 'type': 'Fields', 'integration factor': 1},
            {'name': 'Yoke_Flux_Density', 'unit': 'tesla',
                'equation': 'Byoke', 'type': 'Fields', 'integration factor': 1},
            {'name': 'Eddy_Current_Losses_Housing', 'unit': 'W',
                'equation': 'PeddyHousing', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Eddy_Current_Losses_Separationcan', 'unit': 'W',
                'equation': 'PeddySeparationcan', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Eddy_Current_Losses_Magnet', 'unit': 'W',
                'equation': 'PeddyMagnet', 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'Core_Losses', "unit": "W", 'equation': "CoreLoss",
             'type': 'Transient', 'integration factor': 0.5},
            {'name': "B_Mag_AVG", 'unit': 'T',
                'equation': "B_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
            {'name': "H_Mag_AVG", 'unit': 'Ampere_per_meter',
                'equation': "H_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'J_MAG_AVG', 'unit': 'T',
                'equation': "J_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
        ]

        # for i in range(1,  self.__poleNumber // self.machine["design"]["Symmetry Number"]):
        for i in range(1, 2):
            # Show the operating point only of 1st magnet. Reduces the simulation time.
            outputVariables.append({'name': "B_Mag_AVG_%d" % (i), 'unit': 'T',
                                    'equation': "B_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})
            outputVariables.append({'name': "H_Mag_AVG_%d" % (i), 'unit': 'Ampere_per_meter',
                                    'equation': "H_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})
            outputVariables.append({'name': "J_Mag_AVG_%d" % (i), 'unit': 'T',
                                    'equation': "J_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})

        # equation = "EddyCurrentLoss(%s)+ExcessLoss(%s)+HysteresisLoss(%s)" %(partNames["Stator"], partNames["Stator"], partNames["Stator"])
        # outputVariables.append({'name': 'Core_Losses_Stator', "unit": "W", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        # equation = "EddyCurrentLoss(%s)+ExcessLoss(%s)+HysteresisLoss(%s)" %(partNames["Rotor"], partNames["Rotor"], partNames["Rotor"])
        # outputVariables.append({'name': 'Core_Losses_Rotor', "unit": "W", 'equation': equation, 'type': 'Transient', 'integration factor': 0.5})

        name = "angl_dq"
        # Rotate for 180deg because the BEMF is reverced in 1D simulations...
        equation = "(Moving1.Position %sdeg)*%s+180deg" % (initialPosition,
                                                           float(self.__poleNumber) / 2.0)
        outputVariables.append(
            {'name': name, "unit": "deg", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        for i in range(self.__phaseNumber):
            for j in range(self.__phaseNumber):
                name = "L_%s%s" % (
                    self.__phaseLetters[i], self.__phaseLetters[j])
                equation = "L(%s,%s)" % (
                    self.__phaseLetters[i], self.__phaseLetters[j])
                outputVariables.append(
                    {'name': name, 'unit': 'H', 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        for i in range(self.__phaseNumber):
            name = 'Induced_Voltage_%s' % (self.__phaseLetters[i])
            equation = 'InducedVoltage(%s)' % (self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "V", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        for i in range(self.__phaseNumber):
            name = 'Flux_Linkage_%s' % (self.__phaseLetters[i])
            equation = 'FluxLinkage(%s)' % (self.__phaseLetters[i])
            outputVariables.append(
                {'name': name, "unit": "Wb", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        if (self.__phaseNumber == 3):
            name = 'Psi_d'
            equation = '2/3 * (cos(angl_dq) * %s + cos(angl_dq-2*pi/3) * %s + cos(angl_dq+2*pi/3) * %s)' % ('FluxLinkage(%s)' % (
                self.__phaseLetters[0]), 'FluxLinkage(%s)' % (self.__phaseLetters[1]), 'FluxLinkage(%s)' % (self.__phaseLetters[2]))
            outputVariables.append(
                {'name': name, "unit": "Wb", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

            name = 'Psi_q'
            equation = '2/3 * (-sin(angl_dq) * %s - sin(angl_dq-2*pi/3) * %s - sin(angl_dq+2*pi/3) * %s)' % ('FluxLinkage(%s)' % (
                self.__phaseLetters[0]), 'FluxLinkage(%s)' % (self.__phaseLetters[1]), 'FluxLinkage(%s)' % (self.__phaseLetters[2]))
            outputVariables.append(
                {'name': name, "unit": "Wb", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

            name = 'Psi_0'
            equation = '1/3 * (%s + %s + %s)' % ('FluxLinkage(%s)' % (self.__phaseLetters[0]), 'FluxLinkage(%s)' % (
                self.__phaseLetters[1]), 'FluxLinkage(%s)' % (self.__phaseLetters[2]))
            outputVariables.append(
                {'name': name, "unit": "Wb", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        if (self.__phaseNumber == 3):

            w1 = self.__phaseLetters[0]
            w2 = self.__phaseLetters[1]
            w3 = self.__phaseLetters[2]
            angle = "(Moving1.Position/1deg %s)*%s*pi/180" % (initialPosition,
                                                              float(self.__poleNumber) / 2.0)

            name = "Ldd"
            equation = "2/3*((L("+w1+","+w1+")*cos(angl_dq)+L("+w1+","+w2+")*cos(angl_dq-120deg)+L("+w1+","+w3+")*cos(angl_dq-240deg))*cos(angl_dq)+(L("+w2+","+w1+")*cos(angl_dq)+L("+w2+","+w2+")*cos(angl_dq-120deg)+L(" + \
                w2+","+w3+")*cos(angl_dq-240deg))*cos(angl_dq-120deg)+(L("+w3+","+w1+")*cos(angl_dq)+L(" + \
                w3+","+w2+")*cos(angl_dq-120deg)+L("+w3+","+w3 + \
                ")*cos(angl_dq-240deg))*cos(angl_dq-240deg))"
            # equation = "2/3*((L("+w1+","+w1+")*cos("+angle+")+L("+w1+","+w2+")*cos("+angle+"-2*pi/3)+L("+w1+","+w3+")*cos("+angle+"-4*pi/3))*cos("+angle+")+(L("+w2+","+w1+")*cos("+angle+")+L("+w2+","+w2+")*cos("+angle + \
            #     "-2*pi/3)+L("+w2+","+w3+")*cos("+angle+"-4*pi/3))*cos("+angle+"-2*pi/3)+(L("+w3+","+w1+")*cos("+angle + \
            #     ")+L("+w3+","+w2+")*cos("+angle+"-2*pi/3)+L("+w3+"," + \
            #     w3+")*cos("+angle+"-4*pi/3))*cos("+angle+"-4*pi/3))"
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

            name = "Ldq"
            # equation = "2/3*((L("+w1+","+w1+")*cos("+angle+")+L("+w1+","+w2+")*cos("+angle+"-2*pi/3)+L("+w1+","+w3+")*cos("+angle+"-4*pi/3))*sin("+angle+")+(L("+w2+","+w1+")*cos("+angle+")+L("+w2+","+w2+")*cos("+angle+"-2*pi/3)+L(" + \
            #     w2+","+w3+")*cos("+angle+"-4*pi/3))*sin("+angle+"-2*pi/3)+(L("+w3+","+w1+")*cos("+angle+")+L(" + \
            #     w3+","+w2+")*cos("+angle+"-2*pi/3)+L("+w3+","+w3 + \
            #     ")*cos("+angle+"-4*pi/3))*sin("+angle+"-4*pi/3))"
            equation = "2/3*((L("+w1+","+w1+")*cos(angl_dq)+L("+w1+","+w2+")*cos(angl_dq-120deg)+L("+w1+","+w3+")*cos(angl_dq-240deg))*sin(angl_dq)+(L("+w2+","+w1+")*cos(angl_dq)+L("+w2+","+w2+")*cos(angl_dq-120deg)+L(" + \
                w2+","+w3+")*cos(angl_dq-240deg))*sin(angl_dq-120deg)+(L("+w3+","+w1+")*cos(angl_dq)+L(" + \
                w3+","+w2+")*cos(angl_dq-120deg)+L("+w3+","+w3 + \
                ")*cos(angl_dq-240deg))*sin(angl_dq-240deg))"
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

            name = "Lqq"
            # equation = "2/3*((L("+w1+","+w1+")*sin("+angle+")+L("+w1+","+w2+")*sin("+angle+"-2*pi/3)+L("+w1+","+w3+")*sin("+angle+"-4*pi/3))*sin("+angle+")+(L("+w2+","+w1+")*sin("+angle+")+L("+w2+","+w2+")*sin("+angle+"-2*pi/3)+L(" + \
            #     w2+","+w3+")*sin("+angle+"-4*pi/3))*sin("+angle+"-2*pi/3)+(L("+w3+","+w1+")*sin("+angle+")+L(" + \
            #     w3+","+w2+")*sin("+angle+"-2*pi/3)+L("+w3+","+w3 + \
            #     ")*sin("+angle+"-4*pi/3))*sin("+angle+"-4*pi/3))"
            equation = "2/3*((L("+w1+","+w1+")*sin(angl_dq)+L("+w1+","+w2+")*sin(angl_dq-120deg)+L("+w1+","+w3+")*sin(angl_dq-240deg))*sin(angl_dq)+(L("+w2+","+w1+")*sin(angl_dq)+L("+w2+","+w2+")*sin(angl_dq-120deg)+L(" + \
                w2+","+w3+")*sin(angl_dq-240deg))*sin(angl_dq-120deg)+(L("+w3+","+w1+")*sin(angl_dq)+L(" + \
                w3+","+w2+")*sin(angl_dq-120deg)+L("+w3+","+w3 + \
                ")*sin(angl_dq-240deg))*sin(angl_dq-240deg))"
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

            name = "Lqd"
            # equation = "2/3*((L("+w1+","+w1+")*sin("+angle+")+L("+w1+","+w2+")*sin("+angle+"-2*pi/3)+L("+w1+","+w3+")*sin("+angle+"-4*pi/3))*cos("+angle+")+(L("+w2+","+w1+")*sin("+angle+")+L("+w2+","+w2+")*sin("+angle+"-2*pi/3)+L(" + \
            #     w2+","+w3+")*sin("+angle+"-4*pi/3))*cos("+angle+"-2*pi/3)+(L("+w3+","+w1+")*sin("+angle+")+L(" + \
            #     w3+","+w2+")*sin("+angle+"-2*pi/3)+L("+w3+","+w3 + \
            #     ")*sin("+angle+"-4*pi/3))*cos("+angle+"-4*pi/3))"
            equation = "2/3*((L("+w1+","+w1+")*sin(angl_dq)+L("+w1+","+w2+")*sin(angl_dq-120deg)+L("+w1+","+w3+")*sin(angl_dq-240deg))*cos(angl_dq)+(L("+w2+","+w1+")*sin(angl_dq)+L("+w2+","+w2+")*sin(angl_dq-120deg)+L(" + \
                w2+","+w3+")*sin(angl_dq-240deg))*cos(angl_dq-120deg)+(L("+w3+","+w1+")*sin(angl_dq)+L(" + \
                w3+","+w2+")*sin(angl_dq-120deg)+L("+w3+","+w3 + \
                ")*sin(angl_dq-240deg))*cos(angl_dq-240deg))"
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        if (self.__phaseNumber == 3):
            name = 'Ld'
            angle = "(Moving1.Position/1deg %s)*%s*pi/180" % (initialPosition,
                                                              float(self.__poleNumber) / 2.0)
            L11 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[0], angle, self.__phaseLetters[1], self.__phaseLetters[0], angle, self.__phaseLetters[2], self.__phaseLetters[0])
            L12 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[1], angle, self.__phaseLetters[1], self.__phaseLetters[1], angle, self.__phaseLetters[2], self.__phaseLetters[1])
            L13 = '(cos(%s) * L(%s,%s) + cos(%s-2*pi/3) * L(%s,%s) + cos(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[2], angle, self.__phaseLetters[1], self.__phaseLetters[2], angle, self.__phaseLetters[2], self.__phaseLetters[2])
            equation = '2/3 * (cos(%s) * %s + cos(%s-2*pi/3) * %s + cos(%s+2*pi/3) * %s)' % (
                angle, L11, angle, L12, angle, L13)
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        if (self.__phaseNumber == 3):
            name = 'Lq'
            angle = "(Moving1.Position/1deg %s)*%s*pi/180" % (initialPosition,
                                                              float(self.__poleNumber) / 2.0)
            L11 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[0], angle, self.__phaseLetters[1], self.__phaseLetters[0], angle, self.__phaseLetters[2], self.__phaseLetters[0])
            L12 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[1], angle, self.__phaseLetters[1], self.__phaseLetters[1], angle, self.__phaseLetters[2], self.__phaseLetters[1])
            L13 = '(sin(%s) * L(%s,%s) + sin(%s-2*pi/3) * L(%s,%s) + sin(%s+2*pi/3) * L(%s,%s))' % (angle,
                                                                                                    self.__phaseLetters[0], self.__phaseLetters[2], angle, self.__phaseLetters[1], self.__phaseLetters[2], angle, self.__phaseLetters[2], self.__phaseLetters[2])
            equation = '2/3 * (sin(%s) * %s + sin(%s-2*pi/3) * %s + sin(%s+2*pi/3) * %s)' % (
                angle, L11, angle, L12, angle, L13)
            outputVariables.append(
                {'name': name, "unit": "H", 'equation': equation, 'type': 'Transient', 'integration factor': 1})

        return outputVariables
