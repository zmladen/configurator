from motorStudio.enums import *
import math
import os


class ansysGeometries:
    """
    Class ansysgeom. It contains the methods to plot single objects of the drive machine in ansys Maxwell (e.g. slot, sector, terminal, etc.)
    """

    def __init__(self, oDesktop, machine, useSymmetry):
        """ Constructor for the bldc machine object with the needed parameters """
        # self.bandObjectNames = [] # Set when band object is created
        self.machine = machine
        self.oDesktop = oDesktop
        self.partNames = {
            "Region": "Region",
            "Inner Region": "Inner_Region",
            "Band": "Band",
            "Separation-Can": "Separation_Can",
            "Terminal Left": "Terminal_Left",
            "Terminal Right": "Terminal_Right",
            "Tooth Line": "Tooth_Line",
            "Yoke Line": "Yoke_Line",
            "Master Line": "MasterLine",
            "Slave Line": "SlaveLine",
            "Stator Cutting": "__Stator",
            "Rotor Cutting": "__Rotor",
            "Stator": None,  # Defined by the user as the file name. Has to contain stator in name!
            "Rotor": None,
            "Magnets": [],
            "Housing": None,
            "Shaft": None,
            "Spoke Closing Bridge": None,
            "Spoke Left Connection": None,
            "Spoke Right Connection": None
        }

        if useSymmetry:
            self.__symmetryNumber = self.machine["design"]["Symmetry Number"]
        else:
            self.__symmetryNumber = 1

    def createAll(self, oProject):
        """ Creates all machine geometry necessary for the calculation. """

        self.createMagnetCoordinateSystems(oProject)
        self.importSTEPGeometry(oProject)
        self.createMasterSlaveLines(oProject)
        self.assignMagnetCoordinateSystems(oProject)

    def assignMagnetCoordinateSystems(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        csNames = [i for i in oEditor.GetCoordinateSystems() if i not in [
            "Global"]]

        for index, magnet in enumerate(oEditor.GetMatchedObjectName("Magnet*")):
            # print(index, magnet)
            oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", magnet], [
                                   "NAME:ChangedProps", ["NAME:Orientation", "Value:=", csNames[index]]]]])

    def createMagnetCoordinateSystems(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        for position in range(len(self.machine["design"]["Rotor"]["Magnetization Vectors"])):
            RCSname = "RCS_" + "magnet" + "_" + str(position)
            self.__createMagnetCS(
                oEditor, self.machine["design"]["Rotor"]["Magnetization Vectors"][position], RCSname)

        oEditor.SetWCS(["NAME:SetWCS Parameter", "Working Coordinate System:=",
                       "Global", "RegionDepCSOk:="	, False])

    def importSTEPGeometry(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        geomPath = os.path.join(oProject.GetPath(), "step")

        # Import geometry from the stl folder
        for index, file in enumerate([f for f in os.listdir(geomPath) if f.endswith('.step')]):
            fileName = os.path.splitext(file)[0]  # No extension
            oEditor.Import([
                "NAME:NativeBodyParameters",
                "HealOption:=", 0,
                "Options:=", "-1",
                "FileType:=", "UnRecognized",
                "MaxStitchTol:=", -1,
                "ImportFreeSurfaces:=", False,
                "GroupByAssembly:=", False,
                "CreateGroup:=", False,
                "STLFileUnit:=", "Auto",
                "MergeFacesAngle:=", 0.02,
                "PointCoincidenceTol:=", 1E-006,
                "SourceFile:=", os.path.join(geomPath, file)
            ])
            objectName = oEditor.GetObjectName(index)

            # Change name of the imported object to file name
            if objectName != fileName:
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", [
                                       "NAME:PropServers",  objectName], ["NAME:ChangedProps", ["NAME:Name", "Value:=", fileName]]]])

        # Rotate and merge the segments

        for object in oEditor.GetMatchedObjectName("*"):
            if "stator_segment" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Stator"]["Sector"]["Color"])
                angle = self.machine["design"]["Stator"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Stator"]["Slot Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Stator"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "spoke_closing_bridge" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Stator"]["Sector"]["Cutting Areas Color"])
                angle = self.machine["design"]["Stator"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Stator"]["Slot Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Spoke Closing Bridge"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "spoke_right_connection" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Stator"]["Sector"]["Cutting Areas Color"])
                angle = self.machine["design"]["Stator"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Stator"]["Slot Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Spoke Right Connection"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "spoke_left_connection" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Stator"]["Sector"]["Cutting Areas Color"])
                angle = self.machine["design"]["Stator"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Stator"]["Slot Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Spoke Left Connection"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "rotor_segment" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Rotor"]["Pole"]["Color"])
                angle = self.machine["design"]["Rotor"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Rotor"]["Pole Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Rotor"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "magnet_segment" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Color"])
                angle = self.machine["design"]["Rotor"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Rotor"]["Pole Number"] / \
                    self.__symmetryNumber
                unite = False
                self.partNames["Magnets"].append(object)
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "magnet_right" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Color"])
                angle = self.machine["design"]["Rotor"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Rotor"]["Pole Number"] / \
                    self.__symmetryNumber
                unite = False
                self.partNames["Magnets"].append(object)
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "magnet_left" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Color"])
                angle = self.machine["design"]["Rotor"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Rotor"]["Pole Number"] / \
                    self.__symmetryNumber
                unite = False
                self.partNames["Magnets"].append(object)
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])

            elif "housing" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Housing"]["Color"])
                angle = self.machine["design"]["Housing"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Housing"]["Segment Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Housing"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "shaft" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Shaft"]["Color"])
                angle = self.machine["design"]["Shaft"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Shaft"]["Segment Number"] / \
                    self.__symmetryNumber
                unite = True
                self.partNames["Shaft"] = object
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif "separation_can" in object.lower():
                rgbColor = self.__hex_to_rgb(
                    self.machine["design"]["Separation Can"]["Color"])
                angle = self.machine["design"]["Separation Can"]["Segment Angle (deg)"]
                clones = self.machine["design"]["Separation Can"]["Segment Number"] / \
                    self.__symmetryNumber
                unite = True
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", object], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
                self.partNames["Separation-Can"] = object
            else:
                angle = None
                clones = None
                unite = False

            if angle != None and clones != None:
                selections = object
                for i in range(1, clones):
                    selections += ", %s_%s" % (object, i)

                # print("Part => ", object, "Unite", unite)
                # print(selections)
                oEditor.DuplicateAroundAxis(
                    ["NAME:Selections", "Selections:=", object,
                        "NewPartsModelFlag:=", "Model"],
                    ["NAME:DuplicateAroundAxisParameters",	"CreateNewObjects:=", True,	"WhichAxis:=",
                     "Z", "AngleStr:=", str(angle) + "deg", "NumClones:=", str(clones)],
                    ["NAME:Options", "DuplicateAssignments:=", False],
                    ["CreateGroupsForNewObjects:=", False]
                )

                if unite:
                    oEditor.Unite(
                        ["NAME:Selections",	"Selections:=", selections],
                        ["NAME:UniteParameters", "KeepOriginals:=", False]
                    )

        # Create region
        self.createPieSegment(
            oProject=oProject,
            name=self.partNames["Region"],
            diameter=self.machine["design"]["Region"]["Outer Diameter (mm)"],
            numberOfLineSegments=0,
            segmentAngle=360.0/self.__symmetryNumber)

        # Create band
        if "Outer Diameter (mm)" in self.machine["design"]["Band"] and "Inner Diameter (mm)" in self.machine["design"]["Band"]:
            self.createRingSegment(
                oProject=oProject,
                name=self.partNames["Band"],
                innerDiameter=self.machine["design"]["Band"]["Inner Diameter (mm)"],
                outerDiameter=self.machine["design"]["Band"]["Outer Diameter (mm)"],
                numberOfLineSegments=0,
                segmentAngle=360.0/self.__symmetryNumber)
        else:
            self.createPieSegment(
                oProject=oProject,
                name=self.partNames["Band"],
                diameter=self.machine["design"]["Band"]["Outer Diameter (mm)"],
                numberOfLineSegments=0,
                segmentAngle=360.0/self.__symmetryNumber)

        # Create inner-region
        if "Outer Diameter (mm)" in self.machine["design"]["Inner Region"] and "Inner Diameter (mm)" in self.machine["design"]["Inner Region"]:
            self.createRingSegment(
                oProject=oProject,
                name=self.partNames["Inner Region"],
                innerDiameter=self.machine["design"][
                    "Inner Region"]["Inner Diameter (mm)"],
                outerDiameter=self.machine["design"][
                    "Inner Region"]["Outer Diameter (mm)"],
                numberOfLineSegments=0,
                segmentAngle=360.0/self.__symmetryNumber)
        else:
            self.createPieSegment(
                oProject=oProject,
                name=self.partNames["Inner Region"],
                diameter=self.machine["design"]["Inner Region"]["Outer Diameter (mm)"],
                numberOfLineSegments=0,
                segmentAngle=360.0/self.__symmetryNumber)

        # Create coils
        slotConnectionTable = self.__modifyConnectionTable(
            self.machine["design"]["Winding"]["Layout"]["Connection Table"]['table'])
        for slotNumber in range(self.machine["design"]["Stator"]["Slot Number"] / self.__symmetryNumber):
            # print(slotConnectionTable[slotNumber])
            leftTerminal = slotConnectionTable[slotNumber][self.partNames["Terminal Left"]]
            rightTerminal = slotConnectionTable[slotNumber][self.partNames["Terminal Right"]]
            angle = self.machine["design"]["Stator"]["Segment Angle (deg)"]

            oEditor.DuplicateAroundAxis(
                ["NAME:Selections", "Selections:=",
                    self.partNames["Terminal Left"], "NewPartsModelFlag:=", "Model"],
                ["NAME:DuplicateAroundAxisParameters",	"CreateNewObjects:=", True,	"WhichAxis:=",
                    "Z", "AngleStr:=", str(slotNumber * angle) + "deg", "NumClones:=", "2"],
                ["NAME:Options", "DuplicateAssignments:=", False],
                ["CreateGroupsForNewObjects:=", False]
            )

            oEditor.DuplicateAroundAxis(
                ["NAME:Selections", "Selections:=",
                    self.partNames["Terminal Right"], "NewPartsModelFlag:=", "Model"],
                ["NAME:DuplicateAroundAxisParameters",	"CreateNewObjects:=", True,	"WhichAxis:=",
                    "Z", "AngleStr:=", str(slotNumber * angle) + "deg", "NumClones:=", "2"],
                ["NAME:Options", "DuplicateAssignments:=", False],
                ["CreateGroupsForNewObjects:=", False]
            )

            terminalLeftName = "Phase_%s_Slot_%s_Direction_%s_Terminal_Left" % (
                leftTerminal["phase"], slotNumber, leftTerminal["direction"])
            terminalRightName = "Phase_%s_Slot_%s_Direction_%s_Terminal_Right" % (
                rightTerminal["phase"], slotNumber, rightTerminal["direction"])

            oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers",  "Terminal_Left_1"], [
                                   "NAME:ChangedProps", ["NAME:Name", "Value:=", terminalLeftName]]]])
            oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers",  "Terminal_Right_1"], [
                                   "NAME:ChangedProps", ["NAME:Name", "Value:=", terminalRightName]]]])

            if leftTerminal["phase"] == "A":
                rgbColor = self.__hex_to_rgb("#FF0000")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalLeftName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif leftTerminal["phase"] == "B":
                rgbColor = self.__hex_to_rgb("#008000")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalLeftName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif leftTerminal["phase"] == "C":
                rgbColor = self.__hex_to_rgb("#0000FF")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalLeftName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            else:
                pass

            if rightTerminal["phase"] == "A":
                rgbColor = self.__hex_to_rgb("#FF0000")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalRightName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif rightTerminal["phase"] == "B":
                rgbColor = self.__hex_to_rgb("#008000")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalRightName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            elif rightTerminal["phase"] == "C":
                rgbColor = self.__hex_to_rgb("#0000FF")
                oEditor.ChangeProperty(["NAME:AllTabs", ["NAME:Geometry3DAttributeTab", ["NAME:PropServers", terminalRightName], [
                                       "NAME:ChangedProps", ["NAME:Color", "R:=", rgbColor[0], "G:=", rgbColor[1], "B:=", rgbColor[2]]]]])
            else:
                pass

        oEditor.Delete(["NAME:Selections", "Selections:=",
                       "Terminal_Left,Terminal_Right"])
        self.oDesktop.AddMessage(
            "", "", 0, "STEP Geometry successfully imported.")

    def __modifyConnectionTable(self, table):
        slots = {}
        for row in table:
            if row["inSlot"] in slots:
                if row["inPosition"] == 1:
                    slots[row["inSlot"]].update({self.partNames["Terminal Left"]: {
                                                "phase": row["phase"], "direction": "in"}})
                else:
                    slots[row["inSlot"]].update({self.partNames["Terminal Right"]: {
                                                "phase": row["phase"], "direction": "in"}})
            else:
                if row["inPosition"] == 1:
                    slots[row["inSlot"]] = {self.partNames["Terminal Left"]: {
                        "phase": row["phase"], "direction": "in"}}
                else:
                    slots[row["inSlot"]] = {self.partNames["Terminal Right"]: {
                        "phase": row["phase"], "direction": "in"}}

            if row["outSlot"] in slots:
                if row["outPosition"] == 1:
                    slots[row["outSlot"]].update({self.partNames["Terminal Left"]: {
                                                 "phase": row["phase"], "direction": "out"}})
                else:
                    slots[row["outSlot"]].update({self.partNames["Terminal Right"]: {
                                                 "phase": row["phase"], "direction": "out"}})
            else:
                if row["outPosition"] == 1:
                    slots[row["outSlot"]] = {self.partNames["Terminal Left"]: {
                        "phase": row["phase"], "direction": "out"}}
                else:
                    slots[row["outSlot"]] = {self.partNames["Terminal Right"]: {
                        "phase": row["phase"], "direction": "out"}}

        return slots

    def createPieSegment(self, oProject=None, name="circle1", diameter=10, numberOfLineSegments=25, segmentAngle=45):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        oEditor.CreateCircle(
            [
                "NAME:CircleParameters",
                "IsCovered:="		, True,
                "XCenter:="		, "0mm",
                "YCenter:="		, "0mm",
                "ZCenter:="		, "0mm",
                "Radius:="		, str(diameter / 2.0) + "mm",
                "WhichAxis:="		, "Z",
                "NumSegments:="		, str(numberOfLineSegments)
            ],
            [
                "NAME:Attributes",
                "Name:="		, name,
                "Flags:="		, "",
                "Color:="		, "(255 255 255)",
                "Transparency:="	, 0.6,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\"vacuum\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="		, True,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False
            ])
        if segmentAngle < 360.0:
            oEditor.Split(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:SplitToParameters",
                    "SplitPlane:="		, "ZX",
                    "WhichSide:="		, "PositiveOnly",
                    "ToolType:="		, "PlaneTool",
                    "ToolEntityID:="	, -1,
                    "ToolPartID:="		, -1,
                    "SplitCrossingObjectsOnly:=", False,
                    "DeleteInvalidObjects:=", True
                ])
            oEditor.Rotate(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:RotateParameters",
                    "RotateAxis:="		, "Z",
                    "RotateAngle:="		, str(-segmentAngle) + "deg"
                ])
            oEditor.Split(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:SplitToParameters",
                    "SplitPlane:="		, "ZX",
                    "WhichSide:="		, "NegativeOnly",
                    "ToolType:="		, "PlaneTool",
                    "ToolEntityID:="	, -1,
                    "ToolPartID:="		, -1,
                    "SplitCrossingObjectsOnly:=", False,
                    "DeleteInvalidObjects:=", True
                ])
            oEditor.Rotate(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:RotateParameters",
                    "RotateAxis:="		, "Z",
                    "RotateAngle:="		, str(segmentAngle) + "deg"
                ])

    def createRingSegment(self, oProject=None, name="circle1", innerDiameter=10, outerDiameter=20, numberOfLineSegments=25, segmentAngle=45):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        name_tool = name + "_tool"

        oEditor.CreateCircle(
            [
                "NAME:CircleParameters",
                "IsCovered:="		, True,
                "XCenter:=", "0mm",
                "YCenter:=", "0mm",
                "ZCenter:=", "0mm",
                "Radius:=", str(outerDiameter / 2.0) + "mm",
                "WhichAxis:=", "Z",
                "NumSegments:=", str(numberOfLineSegments)
            ],
            [
                "NAME:Attributes",
                "Name:=", name,
                "Flags:=", "",
                "Color:=", "(255 255 255)",
                "Transparency:=", 0.6,
                "PartCoordinateSystem:=", "Global",
                "UDMId:=", "",
                "MaterialValue:="	, "\"vacuum\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="		, True,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False
            ])

        oEditor.CreateCircle(
            [
                "NAME:CircleParameters",
                "IsCovered:="		, True,
                "XCenter:="		, "0mm",
                "YCenter:="		, "0mm",
                "ZCenter:="		, "0mm",
                "Radius:="		, str(innerDiameter / 2.0) + "mm",
                "WhichAxis:="		, "Z",
                "NumSegments:="		, str(numberOfLineSegments)
            ],
            [
                "NAME:Attributes",
                "Name:="		, name_tool,
                "Flags:="		, "",
                "Color:="		, "(255 255 255)",
                "Transparency:="	, 0.6,
                "PartCoordinateSystem:=", "Global",
                "UDMId:="		, "",
                "MaterialValue:="	, "\"vacuum\"",
                "SurfaceMaterialValue:=", "\"\"",
                "SolveInside:="		, True,
                "IsMaterialEditable:="	, True,
                "UseMaterialAppearance:=", False
            ])

        oEditor.Subtract(
            [
                "NAME:Selections",
                "Blank Parts:="		, name,
                "Tool Parts:="		, name_tool
            ],
            [
                "NAME:SubtractParameters",
                "KeepOriginals:="	, False
            ])

        if segmentAngle < 360.0:
            oEditor.Split(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:SplitToParameters",
                    "SplitPlane:="		, "ZX",
                    "WhichSide:="		, "PositiveOnly",
                    "ToolType:="		, "PlaneTool",
                    "ToolEntityID:="	, -1,
                    "ToolPartID:="		, -1,
                    "SplitCrossingObjectsOnly:=", False,
                    "DeleteInvalidObjects:=", True
                ])
            oEditor.Rotate(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:RotateParameters",
                    "RotateAxis:="		, "Z",
                    "RotateAngle:="		, str(-segmentAngle) + "deg"
                ])
            oEditor.Split(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:SplitToParameters",
                    "SplitPlane:="		, "ZX",
                    "WhichSide:="		, "NegativeOnly",
                    "ToolType:="		, "PlaneTool",
                    "ToolEntityID:="	, -1,
                    "ToolPartID:="		, -1,
                    "SplitCrossingObjectsOnly:=", False,
                    "DeleteInvalidObjects:=", True
                ])
            oEditor.Rotate(
                [
                    "NAME:Selections",
                    "Selections:="		, name,
                    "NewPartsModelFlag:="	, "Model"
                ],
                [
                    "NAME:RotateParameters",
                    "RotateAxis:="		, "Z",
                    "RotateAngle:="		, str(segmentAngle) + "deg"
                ])

    def createMasterSlaveLines(self, oProject):
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")
        p1 = (0, 0)
        p2 = (self.machine["design"]["Region"]["Outer Diameter (mm)"] / 2, 0)
        p3 = self.__rotatePoint(p2, 360.0 / self.__symmetryNumber)
        if self.__symmetryNumber > 1:
            oEditor.CreatePolyline(
                [
                    "NAME:PolylineParameters",
                    "IsPolylineCovered:="	, True,
                    "IsPolylineClosed:="	, False,
                    [
                        "NAME:PolylinePoints",
                        [
                            "NAME:PLPoint",
                            "X:="			, str(p1[0]) + "mm",
                            "Y:="			, str(p1[1]) + "mm",
                            "Z:="			, "0mm"
                        ],
                        [
                            "NAME:PLPoint",
                            "X:="			, str(p2[0]) + "mm",
                            "Y:="			, str(p2[1]) + "mm",
                            "Z:="			, "0mm"
                        ]
                    ],
                    [
                        "NAME:PolylineSegments",
                        [
                            "NAME:PLSegment",
                            "SegmentType:="		, "Line",
                            "StartIndex:="		, 0,
                            "NoOfPoints:="		, 2
                        ]
                    ]
                ],
                [
                    "NAME:Attributes",
                    "Name:="		, "MasterLine",
                    "Flags:="		, "",
                    "Color:="		, "(143 175 143)",
                    "Transparency:="	, 0,
                    "PartCoordinateSystem:=", "Global",
                    "UDMId:="		, "",
                    "MaterialValue:="	, "\"vacuum\"",
                    "SurfaceMaterialValue:=", "\"\"",
                    "SolveInside:="		, True,
                    "IsMaterialEditable:="	, True,
                    "UseMaterialAppearance:=", False
                ])

            oEditor.CreatePolyline(
                [
                    "NAME:PolylineParameters",
                    "IsPolylineCovered:="	, True,
                    "IsPolylineClosed:="	, False,
                    [
                        "NAME:PolylinePoints",
                        [
                            "NAME:PLPoint",
                            "X:="			, str(p1[0]) + "mm",
                            "Y:="			, str(p1[1]) + "mm",
                            "Z:="			, "0mm"
                        ],
                        [
                            "NAME:PLPoint",
                            "X:="			, str(p3[0]) + "mm",
                            "Y:="			, str(p3[1]) + "mm",
                            "Z:="			, "0mm"
                        ]
                    ],
                    [
                        "NAME:PolylineSegments",
                        [
                            "NAME:PLSegment",
                            "SegmentType:="		, "Line",
                            "StartIndex:="		, 0,
                            "NoOfPoints:="		, 2
                        ]
                    ]
                ],
                [
                    "NAME:Attributes",
                    "Name:="		, "SlaveLine",
                    "Flags:="		, "",
                    "Color:="		, "(143 175 143)",
                    "Transparency:="	, 0,
                    "PartCoordinateSystem:=", "Global",
                    "UDMId:="		, "",
                    "MaterialValue:="	, "\"vacuum\"",
                    "SurfaceMaterialValue:=", "\"\"",
                    "SolveInside:="		, True,
                    "IsMaterialEditable:="	, True,
                    "UseMaterialAppearance:=", False
                ])

    def __createMagnetCS(self, oEditor, vectors, name):
        """ Creates relative coordinate systems for each magnet part. This coordinate systems are used to define the magenetization pattern. """

        RCSParameters = ["NAME:RelativeCSParameters",
                         "Mode:=", "Axis/Position", "OriginX:=", str(
                             0) + "mm", "OriginY:=", str(0) + "mm", "OriginZ:=", "0mm",
                         "XAxisXvec:=", str(vectors["xVector"]["x"]) + "mm",
                         "XAxisYvec:=", str(vectors["xVector"]["y"]) + "mm",
                         "XAxisZvec:=", "0mm",
                         "YAxisXvec:=", str(vectors["yVector"]["x"]) + "mm",
                         "YAxisYvec:=", str(vectors["yVector"]["y"]) + "mm",
                         "YAxisZvec:=", "0mm"]

        # In case other coordinate system is left selected!
        oEditor.SetWCS(["NAME:SetWCS Parameter", "Working Coordinate System:=",
                       "Global", "RegionDepCSOk:=", False])

        if name in oEditor.GetCoordinateSystems():
            oEditor.EditRelativeCS(
                RCSParameters, ["NAME:Attributes", "Name:=", name])
        else:
            oEditor.CreateRelativeCS(
                RCSParameters, ["NAME:Attributes", "Name:=", name])

        oEditor.SetWCS(["NAME:SetWCS Parameter", "Working Coordinate System:=",
                       "Global", "RegionDepCSOk:=", False])

    def setBandSegments(self, oProject, numberOfSegments):

        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        # Inner-runner band
        if "Outer Diameter (mm)" in self.machine["design"]["Band"] and "Inner Diameter (mm)" in self.machine["design"]["Band"]:
            oEditor.ChangeProperty(
                ["NAME:AllTabs",
                 ["NAME:Geometry3DCmdTab",
                  ["NAME:PropServers", "Band_tool:CreateCircle:1"],
                  ["NAME:ChangedProps", ["NAME:Number of Segments", "Value:=",
                                         str(int(self.__symmetryNumber * numberOfSegments))]]
                  ]
                 ])
        else:
            oEditor.ChangeProperty(
                ["NAME:AllTabs",
                 ["NAME:Geometry3DCmdTab",
                  ["NAME:PropServers", "Band:CreateCircle:1"],
                  ["NAME:ChangedProps", ["NAME:Number of Segments", "Value:=",
                                         str(int(self.__symmetryNumber * numberOfSegments))]]
                  ]
                 ])

    def __rotatePoint(self, p, angle):
        x, y = p[0], p[1]
        return (x * math.cos(angle * math.pi / 180) - y * math.sin(angle * math.pi / 180), x * math.sin(angle * math.pi / 180) + y * math.cos(angle * math.pi / 180))

    def __hex_to_rgb(self, value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + int(lv / 3)], 16) for i in range(0, lv, int(lv / 3)))
