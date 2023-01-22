import os
import json
from utilities import *
from pmMachine import *
from win32com import client
import ansysPre
import ansysPost
import drawSVG
from virtualTests import *


class project(object):
    """
    Class project. This class manages the calculation project and creates working directories for saving the calculation results.

    :param string projectName: Name of the project. To save calculation results in the current working directory the new directory with this name is created to store the calculation results and reports.
    :param machine machine: Machine object to be calculated.
    :param n-dict tests: Tests dictionary containing the information about all the tests to be performed.
    """

    def __init__(self, calculationOrder, test, machine={}, workingDirectory=os.getcwd(), ansysProjectFile=None, modifyMaterials=True, modifyControlCircuit=True):

        self.test = test
        self.calculationOrder = calculationOrder
        self.workingDirectory = workingDirectory
        self.modifyMaterials = modifyMaterials
        self.modifyControlCircuit = modifyControlCircuit

        if machine != {}:
            self.machine = pmMachine(data=machine['design'])

        else:
            self.machine = pmMachine()

        self.circuitName = "mycontrolcircuit"
        self.designName = "mydesign"
        self.projectDirectory = os.path.join(self.workingDirectory, self.calculationOrder.projectName)
        self.variationDirectory = os.path.join(self.workingDirectory, self.calculationOrder.projectName, self.calculationOrder.variationName)
        self.imageDirectory = os.path.join(self.workingDirectory, self.calculationOrder.projectName, self.calculationOrder.variationName,  "images")
        self.testsDirectory = os.path.join(self.workingDirectory, self.calculationOrder.projectName, self.calculationOrder.variationName,  "tests")
        self.ansysDirectory = os.path.join(self.workingDirectory, self.calculationOrder.projectName, self.calculationOrder.variationName,  "ansys")
        self.machineFile = os.path.join(self.variationDirectory, "machine.json")
        self.reportFile = os.path.join(self.variationDirectory, "calculationReport.html")
        self.__createDirectories()

        self.ansysProjectFile = ansysProjectFile
        self.slotImageName = "slot.svg"
        self.rotorImageName = "rotor.svg"
        self.statorImageName = "stator.svg"
        self.layoutImageName = "layout.svg"

        self.oProject = None
        self.parts = drawSVG.parts(self)
        self.geometries = ansysPre.geometries(self)
        self.definitions = ansysPre.definitions(self)
        self.materials = ansysPre.materials(self)
        self.solutions = ansysPost.solutions(self)

    def runVirtualTests(self):
        if type(self.test) == type(cogging()):
            self.simulations.runCogging()
        elif type(self.test) == type(noload()):
            self.simulations.runNoload()
        elif type(self.test) == type(block120()):
            self.simulations.runBlock120()

    def createReport(self):
        self.solutions.createHTMLReport()
        self.parts.drawRotorXY(filename=self.imageDirectory + "\\" + self.rotorImageName, createNewGroup=True)
        self.parts.drawStatorXY(filename=self.imageDirectory + "\\" + self.statorImageName, createNewGroup=True)
        self.saveJSON(self.machineFile)

    def initializeAnsys(self):
        self.oProject = self.__getAnsysProject()
        if self.oProject != None:
            designs = [design.GetName() for design in self.oProject.GetDesigns()]
            if not self.designName in designs:
                self.oProject.InsertDesign("Maxwell 2D", self.designName, "Transient", "")
                self.geometries.createAll()
                self.materials.createMaterials()
                self.materials.assignMaterials()

            self.simulations = ansysPre.simulations(self)
            self.oProject.SaveAs(self.ansysDirectory + "\\" + self.calculationOrder.projectName + ".aedt", True)
        else:
            print("Ansys project could not be initialized! No calculations will be performed!")
            return False

        return True

    def __isProjectOpen(self):
        """ Checks if the ANSYS project is opened. """
        filename, extension = os.path.splitext(os.path.basename(self.ansysProjectFile))
        for pjt in self.oDesktop.GetProjects():
            if filename == pjt.GetName():
                return True
        return False

    def __getAnsysProject(self):
        """ Initializes the ANSYS model. """
        self.oAnsoftApp = client.Dispatch("Ansoft.ElectronicsDesktop")
        self.oDesktop = self.oAnsoftApp.GetAppDesktop()

        if self.ansysProjectFile == None:
            return self.oDesktop.NewProject(self.calculationOrder.projectName)
        else:
            if self.__isProjectOpen() == False:
                if os.path.exists(self.ansysProjectFile):
                    print("Project >> %s << is found. Opening now." % (self.ansysProjectFile))
                    return self.oDesktop.OpenProject(self.ansysProjectFile)
                else:
                    print("Project >> %s << could not be found. Please check the file name." % (self.ansysProjectFile))
                    return None
            else:
                print("Project >> %s << is already opened. Make sure that the geometry is created. " % (self.ansysProjectFile))
                return self.oDesktop.SetActiveProject(self.calculationOrder.projectName)

    def __createDirectories(self):
        """ Creates the main output directory. """

        if not os.path.exists(self.projectDirectory):
            os.makedirs(self.projectDirectory)
        if not os.path.exists(self.variationDirectory):
            os.makedirs(self.variationDirectory)
        if not os.path.exists(self.imageDirectory):
            os.makedirs(self.imageDirectory)
        if not os.path.exists(self.testsDirectory):
            os.makedirs(self.testsDirectory)
        if not os.path.exists(self.ansysDirectory):
            os.makedirs(self.ansysDirectory)

    def readJSON(self, filename):
        """ reads json representation of the object. """
        with open(filename) as json_data:
            data = json.load(json_data)
        json_data.close()
        return data['Machine']

    def saveJSON(self, filename):
        """ Creates json representation of the object. """

        data = {
            'Parts': self.machine.reprJSON(),
            'Phase Data': self.solutions.getPhaseValues(),
        }

        with open(filename, 'w') as json_data:
            json.dump(data, json_data, cls=ComplexEncoder, indent=3)
        json_data.close()
