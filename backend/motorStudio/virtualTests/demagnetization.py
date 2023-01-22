import os
from motorStudio.enums import *
from fractions import gcd
from utils import exportSolutionCSV


class demagnetization(object):
    """Calculates the demagnetization parameters."""

    def __init__(self, machine=None, currents=[1000], temperatures=[25], speed=1000, numberofPeriods=1, numberofTimeSteps=120):
        self.machine = machine
        self.speed = speed
        self.current = 1
        self.numberofPeriods = numberofPeriods
        self.numberofTimeSteps = numberofTimeSteps
        self.currents = currents
        self.temperatures = temperatures
        self.caption = "Demagnetization Virtual Test"
        self.description = ""

        if self.machine != None:
            self.__poleNumber = self.machine["design"]["Rotor"]["Pole Number"]

    def run(self, oDesktop=None, materials=None, definitions=None, createNewMaterials=True):
        oProject = oDesktop.GetActiveProject()
        oDesign = oProject.GetActiveDesign()

        for temperature in self.temperatures:
            if createNewMaterials:
                materials.createAll(oProject, temperature)
                materials.assignAll(oProject, temperature)

                for current in self.currents:
                    self.current = current

                    definitions.geometries.setBandSegments(
                        oProject=oProject, numberOfSegments=self.numberofTimeSteps)

                    print("Here...")
                    definitions.applyAll(oProject)
                    print("There...")

                    for state in ["on", "off"]:

                        if state == "on":
                            definitions.setDemagOn(oProject)
                        else:
                            definitions.setDemagOff(oProject)

                        oDesktop.AddMessage(
                            "", "", 0, "Running demagnetization %s test..." % (state))

                        oDesign.AnalyzeAll()

                        oDesktop.ClearMessages(oDesktop.GetActiveProject(
                        ).GetName(), oProject.GetActiveDesign().GetName(), 1)

                        path = oProject.GetPath() + "/Results/demagnetization/%s/" % (state) + str(temperature) + \
                            "C" + "/" + str(current) + "A"

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

                        if state == "on":
                            oDesktop.AddMessage(
                                "", "", 0, "The simulation will run once again! Please wait until finished.")
                        else:
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

        outputVariables = [
            {'name': 'Simulation_Time', 'unit': 's', 'equation': 'Time',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Torque', 'unit': 'NewtonMeter', 'equation': 'Moving1.Torque',
                'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Position', 'unit': 'deg',
                'equation': '(2*pi*Moving1.Speed/60rpm)*time * 180/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Speed', 'unit': 'rpm',
                'equation': 'deriv(Moving1.Position*1rad)*60/2/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': "B_Mag_AVG", 'unit': 'T',
                'equation': "B_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
            {'name': "H_Mag_AVG", 'unit': 'Ampere_per_meter',
                'equation': "H_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
            {'name': 'J_MAG_AVG', 'unit': 'T',
                'equation': "J_Mag_AVG_%s" % (partNames["Magnets"][0]), 'type': 'Fields', 'integration factor': 0.5},
        ]

        for i in range(1,  self.__poleNumber // self.machine["design"]["Symmetry Number"]):
            outputVariables.append({'name': "B_Mag_AVG_%d" % (i), 'unit': 'T',
                                    'equation': "B_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})
            outputVariables.append({'name': "H_Mag_AVG_%d" % (i), 'unit': 'Ampere_per_meter',
                                    'equation': "H_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})
            outputVariables.append({'name': "J_Mag_AVG_%d" % (i), 'unit': 'T',
                                    'equation': "J_Mag_AVG_%s_%d" % (partNames["Magnets"][0], i), 'type': 'Fields', 'integration factor': 0.5})

        return outputVariables
