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
import Import
import Sketcher
import random
import string


class geometry(object):
    def __init__(self, stator, winding):
        """Geometry class to control the freecad stator templates. Supported freecad version 0.18."""

        self.stator = stator
        self.winding = winding
        self.templateName = "stator1_new"
        self.activeDocument = None
        self.svg = None
        self.tempDirPath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "stator", "geometry", "templates", "freecad", "temp")

        self.openDocument()

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "stator", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

        self.tempTemplateName = self.templateName + "_" + \
            ''.join(random.sample((string.ascii_uppercase+string.digits), 6))
        self.freecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "stator", "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
        shutil.copy(orginalFreecadTemplatePath, self.freecadTemplatePath)

        # print("############################################################")
        # print("Stator Type:", self.stator.type)
        # print("############################################################")

        # if self.activeDocument == None:
        FreeCAD.open(self.freecadTemplatePath)
        FreeCAD.setActiveDocument(self.tempTemplateName)
        self.activeDocument = FreeCAD.getDocument(self.tempTemplateName)
        self.__setSpreadsheetParameters()

    def closeDocument(self):
        FreeCAD.closeDocument(self.tempTemplateName)
        self.__deleteTempFolder()
        self.activeDocument = None

    def saveTemp(self):
        self.activeDocument.saveAs(os.path.join(
            self.tempDirPath, "tmpStator.FCStd"))

    def __setSpreadsheetParameters(self):
        try:
            self.activeDocument.Spreadsheet.set(
                'slotNumber', str(self.stator.slotNumber))
            self.activeDocument.Spreadsheet.set(
                'outerDiameter', str(self.stator.outerDiameter))
            self.activeDocument.Spreadsheet.set(
                'innerDiameter', str(self.stator.innerDiameter))
            self.activeDocument.Spreadsheet.set(
                'stackLength', str(self.stator.stacklength))
            self.activeDocument.Spreadsheet.set(
                'stackingFactor', str(self.stator.stackingFactor))
            self.activeDocument.Spreadsheet.set(
                'cuttingThickness', str(self.stator.cuttingThickness))
            self.activeDocument.Spreadsheet.set(
                'skewAngle', str(self.stator.skewAngle))
            # self.activeDocument.Spreadsheet.set('segmentAngle', str(self.stator.segmentAngle))
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
                'roundingRadii', str(self.stator.sector.slot.roundingRadius))
            self.activeDocument.recompute()

        except Exception as e:
            print(str(e))
            self.closeDocument()

    def __deleteTempFolder(self):
        try:
            shutil.rmtree(self.tempDirPath, ignore_errors=True)
        except OSError as e:
            print("Error: %s : %s" % (self.tempDirPath, e.strerror))

    def __createTempFolder(self):
        os.makedirs(self.tempDirPath, exist_ok=True)

    def __getSVGFromFreeCad(self, fileName=None, faces=[]):

        if fileName == None:
            print("Please define the name of the SVG file.")
            return ""
        else:
            __objs__ = []
            for face in faces:
                __objs__.append(self.activeDocument.getObject(
                    self.activeDocument.getObjectsByLabel(face["label"])[0].Name))

            # Export SVG to file
            importSVG.export(__objs__, os.path.join(
                self.tempDirPath, fileName))
            del __objs__

            # Read and modify attributes
            return svg.modifySVGAttributes(fileName=fileName, tempDirPath=self.tempDirPath, faces=faces)

    def __modifyWindingSVG(self, freeCadSVG):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        for group in root.findall("g"):
            title = group.find("title")
            # print(title.text)
            if title.text == "b'%s'" % ("SlotWindingsConductor"):
                group_tmp = ElementTree.fromstring(ElementTree.tostring(group))

                for index, circle in enumerate(group_tmp.findall("circle")):
                    # print(index, self.winding.coil.usedWindingNumber)

                    if self.winding.coil.numberOfMultipleWires == 1:
                        if index < self.winding.coil.usedWindingNumber:
                            circle.set("style", circle.get("style") +
                                       ";fill:Orange" + ";stroke:Orange")
                        else:
                            circle.set("style", circle.get("style") +
                                       ";fill:#00ffa5" + ";stroke:#00ffa5")
                    else:
                        if index < self.winding.coil.usedWindingNumber * self.winding.coil.numberOfMultipleWires:
                            if index % 2 == 1:
                                circle.set("style", circle.get(
                                    "style") + ";fill:#ffd27f" + ";stroke:#ffd27f")
                            else:
                                circle.set("style", circle.get(
                                    "style") + ";fill:Orange" + ";stroke:Orange")
                        else:
                            if index % 2 == 1:
                                circle.set("style", circle.get(
                                    "style") + ";fill:#7fffd2" + ";stroke:#7fffd2")
                            else:
                                circle.set("style", circle.get(
                                    "style") + ";fill:#00ffa5" + ";stroke:#00ffa5")

                root.append(group_tmp)
                root.remove(group)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        connectionTable = self.winding.layout.getConnectionTable()["table"]
        # {'Coil Number': 0, 'coil': 'A', 'branch': 'A', 'angle': 0.0, 'inSlot': 1, 'outSlot': 6, 'inPosition': 4, 'outPosition': 3}
        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("TerminalSketch"):
                for row in connectionTable:
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (
                        row['inSlot'] * 360/self.winding.stator.slotNumber)
                    group_tmp.set("transform", transform_tmp)

                    for path in group_tmp.findall("path"):
                        # Only change color
                        if row["branch"] == "A":
                            path.set("style", path.get("style") +
                                     ";fill:Orange" + ";stroke:Orange")
                        else:
                            path.set("style", path.get("style") +
                                     ";fill:#ffb732" + ";stroke:#ffb732")
                    root.append(group_tmp)

                root.remove(group)

        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("StatorSketch"):
                for i in range(1, self.stator.slotNumber):
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i *
                                                      360/self.stator.slotNumber)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" % (rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def getSlotArea(self):
        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("SlotSketch_Surface")[0].Name)
            area = __object__.Shape.Area

            return area
        except Exception as e:
            print(str(e))

    def getSlotCoordinates(self):

        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("SlotSketch")[0].Name)

            coord = []
            for v in __object__.Shape.Vertexes:
                coord.append(point(v.X, v.Y).rotateCopy(
                    90-self.stator.segmentAngle/2))

            return coord
        except Exception as e:
            print(str(e))

    def getTerminalCoordinates(self):

        try:
            __object__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("TerminalSketch")[0].Name)
            coord = []
            for v in __object__.Shape.Vertexes:
                coord.append(point(v.X, v.Y).rotateCopy(
                    90-self.stator.segmentAngle/2))

            return coord
        except Exception as e:
            print(str(e))

    def __addWireIsolationCircles(self):

        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotWindingsIsolation')
            self.activeDocument.SlotWindingsIsolation.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotWindingsIsolation.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireCoordinates:
                self.activeDocument.SlotWindingsIsolation.addGeometry(Part.Circle(FreeCAD.Vector(p["x"], p["y"], 0), FreeCAD.Vector(
                    0, 0, 1), self.winding.coil.wire.gauge[self.winding.coil.wire.isolationGrade]/2.0), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def __addWireConductorCircles(self):

        try:
            self.activeDocument.Body.newObject(
                'Sketcher::SketchObject', 'SlotWindingsConductor')
            self.activeDocument.SlotWindingsConductor.Support = (
                self.activeDocument.XY_Plane, [''])
            self.activeDocument.SlotWindingsConductor.MapMode = 'FlatFace'
            # self.activeDocument.recompute()

            for p in self.winding.coil.wireCoordinates:
                self.activeDocument.SlotWindingsConductor.addGeometry(Part.Circle(FreeCAD.Vector(
                    p["x"], p["y"], 0), FreeCAD.Vector(0, 0, 1), self.winding.coil.wire.gauge["Conductor Diameter (mm)"]/2.0), False)
                # self.activeDocument.recompute()
        except Exception as e:
            print(str(e))

    def getDXFs(self):
        pass

    def getSTEPs(self):

        self.openDocument()

        # Export the geometry
        stator = self.__getSTEPFromFreeCAD(
            "StatorSketch_Surface", "StatorSketch", "Stator_Segment")
        terminal = self.__getSTEPFromFreeCAD(
            "TerminalSketch_Surface", "TerminalSketch", "Terminal")
        toothLine = self.__getSTEPFromFreeCAD(
            "ToothLine", "ToothLine", "Tooth_Line")
        yokeLine = self.__getSTEPFromFreeCAD(
            "YokeLine", "YokeLine", "Yoke_Line")

        # Close FreeCad document
        self.closeDocument()

        output = {
            "Stator Segment": stator,
            "Terminal": terminal,
            "Tooth Line": toothLine,
            "Yoke Line": yokeLine
        }

        return output

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

    def setSVG(self):

        self.__addWireIsolationCircles()
        self.__addWireConductorCircles()

        # Get svg
        (topViewSVG, isValidTopViewSVG) = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[
            {"label": "StatorSketch", "fill": "SteelBlue",
                "stroke": "SteelBlue", "stroke-width": 1},
            {"label": "TerminalSketch", "fill": "None",
                "stroke": "red", "stroke-width": 1},
        ])
        (sideViewSVG, isValidSideViewSVG) = self.__getSVGFromFreeCad(fileName="sideViewSVG.svg", faces=[
            {"label": "StatorSide", "fill": "SteelBlue",
                "stroke": "SteelBlue", "stroke-width": 1},
            {"label": "WindingSide", "fill": "Orange",
                "stroke": "Orange", "stroke-width": 0},
        ])

        (windingViewSVG, isValidWindingViewSVG) = self.__getSVGFromFreeCad(fileName="windingViewSVG.svg", faces=[
            {"label": "StatorSketch", "fill": "SteelBlue",
                "stroke": "SteelBlue", "stroke-width": 1},
            {"label": "TerminalSketch", "fill": "None",
                "stroke": "red", "stroke-width": 1},
            {"label": "SlotWindingsIsolation", "fill": "DarkRed",
                "stroke": "DarkRed", "stroke-width": 0},
            {"label": "SlotWindingsConductor", "fill": "Orange",
                "stroke": "Orange", "stroke-width": 0},
        ])

        output = dict()
        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)
        output["Winding View"] = self.__modifyWindingSVG(windingViewSVG)

        self.svg = output
