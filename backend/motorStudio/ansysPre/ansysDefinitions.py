import os
import math
from motorStudio.enums import *
from motorStudio.virtualTests import *


class ansysDefinitions:
    """Class definitions. It contains the methods to setup the ansys simulation."""

    def __init__(self, oDesktop, virtualTest, geometries, meshSettings, useSymmetry):
        """
        Constructor for the ansyssim class.
        :param machine type: pmMachine.
        :param test type: tests.
        """
        self.oDesktop = oDesktop
        self.machine = virtualTest.machine
        self.virtualTest = virtualTest
        self.circuitName = "blockCircuit"
        self.meshSettings = meshSettings
        self.__phaseConnection = self.machine["design"]["Winding"]["Phase Connection"]["Used"]["name"]
        self.__phaseNumber = self.machine["design"]["Winding"]["Phase Number"]
        self.__slotNumber = self.machine["design"]["Stator"]["Slot Number"]
        self.__poleNumber = self.machine["design"]["Rotor"]["Pole Number"]
        self.__initialPosition = self.machine["design"]["Initial Position (deg)"]
        self.__toothThickness = self.machine["design"][
            "Stator"]["Sector"]["Slot"]["Tooth Thickness (mm)"]
        self.__yokeThickness = self.machine["design"][
            "Stator"]["Sector"]["Slot"]["Yoke Thickness (mm)"]
        self.__symmetryNumber = 1
        self.geometries = geometries

        if useSymmetry:
            self.__symmetryNumber = self.machine["design"]["Symmetry Number"]

    def applyAll(self, oProject):
        """ Calls all functions necessary for the ansys calculation. """

        self.__defineBand(oProject)
        self.__defineDesignSettings(oProject)
        self.__defineAnalysisSetup(oProject)
        self.__defineBoundaryConditions(oProject)
        self.__defineLossesCalculation(oProject)
        self.__createFieldVariables(oProject)
        self.__defineControlCircuit(oProject)
        self.__defineCoils(oProject)

        self.__defineOutputVariables(oProject)
        print("__defineOutputVariables...")

        self.__applyMeshSettings(oProject)

    def setDemagOn(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.ComputeOperatingPoints(
            ["NAME:OP_Option", "LinkType:=", "Demag"])

    def setDemagOff(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oModule.ComputeOperatingPoints(
            ["NAME:OP_Option", "LinkType:=", "None"])

    def __defineBand(self, oProject):
        """ Defines the motion band object. """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("ModelSetup")
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        motionSetup = ["NAME:Data", "Move Type:=", "Rotate", "Coordinate System:=", "Global", "Axis:=", "Z", "Is Positive:=", True,
                       "InitPos:=", str(
                           self.__initialPosition) + "deg", "HasRotateLimit:=", False, "NonCylindrical:="	, False,
                       "Consider Mechanical Transient:=", False, "Angular Velocity:=", str(
                           self.virtualTest.speed) + "rpm",
                       "Objects:=", oEditor.GetMatchedObjectName("Band*")]

        # self.oDesktop.AddMessage("", "", 1, str(oEditor.GetMatchedObjectName("band*")) + "in Band")

        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Band"]))):
            if len(oModule.GetMotionSetupNames()):
                oModule.EditMotionSetup(
                    oModule.GetMotionSetupNames()[0], motionSetup)
            else:
                oModule.AssignBand(motionSetup)
        else:
            print("No object named \"band\" could be found!")
            return False

        # self.oDesktop.AddMessage("", "", 0, str("band ok"))

        return True

    def __defineDesignSettings(self, oProject):
        """ Sets the design settings. """
        oDesign = oProject.GetActiveDesign()

        calculateIncrementalMatrix = False
        if type(self.virtualTest) == type(noload()):
            calculateIncrementalMatrix = True

        oDesign.SetDesignSettings([
            "NAME:Design Settings Data",
            "Perform Minimal validation:=", False,
            "EnabledObjects:=", [],
            "PreserveTranSolnAfterDatasetEdit:=", False,
            "ComputeTransientInductance:=", True,
            "ComputeIncrementalMatrix:=", calculateIncrementalMatrix,
            "PerfectConductorThreshold:=", 1E+030,
            "InsulatorThreshold:=", 1,
            "ModelDepth:=", str(
                self.machine["design"]["Stator"]["Stack Length (mm)"]) + "mm",

            "UseSkewModel:=", True if self.machine["design"][
                "Rotor"]["Skew Angle (deg)"] > 0 else False,
            "SkewType:=", "Step",
            "SkewPart:=", "Rotor",
            "SkewAngle:=", str(
                self.machine["design"]["Rotor"]["Skew Angle (deg)"]) + "deg",
            "NumberOfSlices:="	, str(self.machine["design"][
                "Rotor"]["Number of Skew Slices"]),
            "EnableTranTranLinkWithSimplorer:=", False,
            "BackgroundMaterialName:=", "vacuum",
            "Multiplier:=", str(self.__symmetryNumber)
        ], [
            "NAME:Model Validation Settings",
            "EntityCheckLevel:=", "Strict",
            "IgnoreUnclassifiedObjects:=", False,
            "SkipIntersectionChecks:=", False
        ])

        return True

    def __defineAnalysisSetup(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("AnalysisSetup")

        setupParameters = ["NAME:Setup1", "Enabled:=", True, "NonlinearSolverResidual:=", "0.0001",
                           "TimeIntegrationMethod:=", 0, "StopTime:=", str(
                               self.virtualTest.simulationTime()) + "s",
                           "TimeStep:=", str(
                               self.virtualTest.timeStep()) + "s",
                           "OutputError:=", False, "UseControlProgram:=", False, "ControlProgramName:=", "", "ControlProgramArg:=", "",
                           "CallCtrlProgAfterLastStep:=", False, "FastReachSteadyState:=", False, "IsGeneralTransient:=", True,
                           "NumberOfTimeSubDivisions:=", 1, "HasSweepSetup:=", True, "SweepSetupType:=", "LinearStep",
                           "StartValue:=", "0s", "StopValue:=", str(
                               self.virtualTest.simulationTime()) + "s",
                           "StepSize:=", str(
                               self.virtualTest.timeStep()) + "s",
                           "UseAdaptiveTimeStep:=", False, "InitialTimeStep:=", "0.002s",
                           "MinTimeStep:=", str(self.virtualTest.timeStep() / 3) + "s", "MaxTimeStep:=", str(self.virtualTest.timeStep()) + "s", "TimeStepErrTolerance:=", 0.0001]

        if len(oModule.GetSetups()) != 0:
            for setup in oModule.GetSetups():
                oModule.EditSetup(setup, setupParameters)
        else:
            oModule.InsertSetup("Transient", setupParameters)

        return True

    def __defineBoundaryConditions(self, oProject):
        """
        Defines all boundary conditions necessary for the calculation.
        :param oProject type: AnsysAPI.
        """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        oModule.DeleteAllBoundaries()

        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Region"]))):
            regionName = oEditor.GetMatchedObjectName(
                "%s*" % (self.geometries.partNames["Region"]))[0]
            # Outer baundary

            p = {"x": self.machine["design"]["Region"]
                 ["Outer Diameter (mm)"] / 2.0, "y": 0}
            p = self.__rotatePoint(p, 360.0 / self.__symmetryNumber / 2.0)
            edgeid = oEditor.GetEdgeByPosition(["NAME:EdgeParameters", "BodyName:=", regionName, "XPosition:=", str(
                p["x"]) + "mm", "YPosition:=", str(p["y"]) + "mm", "ZPosition:=", "0mm"])
            oModule.AssignVectorPotential(["NAME:VectorPotential", "Edges:=", [
                                          edgeid], "Value:=", "0", "CoordinateSystem:=", ""])

            if self.machine["design"]["Use Symmetry"] and self.__symmetryNumber > 1:
                # Master
                oModule.AssignMaster(["NAME:Master1", "Objects:=", [
                                     self.geometries.partNames["Master Line"]], "ReverseV:=", False])
                # Slave
                if self.__poleNumber / self.__symmetryNumber % 2 == 0:
                    oModule.AssignSlave(["NAME:Slave1", "Objects:=", [
                                        self.geometries.partNames["Slave Line"]], "ReverseU:=", False, "Master:=", "Master1", "SameAsMaster:=", True])
                else:
                    oModule.AssignSlave(["NAME:Slave1", "Objects:=", [
                                        self.geometries.partNames["Slave Line"]], "ReverseU:=", False, "Master:=", "Master1", "SameAsMaster:=", False])

                self.oDesktop.AddMessage(
                    "", "", 0, "Master and slave boundary conditions have been applied.")

        # if len(oModule.GetBoundariesOfType("Vector Potential")) == 0:
        #     oModule.AssignVectorPotential(["NAME:VectorPotential1", "Edges:=", [edgeid], "Value:=", "0", "CoordinateSystem:=", ""])

        else:
            print("No object named \"region\" could be found!")
            return False

        return True

    def __defineLossesCalculation(self, oProject):
        """ Defines if the eddy effects and the core losses are included in the calculation. """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        coreObjects = []
        coreObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Stator"]))
        coreObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Rotor"]))
        coreObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Stator Cutting"]))
        coreObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Rotor Cutting"]))
        # When "True" the core losses are substracted from the airgap-torque.
        if type(self.virtualTest) == type(cogging()):
            oModule.SetCoreLoss(coreObjects, False)
        else:
            oModule.SetCoreLoss(coreObjects, True)

        eddyObjects = []
        eddyObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Housing"]))
        eddyObjects += oEditor.GetMatchedObjectName(
            "%s*" % (self.geometries.partNames["Separation-Can"]))

        for magnetPart in self.geometries.partNames["Magnets"]:
            eddyObjects += oEditor.GetMatchedObjectName("%s*" % (magnetPart))

        eddyEffectVectorArray = ["NAME:EddyEffectVector"]
        for object in eddyObjects:
            if type(self.virtualTest) == type(cogging()) or type(self.virtualTest) == type(demagnetization()):
                eddyEffectVectorArray.append(
                    ["NAME:Data", "Object Name:=", object, "Eddy Effect:=", False])
            else:
                eddyEffectVectorArray.append(
                    ["NAME:Data", "Object Name:=", object, "Eddy Effect:=", True])

        oModule.SetEddyEffect(
            ["NAME:Eddy Effect Setting", eddyEffectVectorArray])

        return True

    def __createFieldVariables(self, oProject):
        """ Creates field variables used in the output variables. """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("FieldsReporter")
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        if (oModule.DoesNamedExpressionExists("Brad") != 1):
            oModule.EnterQty("B")
            oModule.CalcOp("ScalarX")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Cos")
            oModule.CalcOp("*")
            oModule.EnterQty("B")
            oModule.CalcOp("ScalarY")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Sin")
            oModule.CalcOp("*")
            oModule.CalcOp("+")
            oModule.AddNamedExpression("Brad", "Fields")

        if (oModule.DoesNamedExpressionExists("Btan") != 1):
            oModule.EnterQty("B")
            oModule.CalcOp("ScalarY")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Cos")
            oModule.CalcOp("*")
            oModule.EnterQty("B")
            oModule.CalcOp("ScalarX")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Sin")
            oModule.CalcOp("*")
            oModule.CalcOp("-")
            oModule.AddNamedExpression("Btan", "Fields")

        if (oModule.DoesNamedExpressionExists("Hrad") != 1):
            oModule.EnterQty("H")
            oModule.CalcOp("ScalarX")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Cos")
            oModule.CalcOp("*")
            oModule.EnterQty("H")
            oModule.CalcOp("ScalarY")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Sin")
            oModule.CalcOp("*")
            oModule.CalcOp("+")
            oModule.AddNamedExpression("Hrad", "Fields")

        if (oModule.DoesNamedExpressionExists("Htan") != 1):
            oModule.EnterQty("H")
            oModule.CalcOp("ScalarY")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Cos")
            oModule.CalcOp("*")
            oModule.EnterQty("H")
            oModule.CalcOp("ScalarX")
            oModule.CalcOp("Smooth")
            oModule.EnterScalarFunc("PHI")
            oModule.CalcOp("Sin")
            oModule.CalcOp("*")
            oModule.CalcOp("-")
            oModule.AddNamedExpression("Htan", "Fields")

        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Tooth Line"]))):
            if (oModule.DoesNamedExpressionExists("Btooth") != 1):
                oModule.CopyNamedExprToStack("Brad")
                oModule.EnterLine(self.geometries.partNames["Tooth Line"])
                oModule.CalcOp("Integrate")
                oModule.EnterScalar(self.__toothThickness * 1E-3)
                oModule.CalcOp("/")
                oModule.AddNamedExpression("Btooth", "Fields")
        else:
            print("No object named \"Tooth_Line\" could be found!")
            return False
        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Yoke Line"]))):
            if (oModule.DoesNamedExpressionExists("Byoke") != 1):
                oModule.CopyNamedExprToStack("Btan")
                oModule.EnterLine(self.geometries.partNames["Yoke Line"])
                oModule.CalcOp("Integrate")
                oModule.EnterScalar(self.__yokeThickness * 1E-3)
                oModule.CalcOp("/")
                oModule.AddNamedExpression("Byoke", "Fields")
        else:
            print("No object named \"Yoke_Line\" could be found!")
            return False
        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Housing"]))):
            if (oModule.DoesNamedExpressionExists("PeddyHousing") != 1):
                equation = ""
                for i, object in enumerate(oEditor.GetMatchedObjectName("Housing*")):
                    oModule.EnterQty("J")
                    oModule.CalcOp("ScalarZ")
                    oModule.CalcOp("Smooth")
                    oModule.EnterScalar(2)
                    oModule.CalcOp("Pow")
                    oModule.EnterSurf(object)
                    oModule.CalcOp("Integrate")
                    oModule.EnterScalar(self.machine["design"]["Housing"]["Material"]["Used"]["Conductivity (S/m)"] /
                                        self.machine["design"]["Stator"]["Stack Length (mm)"] / 1E-3 / self.__symmetryNumber)
                    oModule.CalcOp("/")
                    if i >= 1:
                        oModule.CalcOp("+")

                oModule.AddNamedExpression("PeddyHousing", "Fields")
        else:
            if (oModule.DoesNamedExpressionExists("PeddyHousing") != 1):
                oModule.EnterScalar(0)
                oModule.AddNamedExpression("PeddyHousing", "Fields")

        if len(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Separation-Can"]))):
            if (oModule.DoesNamedExpressionExists("PeddySeparationcan") != 1):
                equation = ""
                for i, object in enumerate(oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Separation-Can"]))):
                    oModule.EnterQty("J")
                    oModule.CalcOp("ScalarZ")
                    oModule.CalcOp("Smooth")
                    oModule.EnterScalar(2)
                    oModule.CalcOp("Pow")
                    oModule.EnterSurf(object)
                    oModule.CalcOp("Integrate")
                    oModule.EnterScalar(self.machine["design"]["Separation Can"]["Material"]["Used"]["Conductivity (S/m)"] /
                                        self.machine["design"]["Rotor"]["Stack Length (mm)"] / 1E-3 / self.__symmetryNumber)
                    oModule.CalcOp("/")
                    if i >= 1:
                        oModule.CalcOp("+")

                oModule.AddNamedExpression("PeddySeparationcan", "Fields")
        else:
            if (oModule.DoesNamedExpressionExists("PeddySeparationcan") != 1):
                oModule.EnterScalar(0)
                oModule.AddNamedExpression("PeddySeparationcan", "Fields")

        for magnetPart in self.geometries.partNames["Magnets"]:
            print("magnetPart", magnetPart)
            if len(oEditor.GetMatchedObjectName("%s*" % (magnetPart))):
                if (oModule.DoesNamedExpressionExists("PeddyMagnet") != 1):
                    # equation = ""
                    for i, object in enumerate(oEditor.GetMatchedObjectName("%s*" % (magnetPart))):
                        oModule.EnterQty("J")
                        oModule.CalcOp("ScalarZ")
                        oModule.CalcOp("Smooth")
                        oModule.EnterScalar(2)
                        oModule.CalcOp("Pow")
                        oModule.EnterSurf(object)
                        oModule.CalcOp("Integrate")
                        oModule.EnterScalar(self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Material"]["Used"]
                                            ["Conductivity (S/m)"] / self.machine["design"]["Rotor"]["Stack Length (mm)"] / 1E-3 / self.__symmetryNumber)
                        oModule.CalcOp("/")
                        if i >= 1:
                            oModule.CalcOp("+")

                    oModule.AddNamedExpression("PeddyMagnet", "Fields")

                # Expression to determine the average magnitude of B in magnet for demagnetization
                for i, object in enumerate(oEditor.GetMatchedObjectName("%s*" % (magnetPart))):
                    expressionName = "B_Mag_AVG_%s" % (object)

                    if (oModule.DoesNamedExpressionExists(expressionName) != 1):
                        oModule.EnterQty("B")
                        oModule.CalcOp("Mag")
                        oModule.CalcOp("Smooth")
                        oModule.EnterSurf(object)
                        oModule.CalcOp("Integrate")
                        oModule.EnterScalar(
                            self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Area (mm2)"]*1e-6)
                        oModule.CalcOp("/")
                        oModule.EnterScalar(
                            1 + self.machine["design"]["Effective Overhang (%)"] / 100.0)
                        oModule.CalcOp("/")

                        oModule.AddNamedExpression(expressionName, "Fields")

                for i, object in enumerate(oEditor.GetMatchedObjectName("%s*" % (magnetPart))):
                    expressionName = "H_Mag_AVG_%s" % (object)

                    if (oModule.DoesNamedExpressionExists(expressionName) != 1):
                        oModule.EnterQty("H")
                        oModule.CalcOp("Mag")
                        oModule.CalcOp("Smooth")
                        oModule.EnterSurf(object)
                        oModule.CalcOp("Integrate")
                        oModule.EnterScalar(
                            -self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Area (mm2)"]*1e-6)
                        oModule.CalcOp("/")
                        oModule.EnterScalar(
                            1 + self.machine["design"]["Effective Overhang (%)"] / 100.0)
                        oModule.CalcOp("/")

                        oModule.AddNamedExpression(expressionName, "Fields")

                # Expression to determine the average magnitude of B in magnet for demagnetization
                for i, object in enumerate(oEditor.GetMatchedObjectName("%s*" % (magnetPart))):
                    expressionName = "J_Mag_AVG_%s" % (object)

                    if (oModule.DoesNamedExpressionExists(expressionName) != 1):
                        # J = B - u0 * H
                        oModule.CopyNamedExprToStack("B_Mag_AVG_%s" % (object))
                        oModule.CopyNamedExprToStack("H_Mag_AVG_%s" % (object))
                        # u0 = 4 * pi * 1e-7 [H/m]
                        oModule.EnterScalar(1.25663706143592E-06)
                        oModule.CalcOp("*")
                        oModule.CalcOp("-")
                        oModule.AddNamedExpression(expressionName, "Fields")

            else:
                if (oModule.DoesNamedExpressionExists("PeddyMagnet") != 1):
                    oModule.EnterScalar(0)
                    oModule.AddNamedExpression("PeddyMagnet", "Fields")

        return True

    def __defineControlCircuit(self, oProject):
        """
        Creates the control circuit for the performance calculation and exports the netlist in the project directory. If the circuit with the predefined name already exists
        only the netlist of the existing circuit will be exported.
        """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oProject = self.oDesktop.GetActiveProject()

        if self.__phaseNumber != 3:
            self.oDesktop.AddMessage(
                "", "", 1, "Currently only 3 phase machines are supported.")
            return

        if type(self.virtualTest) == type(block120()):
            if self.__phaseConnection == "delta":
                circuitFile = oProject.GetPath() + "circuitDelta120.sph"
                if not os.path.isfile(circuitFile):
                    self.oDesktop.AddMessage(
                        "", "", 1, "Circuit file \"%s\" can not be found!." % (circuitFile))
                    return
                oModule.EditExternalCircuit(circuitFile, [
                                            "VVSource", "VVPULSE1", "VVPULSE2", "VVPULSE3", "VVPULSE4", "VVPULSE5", "VVPULSE6", "VIs"], [1, 2, 2, 2, 2, 2, 2, 1], [], [])
            else:
                circuitFile = oProject.GetPath() + "circuitStar120.sph"
                if not os.path.isfile(circuitFile):
                    self.oDesktop.AddMessage(
                        "", "", 1, "Circuit file \"%s\" can not be found!." % (circuitFile))
                    return
                oModule.EditExternalCircuit(circuitFile, [
                                            "VVSource", "VVPULSE1", "VVPULSE2", "VVPULSE3", "VVPULSE4", "VVPULSE5", "VVPULSE6", "VIs"], [1, 2, 2, 2, 2, 2, 2, 1], [], [])

            oModule.SetMinimumTimeStep(
                str(self.virtualTest.timeStep() / 10) + "s")
            self.oDesktop.AddMessage(
                "", "", 1, "Circuit file \"%s\" loaded successfully!." % (circuitFile))

        if type(self.virtualTest) == type(block180()):
            if self.__phaseConnection == "delta":
                circuitFile = oProject.GetPath() + "circuitDelta180.sph"
                if not os.path.isfile(circuitFile):
                    self.oDesktop.AddMessage(
                        "", "", 1, "Circuit file \"%s\" can not be found!." % (circuitFile))
                    return
                oModule.EditExternalCircuit(circuitFile, [
                                            "VVSource", "VVPULSE1", "VVPULSE2", "VVPULSE3", "VVPULSE4", "VVPULSE5", "VVPULSE6", "VIs"], [1, 2, 2, 2, 2, 2, 2, 1], [], [])
            else:
                circuitFile = oProject.GetPath() + "circuitStar180.sph"
                if not os.path.isfile(circuitFile):
                    self.oDesktop.AddMessage(
                        "", "", 1, "Circuit file \"%s\" can not be found!." % (circuitFile))
                    return
                oModule.EditExternalCircuit(circuitFile, [
                                            "VVSource", "VVPULSE1", "VVPULSE2", "VVPULSE3", "VVPULSE4", "VVPULSE5", "VVPULSE6", "VIs"], [1, 2, 2, 2, 2, 2, 2, 1], [], [])

            oModule.SetMinimumTimeStep(
                str(self.virtualTest.timeStep() / 10) + "s")
            self.oDesktop.AddMessage(
                "", "", 1, "Circuit file \"%s\" loaded successfully!." % (circuitFile))

    def __defineCoils(self, oProject):
        """Creates the winding groups and assigns the coils to the corresponding winding group."""
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        terminals = oEditor.GetMatchedObjectName("Phase_*")
        if oDesign.GetSolutionType() == 'Transient':
            for terminal in terminals:
                phase, slot, direction = terminal.split("_")[1], terminal.split("_")[
                    3], terminal.split("_")[5]

                self.__createWindingGroups(oModule, phase)

                coilParam = ["NAME:" + terminal, "Objects:=", [terminal],
                             "Conductor number:=", str(
                                 self.machine["design"]["Winding"]["Coil"]["Winding Number"]),
                             "ParentBndID:=", phase,
                             "Winding:=", phase,
                             "PolarityType:=", "Positive" if direction == "in" else "Negative"]

                if len(oEditor.GetMatchedObjectName("%s*" % (terminal))):
                    if (terminal in oModule.GetExcitationsOfType("Coil")):
                        oModule.EditCoil(terminal, coilParam)
                    else:
                        oModule.AssignCoil(coilParam)
                else:
                    print("No objact named \"%s\" could be found!" % (terminal))
                    return False

            # # if os.path.exists(os.path.join(self.project.ansysDirectory, self.project.calculationOrder.projectName + ".sph")):
            # #     oModule.EditExternalCircuit(os.path.join(self.project.ansysDirectory, self.project.calculationOrder.projectName + ".sph").replace("\\", "\\\\"),
            # #                                 ["VVPULSE3", "VVPULSE4", "VVs", "VVPULSE1", "VVPULSE2", "VVPULSE5", "VVPULSE6", "VIs"], [2, 2, 1, 2, 2, 2, 2, 1], [], [])
            # # else:
            # #     print("The netlist \"%s.sph\" could not be found. The test will not be performed." % (self.project.calculationOrder.projectName))
            # #     return False

        return True

    def __applyMeshSettings(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("MeshSetup")
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        oModule.InitialMeshSettings(
            [
                "NAME:MeshSettings",
                [
                    "NAME:GlobalSurfApproximation",
                    "CurvedSurfaceApproxChoice:=", "UseSlider",
                    "SliderMeshSettings:=", int(
                        self.meshSettings["Mesh Quality"])
                ],
                [
                    "NAME:GlobalModelRes",
                    "UseAutoLength:=", True
                ],
                "MeshMethod:=", self.meshSettings["Mesh Engine"]
            ])

        # if not "__rotor" in oModule.GetOperationNames("Edge Cut Based"):
        #     oModule.AssignEdgeCutLayerOp(["NAME:EdgeCut_rotor", "Objects:=", ["__rotor", ], "Layer Thickenss:=",  str(self.machine["design"]["Rotor"]["Cutting Thickness (mm)"]) + "mm"])
        # else:
        #     oModule.EditEdgeCutLayerOp()
        #
        # if not "__stator" in oModule.GetOperationNames("Edge Cut Based"):
        #     oModule.AssignEdgeCutLayerOp(["NAME:EdgeCut_stator", "Objects:=", ["__stator"], "Layer Thickenss:=", str(self.machine["design"]["Stator"]["Cutting Thickness (mm)"]) + "mm"])

        # # Magnet mesh settings
        # if len(oEditor.GetMatchedObjectName("magnet*")):
        #     objects = oEditor.GetMatchedObjectName("magnet*")
        #
        #     if not "magnets" in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp([
        #             "NAME:%s" % ("magnets"),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "Objects:=", objects,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 25.5) + "mm"
        #         ])
        #     else:
        #         oModule.EditLengthOp("magnets", [
        #             "NAME:%s" % ("magnets"),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 25.5) + "mm"
        #         ])
        #
        # # Rotor Cutting Area mesh settings
        # if len(oEditor.GetMatchedObjectName("__rotor*")):
        #     name = oEditor.GetMatchedObjectName("__rotor*")
        #
        #     if not name[0] in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp([
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "Objects:=", [name[0]],
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Cutting Thickness (mm)"] * 3.0) + "mm"])
        #     else:
        #         oModule.EditLengthOp(name[0], [
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Cutting Thickness (mm)"] * 3.0) + "mm"])
        #
        # # Stator Cutting Area mesh settings
        # if len(oEditor.GetMatchedObjectName("__stator*")):
        #     objects = oEditor.GetMatchedObjectName("__stator*")
        #
        #     if not "__stator" in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp([
        #             "NAME:%s" % ("__stator"),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "Objects:=", objects,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Cutting Thickness (mm)"] * 3.0) + "mm"])
        #     else:
        #         oModule.EditLengthOp("__stator", [
        #             "NAME:%s" % ("__stator"),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Cutting Thickness (mm)"] * 3.0) + "mm"])
        #
        # # Rotor mesh settings
        # if len(oEditor.GetMatchedObjectName("rotor*")):
        #     name = oEditor.GetMatchedObjectName("rotor*")
        #
        #     if not name[0] in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp([
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "Objects:=", [name[0]],
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 25.0) + "mm"])
        #     else:
        #         oModule.EditLengthOp(name[0], [
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 25.0) + "mm"])
        #
        # # Stator mesh settings
        # if len(oEditor.GetMatchedObjectName("stator*")):
        #     name = oEditor.GetMatchedObjectName("stator*")
        #
        #     if not name[0] in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp([
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "Objects:=", [name[0]],
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Outer Diameter (mm)"] / 30.0) + "mm"])
        #     else:
        #         oModule.EditLengthOp(name[0], [
        #             "NAME:%s" % (name[0]),
        #             "RefineInside:=", True,
        #             "Enabled:=", True,
        #             "RestrictElem:=", False,
        #             "NumMaxElem:=", "1000",
        #             "RestrictLength:=", True,
        #             "MaxLength:=", str(self.machine["design"]["Stator"]["Outer Diameter (mm)"] / 30.0) + "mm"])

        # # Band mesh settings
        # if self.virtualTest:
        #     dAlpha = (2 * math.pi * self.virtualTest.speed / 60) * self.virtualTest.timeStep() * self.__symmetryNumber
        #     chordLength = 2 * self.machine["design"]["Band"]["Outer Diameter (mm)"] / 2.0 * math.sqrt(1 - math.cos(dAlpha / 2.0) ** 2.0)
        # else:
        #     chordLength = 1  # mm
        #
        # if len(oEditor.GetMatchedObjectName("band*")):
        #     bandName = oEditor.GetMatchedObjectName("band*")
        #     p = {"x": self.machine["design"]["Band"]["Outer Diameter (mm)"] / 2.0, "y": 0}
        #     p = self.__rotatePoint(p, 180.0 / self.__poleNumber)
        #     edgeid = oEditor.GetEdgeByPosition(["NAME:EdgeParameters", "BodyName:=", bandName[0], "XPosition:=", str(p["x"]) + "mm", "YPosition:=", str(p["y"]) + "mm", "ZPosition:=", "0mm"])
        #
        #     if not bandName[0] in oModule.GetOperationNames("Length Based"):
        #         oModule.AssignLengthOp(["NAME:%s" % (bandName[0]), "RefineInside:=", False, "Enabled:=", True, "Edges:=", [edgeid], "RestrictElem:=",
        #                                 False, "NumMaxElem:=", "1000", "RestrictLength:=", True, "MaxLength:=", str(chordLength) + "mm"])
        #     else:
        #
        #         oModule.EditLengthOp(bandName[0], ["NAME:%s" % (bandName[0]), "RefineInside:=", False, "RestrictElem:=", False, "RestrictLength:=", True, "MaxLength:=",  str(chordLength) + "mm"])

        # # Symmetry boundaries
        # if len(oEditor.GetMatchedObjectName("region*")):
        #     regionName = oEditor.GetMatchedObjectName("region*")
        #     for i in range(len(regionName)):
        #         if self.machine["design"]["Use Symmetry"] and self.__symmetryNumber > 1:
        #             if i == 0:
        #                 # Master
        #                 lineName = "master"
        #                 p = {"x": self.machine["design"]["Region"]["Outer Diameter (mm)"] / 4.0, "y": 0}
        #                 edgeid = oEditor.GetEdgeByPosition(["NAME:EdgeParameters", "BodyName:=", regionName[i], "XPosition:=", str(p["x"]) + "mm", "YPosition:=", str(p["y"]) + "mm", "ZPosition:=", "0mm"])
        #
        #                 if not lineName in oModule.GetOperationNames("Length Based"):
        #                     oModule.AssignLengthOp(["NAME:%s" % (lineName), "RefineInside:=", False, "Enabled:=", True, "Edges:=", [edgeid], "RestrictElem:=",
        #                                             False, "NumMaxElem:=", "1000", "RestrictLength:=", True, "MaxLength:=", str(2) + "mm"])
        #                 else:
        #                     oModule.EditLengthOp(lineName, ["NAME:%s" % (lineName), "RefineInside:=", False, "RestrictElem:=", False, "RestrictLength:=", True, "MaxLength:=",  str(2) + "mm"])
        #
        #             if i == len(regionName) - 1:
        #                 # Slave
        #                 lineName = "slave"
        #                 p = {"x": self.machine["design"]["Region"]["Outer Diameter (mm)"] / 4.0, "y": 0}
        #                 p = self.__rotatePoint(p, 360.0 / self.__symmetryNumber)
        #
        #                 edgeid = oEditor.GetEdgeByPosition(["NAME:EdgeParameters", "BodyName:=", regionName[i], "XPosition:=", str(p["x"]) + "mm", "YPosition:=", str(p["y"]) + "mm", "ZPosition:=", "0mm"])
        #                 if not lineName in oModule.GetOperationNames("Length Based"):
        #                     oModule.AssignLengthOp(["NAME:%s" % (lineName), "RefineInside:=", False, "Enabled:=", True, "Edges:=", [edgeid], "RestrictElem:=",
        #                                             False, "NumMaxElem:=", "1000", "RestrictLength:=", True, "MaxLength:=", str(2) + "mm"])
        #                 else:
        #                     oModule.EditLengthOp(lineName, ["NAME:%s" % (lineName), "RefineInside:=", False, "RestrictElem:=", False, "RestrictLength:=", True, "MaxLength:=",  str(2) + "mm"])

        oDesign.ApplyMeshOps(["Setup1"])

    def __defineOutputVariables(self, oProject):
        """
        Defines all output variables of the solution.
        :param oProject type: AnsysAPI.
        """
        oDesign = oProject.GetActiveDesign()
        oModule = oDesign.GetModule("BoundarySetup")
        # windingGroups = oModule.GetExcitationsOfType("Winding Group")
        oModule = oDesign.GetModule("OutputVariable")
        # oEditor = oDesign.SetActiveEditor("3D Modeler")

        # delete all existing variables
        for variable in oModule.GetOutputVariables():
            oModule.DeleteOutputVariable(variable)

        for var in self.virtualTest.getOutputVariableDefinitions(partNames=self.geometries.partNames):
            # vars += ({'name':'simulationTime', 'equation':'Time', 'type':'Transient'}, )

            if var['type'] == "Transient":
                if var['name'] in oModule.GetOutputVariables():
                    oModule.EditOutputVariable(
                        var['name'], var['equation'], var['name'], "Setup1 : Transient", "Transient", [])
                else:
                    oModule.CreateOutputVariable(
                        var['name'], var['equation'], "Setup1 : Transient", "Transient", [])
            else:
                if var['name'] in oModule.GetOutputVariables():
                    oModule.EditOutputVariable(
                        var['name'], var['equation'], var['name'], "Setup1 : Transient", "Fields", [])
                else:
                    oModule.CreateOutputVariable(
                        var['name'], var['equation'], "Setup1 : Transient", "Fields", [])

    def __createWindingGroups(self, oModule, phase):
        """ Creates the winding group. Peak current [A] and speed [rpm] used only for foc control."""

        if type(self.virtualTest) == type(noload()) or type(self.virtualTest) == type(cogging()):
            excitationType = "Voltage"
            resistance = str(1) + "megOhm"
            current = "0mA"
        elif type(self.virtualTest) == type(block120()) or type(self.virtualTest) == type(block180()):
            excitationType = "External"
            resistance = str(0) + "Ohm"
            current = "0mA"
        elif type(self.virtualTest) == type(foc()):
            excitationType = "Current"
            resistance = str(0) + "Ohm"

            self.__initialPosition

            if phase == 'A':

                # current = "%s * sin(2 * pi * %s / 60 * Time * %s - %s)" % (
                #     self.virtualTest.current, self.virtualTest.speed, self.__poleNumber / 2, 0)
                current = "%s * cos((2 * pi * %s / 60 * Time) * %s + pi)-%s*sin((2 * pi * %s / 60 * Time ) * %s + pi)" % (
                    self.virtualTest.id, self.virtualTest.speed, self.__poleNumber / 2, self.virtualTest.iq, self.virtualTest.speed, self.__poleNumber / 2)
            if phase == 'B':
                # current = "%s * sin(2 * pi * %s / 60 * Time * %s - %s)" % (
                #     self.virtualTest.current, self.virtualTest.speed, self.__poleNumber / 2, 2 * math.pi / 3)
                current = "%s * cos((2 * pi * %s / 60 * Time) * %s + pi - 2 * pi / 3)-%s*sin((2 * pi * %s / 60 * Time ) * %s + pi - 2 * pi / 3)" % (
                    self.virtualTest.id, self.virtualTest.speed, self.__poleNumber / 2,  self.virtualTest.iq, self.virtualTest.speed, self.__poleNumber / 2)

            if phase == 'C':
                # current = "%s * sin(2 * pi * %s / 60 * Time * %s - %s)" % (
                #     self.virtualTest.current, self.virtualTest.speed, self.__poleNumber / 2, 4 * math.pi / 3)

                current = "%s * cos((2 * pi * %s / 60 * Time) * %s + pi - 4 * pi / 3)-%s*sin((2 * pi * %s / 60 * Time ) * %s + pi - 4 * pi / 3)" % (
                    self.virtualTest.id, self.virtualTest.speed, self.__poleNumber / 2,  self.virtualTest.iq, self.virtualTest.speed, self.__poleNumber / 2)

        elif type(self.virtualTest) == type(demagnetization()):
            excitationType = "Current"
            resistance = str(0) + "Ohm"
            if self.__phaseConnection == "delta":
                if phase == 'A':
                    current = "2.0 / 3.0 * %s" % (self.virtualTest.current)
                if phase == 'B':
                    current = "-1.0 / 3.0 * %s" % (self.virtualTest.current)
                if phase == 'C':
                    current = "-1.0 / 3.0 * %s" % (self.virtualTest.current)
            else:
                if phase == 'A':
                    current = "%s" % (self.virtualTest.current)
                if phase == 'B':
                    current = "-%s" % (self.virtualTest.current)
                if phase == 'C':
                    current = "%s" % (0)

        windingParameters = ["NAME:" + phase, "Type:=", excitationType,
                             "IsSolid:=", False, "Current:=", current,
                             "Resistance:=", resistance, "Inductance:=", "0nH",
                             "Voltage:=", "0mV", "ParallelBranchesNum:=", str(self.machine["design"]["Winding"]["Parallel Coils"])]

        if phase in oModule.GetExcitationsOfType("Winding Group"):
            oModule.EditWindingGroup(phase, windingParameters)
        else:
            oModule.AssignWindingGroup(windingParameters)

    def __getIDs(self):
        oEditor = self.project.oDesign.SetActiveEditor("SchematicEditor")
        ids = []
        for comp in oEditor.GetAllComponents():
            ids.append(int(oEditor.GetPropertyValue(
                "ComponentTab", comp, "ID")))
        return ids

    def __createComponent(self, **kwargs):
        """ Creates the maxwell circuit component. """
        # oEditor = self.project.oDesign.SetActiveEditor("SchematicEditor")
        oDesign = kwargs['oDesign']
        oEditor = oDesign.SetActiveEditor("SchematicEditor")
        x = kwargs['x']
        y = kwargs['y']
        angle = kwargs['angle']
        id = kwargs['id']
        elementName = kwargs['elementName']
        properties = kwargs['properties']
        componentName = 'CompInst@%s;%s' % (elementName.split(":")[1], id)

        oEditor.CreateComponent(["NAME:ComponentProps", "Name:=", elementName, "Id:=", str(id)], [
                                "NAME:Attributes", "Page:=", 1, "X:=", x, "Y:=", y, "Angle:=", angle, "Flip:=", False])
        for key in properties:
            oEditor.SetPropertyValue(
                "PassedParameterTab", componentName, key, properties[key])

    def __rotatePoint(self, p, angle):
        x, y = p["x"], p["y"]

        return {
            "x": x * math.cos(angle * math.pi / 180) - y * math.sin(angle * math.pi / 180),
            "y": x * math.sin(angle * math.pi / 180) + y * math.cos(angle * math.pi / 180)
        }
