import os
from motorStudio.enums import *
from fractions import gcd
from utils import exportSolutionCSV


class cogging(object):
    """Calculates the cogging torque of the machine"""

    def __init__(self, machine=None, speeds=[1000], temperatures=[25], numberofPeriods=1, numberofTimeSteps=120):
        self.machine = machine
        self.speed = 1000
        self.numberofPeriods = numberofPeriods
        self.numberofTimeSteps = numberofTimeSteps
        self.speeds = speeds
        self.temperatures = temperatures
        self.caption = "Cogging Virtual Test"
        self.description = ""

        if self.machine != None:
            self.__poleNumber = self.machine["design"]["Rotor"]["Pole Number"]
            self.__slotNumber = self.machine["design"]["Stator"]["Slot Number"]

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

                    oDesktop.AddMessage("", "", 1, "Running cogging test...")
                    oDesign.AnalyzeAll()

                    oDesktop.ClearMessages(oDesktop.GetActiveProject().GetName(), oProject.GetActiveDesign().GetName(), 1)
                    path = oProject.GetPath() + "/Results/cogging/" + str(temperature) + "C" + "/" + str(speed) + "rpm"
                    if not os.path.exists(path):
                        os.makedirs(path)

                    exportSolutionCSV(
                        oDesign,
                        oDesktop,
                        self.getOutputVariableDefinitions(),
                        self.simulationTime(),
                        self.timeStep(),
                        path
                    )

                    oDesktop.AddMessage("", "", 1, "Finished! Please check the \"%s\" directory in the current project folder. " % (path))
                    oDesign.DeleteFullVariation("All", False)

                    # When finished delete all reports
                    oModule = oDesign.GetModule("ReportSetup")
                    oModule.DeleteAllReports()

                    oProject.Save()
                    oDesktop.AddMessage("", "", 1, "Project saved. This increases the speed of the calculations.")

    def simulationTime(self):
        return 60.0 / self.speed * self.numberofPeriods / (self.__poleNumber * self.__slotNumber / gcd(self.__poleNumber, self.__slotNumber))

    def timeStep(self):
        return 60.0 / self.speed * self.numberofPeriods / (self.__poleNumber * self.__slotNumber / gcd(self.__poleNumber, self.__slotNumber)) / self.numberofTimeSteps

    def getOutputVariableDefinitions(self, partNames={}):
        """ Defines the ouput variables in form of tuple of dictionaries: ({'name':'variableName', 'equation':'variableEquation', 'type':'variableType'}). """

        outputVariables = [
            {'name': 'Simulation_Time', 'unit': 's', 'equation': 'Time', 'type': 'Transient', 'integration factor': 1},
            {'name': 'Shaft_Position', 'unit': 'deg', 'equation': '(2*pi*Moving1.Speed/60rpm)*time * 180/pi', 'type': 'Transient', 'integration factor': 0.5},
            {'name': 'Shaft_Torque', 'unit': 'NewtonMeter', 'equation': 'Moving1.Torque', 'type': 'Transient', 'integration factor': 1}
        ]

        return outputVariables
