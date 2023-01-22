import os
import sys
import math
from motorStudio.enums import *
from motorStudio.virtualTests import *
from ansysGeometries import ansysGeometries
from ansysMaterials import ansysMaterials
from ansysDefinitions import ansysDefinitions


class ansysSimulations:
    """Class ansyssim. It contains the methods to setup and run the test in ansys."""

    def __init__(self, oDesktop, meshSettings={}, machine=None, simulationSettings={}):
        """Constructor for the ansyssim class. None variables are defined in run method."""

        self.oDesktop = oDesktop
        self.oProject = oDesktop.GetActiveProject()
        self.machine = machine
        self.meshSettings = meshSettings
        self.simulationSettings = simulationSettings
        self.geometries = ansysGeometries(
            oDesktop, machine=machine, useSymmetry=self.simulationSettings["Use Symmetry"])
        # self.materials = ansysMaterials(
        #     oDesktop, machine=machine, geometries=self.geometries)
        self.definitions = None
        self.virtualTest = None

        if simulationSettings["Create New Design"]:
            self.oProject.InsertDesign(
                "Maxwell 2D", "DriveSimulations", "Transient", "")
            self.geometries.createAll(self.oProject)
            self.oDesktop.ClearMessages(self.oDesktop.GetActiveProject(
            ).GetName(), self.oProject.GetActiveDesign().GetName(), 1)

    def run(self, virtualTests=[]):

        for virtualTest in virtualTests:
            self.definitions = ansysDefinitions(self.oDesktop, virtualTest=virtualTest, geometries=self.geometries,
                                                meshSettings=self.meshSettings, useSymmetry=self.simulationSettings["Use Symmetry"])

            self.materials = ansysMaterials(
                self.oDesktop, machine=self.machine, geometries=self.geometries, virtualTest=virtualTest)

            virtualTest.run(oDesktop=self.oDesktop, materials=self.materials, definitions=self.definitions,
                            createNewMaterials=self.simulationSettings["Create New Materials"])
            # self.oDesktop.ClearMessages(self.oDesktop.GetActiveProject().GetName(), self.oProject.GetActiveDesign().GetName(), 1)

            # oProject = self.oDesktop.GetActiveProject()
            # self.materials.createAll(oProject, 25)
            # self.materials.assignAll(oProject, 25)
            # self.definitions.applyAll(oProject)
            # self.oDesktop.ClearMessages(self.oDesktop.GetActiveProject().GetName(), oProject.GetActiveDesign().GetName(), 1)
