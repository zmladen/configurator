import os
import shutil
from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
from math import pi, cos, sin, sqrt
from utils import spiral, circle, point, svg
import numpy as np
import FreeCAD
import importSVG
import Part
import Sketcher
import importDXF
import Import
import random
import string


class geometry(object):
    def __init__(self, stator, winding):
        """Geometry class to control the freecad stator templates. Supported freecad version 0.18."""

        self.stator = stator
        self.winding = winding
        self.activeDocument = None
        self.svg = None
        self.tempDirPath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "stator", "geometry", "templates", "freecad", "temp")

        if self.stator.type == 1:
            # Inner-runner needle winding
            self.templateName = "StatorIRRoundBack"
        elif self.stator.type == 3:

            if self.winding.coilSpan == 1:
                # Inner-runner needle winding
                self.templateName = "StatorIRNeedleWinding"
            else:
                self.templateName = "StatorIRNeedleWindingCoilSpan"

        elif self.stator.type == 5:
            # Outer runner needle winding
            self.templateName = "StatorORNeedleWinding"
        elif self.stator.type == 7:
            # Inner-runner spoke stator ellipse
            self.templateName = "StatorIRSpokeEllipse"

        else:
            self.templateName = "StatorIRNeedleWinding"

        self.openDocument()

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "stator", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

        self.tempTemplateName = self.templateName + "_" + \
            ''.join(random.sample((string.ascii_uppercase+string.digits), 6))
        self.freecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "stator", "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
        shutil.copy(orginalFreecadTemplatePath, self.freecadTemplatePath)

        # print("############################################################")
        # print("Stator Type:", self.stator.type)
        # print("############################################################")

        if self.activeDocument == None:
            FreeCAD.open(self.freecadTemplatePath)
            FreeCAD.setActiveDocument(self.tempTemplateName)
            self.activeDocument = FreeCAD.getDocument(self.tempTemplateName)
            self.__setSpreadsheetParameters()

    def closeDocument(self):
        # self.saveTemp()
        FreeCAD.closeDocument(self.tempTemplateName)
        self.__deleteTempFolder()
        self.activeDocument = None

    def __setDependentSpreadsheetParameters(self):
        """Here the parameters are set that are dependent on the standard parameters."""
        try:
            self.activeDocument.Spreadsheet.set(
                'axialHeight', str(self.winding.coil.axialHeight))
            self.activeDocument.recompute()

        except Exception as e:
            print(str(e))
            self.closeDocument()

    def __setSpreadsheetParameters(self):
        try:
            self.activeDocument.Spreadsheet.set(
                'outerDiameter', str(self.stator.outerDiameter))
            self.activeDocument.Spreadsheet.set(
                'innerDiameter', str(self.stator.innerDiameter))
            self.activeDocument.Spreadsheet.set(
                'slotNumber', str(self.stator.slotNumber))
            self.activeDocument.Spreadsheet.set(
                'stackLength', str(self.stator.stacklength))
            self.activeDocument.Spreadsheet.set(
                'stackingFactor', str(self.stator.stackingFactor))
            self.activeDocument.Spreadsheet.set(
                'cuttingThickness', str(self.stator.cuttingThickness))
            self.activeDocument.Spreadsheet.set('tipHeightReduction', str(
                self.stator.sector.slot.tipHeightReduction))
            self.activeDocument.Spreadsheet.set(
                'toothThickness', str(self.stator.sector.slot.toothThickness))
            self.activeDocument.Spreadsheet.set(
                'yokeThickness', str(self.stator.sector.slot.yokeThickness))
            self.activeDocument.Spreadsheet.set(
                'tipHeight', str(self.stator.sector.slot.tipHeight))
            self.activeDocument.Spreadsheet.set(
                'tipAngle', str(self.stator.sector.slot.tipAngle))
            self.activeDocument.Spreadsheet.set(
                'openingLeft', str(self.stator.sector.slot.openingLeft))
            self.activeDocument.Spreadsheet.set(
                'openingRight', str(self.stator.sector.slot.openingRight))
            self.activeDocument.Spreadsheet.set(
                'backWidth', str(self.stator.sector.slot.backWidth))

            self.activeDocument.Spreadsheet.set(
                'phaseSeparation', str(self.winding.phaseSeparation))
            self.activeDocument.Spreadsheet.set(
                'slotIsolation', str(self.winding.slotIsolation))
            self.activeDocument.Spreadsheet.set(
                'axialOverhang', str(self.winding.axialOverhang))

            if self.stator.type == 7:
                self.activeDocument.Spreadsheet.set(
                    'spokeBridgeHeight', str(self.stator.sector.slot.spokeBridgeHeight))
                self.activeDocument.Spreadsheet.set(
                    'connectionHeight', str(self.stator.sector.slot.connectionHeight))
                self.activeDocument.Spreadsheet.set(
                    'connectionWidth', str(self.stator.sector.slot.connectionWidth))
                self.activeDocument.Spreadsheet.set(
                    'connectionThickness', str(self.stator.sector.slot.connectionThickness))

            # self.activeDocument.Spreadsheet.set('roundingRadii', str(self.stator.sector.slot.roundingRadius))
            self.activeDocument.recompute()
        except Exception as e:
            print(str(e))
            self.closeDocument()

    def saveTemp(self):
        self.activeDocument.saveAs(os.path.join(
            self.tempDirPath, "tmpStator.FCStd"))

    def __deleteTempFolder(self):
        try:
            shutil.rmtree(self.tempDirPath, ignore_errors=True)
        except OSError as e:
            print("Error: %s : %s" % (self.tempDirPath, e.strerror))

    def __createTempFolder(self):
        os.makedirs(self.tempDirPath, exist_ok=True)

    def __getSVGFromFreeCad(self, fileName=None, faces=[]):
        try:
            if fileName == None:
                print("Please define the name of the SVG file.")
                return ""
            else:
                __objs__ = []
                isValid = True
                for face in faces:
                    sketch = self.activeDocument.getObject(
                        self.activeDocument.getObjectsByLabel(face["label"])[0].Name)
                    __objs__.append(sketch)
                    # sketch.recompute() returns True if sketch is valid
                    isValid = isValid and sketch.recompute()

                # Export SVG to file
                importSVG.export(__objs__, os.path.join(
                    self.tempDirPath, fileName))
                del __objs__

                # Read and modify attributes
                return (svg.modifySVGAttributes(fileName=fileName, tempDirPath=self.tempDirPath, faces=faces), isValid)
        except Exception as e:
            print(str(e))

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        terminalLeftGroup = None
        terminalRightGroup = None
        connectionTable = self.winding.layout.getConnectionTable()["table"]

        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("TerminalLeftSketch"):
                terminalLeftGroup = ElementTree.fromstring(
                    ElementTree.tostring(group))
                root.remove(group)

            if title.text == "b'%s'" % ("TerminalRightSketch"):
                terminalRightGroup = ElementTree.fromstring(
                    ElementTree.tostring(group))
                root.remove(group)

        if terminalLeftGroup != None and terminalRightGroup != None:

            for i, row in enumerate(connectionTable):

                if (row["inPosition"] == 1):
                    group_tmp_left = ElementTree.fromstring(
                        ElementTree.tostring(terminalLeftGroup))
                    group_tmp_right = ElementTree.fromstring(
                        ElementTree.tostring(terminalRightGroup))

                if (row["inPosition"] == 2):
                    group_tmp_left = ElementTree.fromstring(
                        ElementTree.tostring(terminalRightGroup))
                    group_tmp_right = ElementTree.fromstring(
                        ElementTree.tostring(terminalLeftGroup))

                transform_tmp = group_tmp_left.get("transform")
                transform_tmp += " rotate(%s)" % (
                    row['inSlot'] * 360.0 / self.stator.slotNumber)
                group_tmp_left.set("transform", transform_tmp)

                for path in group_tmp_left.findall("path"):
                    # Only change color
                    if row["phase"] == "A":
                        path.set("style", path.get("style") +
                                 ";fill:Red" + ";stroke:Red")
                    elif row["phase"] == "B":
                        path.set("style", path.get("style") +
                                 ";fill:Green" + ";stroke:Green")
                    elif row["phase"] == "C":
                        path.set("style", path.get("style") +
                                 ";fill:Blue" + ";stroke:Blue")
                    else:
                        path.set("style", path.get("style") +
                                 ";fill:White" + ";stroke:Red")

                root.append(group_tmp_left)

                transform_tmp = group_tmp_right.get("transform")
                transform_tmp += " rotate(%s)" % (
                    row['outSlot'] * 360.0 / self.stator.slotNumber)
                group_tmp_right.set("transform", transform_tmp)

                for path in group_tmp_right.findall("path"):
                    # Only change color
                    if row["phase"] == "A":
                        path.set("style", path.get("style") +
                                 ";fill:Red" + ";stroke:Red")
                    elif row["phase"] == "B":
                        path.set("style", path.get("style") +
                                 ";fill:Green" + ";stroke:Green")
                    elif row["phase"] == "C":
                        path.set("style", path.get("style") +
                                 ";fill:Blue" + ";stroke:Blue")
                    else:
                        path.set("style", path.get("style") +
                                 ";fill:White" + ";stroke:Red")

                root.append(group_tmp_right)

        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("StatorSketch1") or title.text == "b'%s'" % ("StatorSketch2") or title.text == "b'%s'" % ("StatorCuttingAreasSketch"):
                for i in range(1, self.stator.slotNumber):
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i *
                                                      360.0 / self.stator.slotNumber)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" % (rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __addWireLeftIsolationCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotLeftWindingsIsolation')
            self.activeDocument.SlotLeftWindingsIsolation.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotLeftWindingsIsolation.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireLeftCoordinates:
                self.activeDocument.SlotLeftWindingsIsolation.addGeometry(Part.Circle(FreeCAD.Vector(p["x"], p["y"], 0), FreeCAD.Vector(
                    0, 0, 1), self.winding.coil.wire.gauge[self.winding.coil.wire.isolationGrade]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireLeftConductorCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotLeftWindingsConductor')
            self.activeDocument.SlotLeftWindingsConductor.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotLeftWindingsConductor.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireLeftCoordinates:
                self.activeDocument.SlotLeftWindingsConductor.addGeometry(Part.Circle(FreeCAD.Vector(
                    p["x"], p["y"], 0), FreeCAD.Vector(0, 0, 1), self.winding.coil.wire.gauge["Conductor Diameter (mm)"]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireRightIsolationCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotRightWindingsIsolation')
            self.activeDocument.SlotRightWindingsIsolation.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotRightWindingsIsolation.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireRightCoordinates:
                self.activeDocument.SlotRightWindingsIsolation.addGeometry(Part.Circle(FreeCAD.Vector(p["x"], p["y"], 0), FreeCAD.Vector(
                    0, 0, 1), self.winding.coil.wire.gauge[self.winding.coil.wire.isolationGrade]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireRightConductorCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotRightWindingsConductor')
            self.activeDocument.SlotRightWindingsConductor.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotRightWindingsConductor.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireRightCoordinates:
                self.activeDocument.SlotRightWindingsConductor.addGeometry(Part.Circle(FreeCAD.Vector(
                    p["x"], p["y"], 0), FreeCAD.Vector(0, 0, 1), self.winding.coil.wire.gauge["Conductor Diameter (mm)"]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireSingleIsolationCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotSingleWindingsIsolation')
            self.activeDocument.SlotSingleWindingsIsolation.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotSingleWindingsIsolation.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireSingleCoordinates:
                self.activeDocument.SlotSingleWindingsIsolation.addGeometry(Part.Circle(FreeCAD.Vector(p["x"], p["y"], 0), FreeCAD.Vector(
                    0, 0, 1), self.winding.coil.wire.gauge[self.winding.coil.wire.isolationGrade]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireSingleConductorCircles(self):
        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotSingleWindingsConductor')
            self.activeDocument.SlotSingleWindingsConductor.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotSingleWindingsConductor.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireSingleCoordinates:
                self.activeDocument.SlotSingleWindingsConductor.addGeometry(Part.Circle(FreeCAD.Vector(
                    p["x"], p["y"], 0), FreeCAD.Vector(0, 0, 1), self.winding.coil.wire.gauge["Conductor Diameter (mm)"]/2), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def getTerminalSingleCoordinates(self):
        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("TerminalSingleSketch")[0].Name)

            coord = []
            for v in __object__.Shape.Vertexes:
                coord.append(point(v.X, v.Y).rotateCopy(
                    90-self.stator.segmentAngle/2))
            return coord
        except Exception as e:
            print(str(e))

    def getTerminalLeftCoordinates(self):
        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("TerminalLeftSketch")[0].Name)

            coord = []
            for v in __object__.Shape.Vertexes:
                coord.append(point(v.X, v.Y).rotateCopy(
                    90-self.stator.segmentAngle/2))
            return coord
        except Exception as e:
            print(str(e))

    def getTerminalRightCoordinates(self):
        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("TerminalRightSketch")[0].Name)
            coord = []
            for v in __object__.Shape.Vertexes:
                coord.append(point(v.X, v.Y).rotateCopy(
                    90-self.stator.segmentAngle/2))

            return coord
        except Exception as e:
            print(str(e))

    def getSlotArea(self):
        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("SlotSketch_Surface")[0].Name)
            area = __object__.Shape.Area

            return area
        except Exception as e:
            print(str(e))

    def __getDXFFromFreeCAD(self, label):
        print(self.activeDocument)
        objects = self.activeDocument.getObjectsByLabel(label)

        if len(objects):
            sketch = self.activeDocument.getObject(objects[0].Name)

            if sketch.recompute() == True:
                importDXF.export([sketch], os.path.join(
                    self.tempDirPath, "%s.dxf" % (label)))
                f = open(os.path.join(self.tempDirPath, "%s.dxf" % (label)), "r")
                content = f.read()
                f.close()
                return content
            else:
                return None
        else:
            return None

    def __getSTEPFromFreeCAD(self, surfaceLabel, sketchLabel, productName):
        try:
            sketchObjects = self.activeDocument.getObjectsByLabel(sketchLabel)
            surfaceObjects = self.activeDocument.getObjectsByLabel(
                surfaceLabel)

            if len(sketchObjects) and len(surfaceObjects):
                sketch = self.activeDocument.getObject(sketchObjects[0].Name)
                surface = self.activeDocument.getObject(surfaceObjects[0].Name)

                if sketch.recompute() == True:
                    Import.export([surface], os.path.join(
                        self.tempDirPath, "%s.step" % (surfaceLabel)))
                    f = open(os.path.join(self.tempDirPath,
                             "%s.step" % (surfaceLabel)), "r")
                    content = f.read()
                    f.close()
                    return content.replace(surfaceLabel, productName)
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(str(e))

    def getSTEPs(self):

        self.openDocument()

        # Export the geometry
        stator1 = self.__getSTEPFromFreeCAD(
            "StatorSketch1_Surface", "StatorSketch1", "Stator_Segment")
        stator2 = self.__getSTEPFromFreeCAD(
            "StatorSketch2_Surface", "StatorSketch2", "Stator_Segment")
        spokeClosingBridge = self.__getSTEPFromFreeCAD(
            "SpokeClosingBridge_Surface", "StatorCuttingAreasSketch", "Spoke_Closing_Bridge")
        spokeLeftConnection = self.__getSTEPFromFreeCAD(
            "SpokeLeftConnection_Surface", "StatorCuttingAreasSketch", "Spoke_Left_Connection")
        spokeRightConnection = self.__getSTEPFromFreeCAD(
            "SpokeRightConnection_Surface", "StatorCuttingAreasSketch", "Spoke_Right_Connection")
        terminalLeft = self.__getSTEPFromFreeCAD(
            "TerminalLeftSketch_Surface", "TerminalLeftSketch", "Terminal_Left")
        terminalRight = self.__getSTEPFromFreeCAD(
            "TerminalRightSketch_Surface", "TerminalRightSketch", "Terminal_Right")
        toothLine = self.__getSTEPFromFreeCAD(
            "ToothLine", "ToothLine", "Tooth_Line")
        yokeLine = self.__getSTEPFromFreeCAD(
            "YokeLine", "YokeLine", "Yoke_Line")

        # Close FreeCad document
        self.closeDocument()

        output = {
            "Terminal Left": terminalLeft,
            "Terminal Right": terminalRight,
            "Tooth Line": toothLine,
            "Yoke Line": yokeLine,
            "Spoke Closing Bridge": spokeClosingBridge,
            "Spoke Left Connection": spokeLeftConnection,
            "Spoke Right Connection": spokeRightConnection
        }

        if stator1 != None:
            output["Stator Segment"] = stator1
        else:
            output["Stator Segment"] = stator2

        return output

    def getDXFs(self):

        self.openDocument()

        # Export the geometry
        statorSketch1 = self.__getDXFFromFreeCAD("StatorSketch1")
        statorSketch2 = self.__getDXFFromFreeCAD("StatorSketch2")
        terminalLeft = self.__getDXFFromFreeCAD("TerminalLeftSketch")
        terminalRight = self.__getDXFFromFreeCAD("TerminalRightSketch")
        toothLine = self.__getDXFFromFreeCAD("ToothLine")
        yokeLine = self.__getDXFFromFreeCAD("YokeLine")

        # Close FreeCad document
        self.closeDocument()

        output = {
            "Terminal Left": terminalLeft,
            "Terminal Right": terminalRight,
            "Tooth Line": toothLine,
            "Yoke Line": yokeLine
        }

        if statorSketch1 != None:
            output["Stator Segment"] = statorSketch1
        else:
            output["Stator Segment"] = statorSketch2

        return output

    def setSVG(self):

        self.__addWireLeftIsolationCircles()
        self.__addWireLeftConductorCircles()
        self.__addWireRightIsolationCircles()
        self.__addWireRightConductorCircles()
        self.__addWireSingleIsolationCircles()
        self.__addWireSingleConductorCircles()

        self.__setDependentSpreadsheetParameters()

        facesTopView = [
            {"label": "TerminalLeftSketch", "fill": "yellow",
                "stroke": "yellow", "stroke-width": 1},
            {"label": "TerminalRightSketch", "fill": "yellow",
                "stroke": "yellow", "stroke-width": 1},
        ]

        facesWindingView = [

        ]

        if self.winding.coilSpan == 1:

            facesWindingView.append({"label": "TerminalLeftSketch", "fill": "white",
                                     "stroke": "red", "stroke-width": 1})
            facesWindingView.append({"label": "TerminalRightSketch", "fill": "white",
                                     "stroke": "red", "stroke-width": 1})

            facesWindingView.append({"label": "SlotLeftWindingsIsolation", "fill": "DarkRed",
                                     "stroke": "DarkRed", "stroke-width": 0})
            facesWindingView.append({"label": "SlotLeftWindingsConductor", "fill": "Orange",
                                     "stroke": "DarkRed", "stroke-width": 0})
            facesWindingView.append({"label": "SlotRightWindingsIsolation", "fill": "DarkRed",
                                     "stroke": "DarkRed", "stroke-width": 0})
            facesWindingView.append({"label": "SlotRightWindingsConductor", "fill": "Orange",
                                     "stroke": "DarkRed", "stroke-width": 0})
        else:
            facesWindingView.append({"label": "TerminalSingleSketch", "fill": "white",
                                     "stroke": "red", "stroke-width": 1})
            facesWindingView.append({"label": "SlotSingleWindingsIsolation", "fill": "DarkRed",
                                     "stroke": "DarkRed", "stroke-width": 0})
            facesWindingView.append({"label": "SlotSingleWindingsConductor", "fill": "Orange",
                                     "stroke": "DarkRed", "stroke-width": 0})

        if self.stator.type == 7:
            facesTopView = [{"label": "StatorCuttingAreasSketch",
                             "fill": "#bad0e3", "stroke": "#bad0e3", "stroke-width": 0}] + facesTopView

            facesWindingView = [{"label": "StatorCuttingAreasSketch",
                                 "fill": "#bad0e3", "stroke": "#bad0e3", "stroke-width": 0}] + facesWindingView

        (topViewSVG, isValidTopViewSVG) = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[{
            "label": "StatorSketch1", "fill": "SteelBlue", "stroke": "SteelBlue", "stroke-width": 1}] + facesTopView)

        (windingViewSVG, isValidWindingViewSVG) = self.__getSVGFromFreeCad(fileName="WindingViewStator.svg", faces=[{
            "label": "StatorSketch1", "fill": "SteelBlue", "stroke": "SteelBlue", "stroke-width": 1}] + facesWindingView)

        if isValidTopViewSVG == False:
            (topViewSVG, isValidTopViewSVG) = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[{
                "label": "StatorSketch2", "fill": "SteelBlue", "stroke": "SteelBlue", "stroke-width": 1}] + facesTopView)

            (windingViewSVG, isValidWindingViewSVG) = self.__getSVGFromFreeCad(fileName="WindingViewStator.svg", faces=[{
                "label": "StatorSketch2", "fill": "SteelBlue", "stroke": "SteelBlue", "stroke-width": 1}] + facesWindingView)

        (sideViewSVG, isValidSideViewSVG) = self.__getSVGFromFreeCad(fileName="SideViewStator.svg", faces=[
            {"label": "StatorStack", "fill": "SteelBlue",
                "stroke": "SteelBlue", "stroke-width": 1},
            {"label": "Isolation", "fill": "#f8991d",
                "stroke": "#f8991d", "stroke-width": 1},
        ])

        output = dict()

        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)
        output["Winding View"] = windingViewSVG

        self.svg = output
