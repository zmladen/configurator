import os
import shutil
# from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
# from math import pi, cos, sin, sqrt
from utils import point, svg
# import numpy as np
# import FreeCAD
# import importSVG
# import Part
# import Sketcher
# import importDXF


class geometry(object):
    def __init__(self, winding):
        """Geometry class to control the freecad stator templates. Supported freecad version 0.18."""

        self.winding = winding
        self.templateName = "winding3"
        self.tempDirPath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "winding", "geometry", "templates", "freecad", "temp")
        self.freecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "winding", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

    def __setSpreadsheetParameters(self):
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'slotNumber', str(self.winding.stator.slotNumber))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'outerDiameter', str(self.winding.stator.outerDiameter))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'innerDiameter', str(self.winding.stator.innerDiameter))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'stackLength', str(self.winding.stator.stacklength))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'stackingFactor', str(self.winding.stator.stackingFactor))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'cuttingThickness', str(self.winding.stator.cuttingThickness))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'skewAngle', str(self.winding.stator.skewAngle))
        FreeCAD.ActiveDocument.Spreadsheet.set('tipHeightReduction', str(
            self.winding.stator.sector.slot.tipHeightReduction))
        FreeCAD.ActiveDocument.Spreadsheet.set('toothThickness', str(
            self.winding.stator.sector.slot.toothThickness))
        FreeCAD.ActiveDocument.Spreadsheet.set('yokeThickness', str(
            self.winding.stator.sector.slot.yokeThickness))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'tipHeight', str(self.winding.stator.sector.slot.tipHeight))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'tipAngle', str(self.winding.stator.sector.slot.tipAngle))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'openingLeft', str(self.winding.stator.sector.slot.openingLeft))
        FreeCAD.ActiveDocument.Spreadsheet.set('openingRight', str(
            self.winding.stator.sector.slot.openingRight))
        FreeCAD.ActiveDocument.Spreadsheet.set('roundingRadii', str(
            self.winding.stator.sector.slot.roundingRadius))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'slotIsolation', str(self.winding.slotIsolation))
        FreeCAD.ActiveDocument.Spreadsheet.set(
            'coilAxialHeight', str(self.winding.coil.axialHeight))
        FreeCAD.ActiveDocument.recompute()

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
                __objs__.append(FreeCAD.ActiveDocument.getObject(
                    FreeCAD.ActiveDocument.getObjectsByLabel(face["label"])[0].Name))

            # Export SVG to file
            importSVG.export(__objs__, os.path.join(
                self.tempDirPath, fileName))
            del __objs__

            # Read and modify attributes
            return svg.modifySVGAttributes(fileName=fileName, tempDirPath=self.tempDirPath, faces=faces)

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        connectionTable = self.winding.layout.getConnectionTable()["table"]
        # {'Coil Number': 0, 'coil': 'A', 'branch': 'A', 'angle': 0.0, 'inSlot': 1, 'outSlot': 6, 'inPosition': 4, 'outPosition': 3}
        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("Terminal"):
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

            if title.text == "b'%s'" % ("TerminalLeft"):
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

            if title.text == "b'%s'" % ("TerminalRight"):
                for row in connectionTable:
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (
                        row['outSlot'] * 360/self.winding.stator.slotNumber)
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

            transform = group.get("transform")
            transform += " rotate(%s)" % (rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def getTerminalCoordinates(self):
        # Open Template
        FreeCAD.open(self.freecadTemplatePath)
        FreeCAD.setActiveDocument(self.templateName)
        FreeCAD.ActiveDocument = FreeCAD.getDocument(self.templateName)

        # Set the input parameters
        self.__setSpreadsheetParameters()

        __object__ = FreeCAD.ActiveDocument.getObject(
            FreeCAD.ActiveDocument.getObjectsByLabel("Terminal")[0].Name)

        coord = []
        for v in __object__.Shape.Vertexes:
            coord.append(point(v.X, v.Y).rotateCopy(
                90-self.winding.stator.segmentAngle/2))

        # Close FreeCad document
        FreeCAD.closeDocument(self.templateName)

        # [p0, p1, p2, p3, p4, p5]
        return coord

    def __addWireIsolationCircles(self):
        FreeCAD.ActiveDocument.Body.newObject(
            'Sketcher::SketchObject', 'SlotWindingsIsolation')
        FreeCAD.ActiveDocument.SlotWindingsIsolation.Support = (
            FreeCAD.ActiveDocument.XY_Plane, [''])
        FreeCAD.ActiveDocument.SlotWindingsIsolation.MapMode = 'FlatFace'
        FreeCAD.ActiveDocument.recompute()

        coordinates = self.winding.coil.getWireCoordinates(
            terminalCoordinates=self.winding.terminalCoordinates)[0]

        for p in coordinates:
            FreeCAD.ActiveDocument.SlotWindingsIsolation.addGeometry(Part.Circle(FreeCAD.Vector(p.X, p.Y, 0), FreeCAD.Vector(
                0, 0, 1), self.winding.coil.wire.gauge[self.winding.coil.wire.isolationGrade]/2), False)
            FreeCAD.ActiveDocument.recompute()

    def __addWireConductorCircles(self):
        FreeCAD.ActiveDocument.Body.newObject(
            'Sketcher::SketchObject', 'SlotWindingsConductor')
        FreeCAD.ActiveDocument.SlotWindingsConductor.Support = (
            FreeCAD.ActiveDocument.XY_Plane, [''])
        FreeCAD.ActiveDocument.SlotWindingsConductor.MapMode = 'FlatFace'
        FreeCAD.ActiveDocument.recompute()

        wireCoordinates = self.winding.coil.getWireCoordinates(
            terminalCoordinates=self.winding.terminalCoordinates)[0]

        for p in wireCoordinates:
            FreeCAD.ActiveDocument.SlotWindingsConductor.addGeometry(Part.Circle(FreeCAD.Vector(
                p.X, p.Y, 0), FreeCAD.Vector(0, 0, 1), self.winding.coil.wire.gauge["Conductor Diameter (mm)"]/2), False)
            FreeCAD.ActiveDocument.recompute()

    def getDXF(self):
        # Open Template
        FreeCAD.open(self.freecadTemplatePath)
        FreeCAD.setActiveDocument(self.templateName)
        FreeCAD.ActiveDocument = FreeCAD.getDocument(self.templateName)
        # Create the temporary folder
        self.__createTempFolder()
        # Set the input parameters
        self.__setSpreadsheetParameters()
        # Export the geometry
        importDXF.export([FreeCAD.ActiveDocument.getObject(FreeCAD.ActiveDocument.getObjectsByLabel("Stator")[0].Name)],
                         os.path.join(self.tempDirPath, "stator.dxf"))
        # Close FreeCad document
        FreeCAD.closeDocument(self.templateName)

        f = open(os.path.join(self.tempDirPath, "stator.dxf"), "r")
        text = f.read()
        f.close()
        # Delete the folder and files
        # self.__deleteTempFolder()

        return text

    def getSVG(self):
        # Open Template
        FreeCAD.open(self.freecadTemplatePath)
        FreeCAD.setActiveDocument(self.templateName)
        FreeCAD.ActiveDocument = FreeCAD.getDocument(self.templateName)

        # Create the temporary folder
        self.__createTempFolder()
        # Set the input parameters
        self.__setSpreadsheetParameters()

        # Aad the wire coordinates
        self.__addWireIsolationCircles()
        self.__addWireConductorCircles()

        # Get the svg
        topViewSVG = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[
            {"label": "Terminal", "fill": "Orange",
                "stroke": "Orange", "stroke-width": 0},
            # {"label":"TerminalRight", "fill": "#ffb732", "stroke": "#ffb732", "stroke-width": 0},
        ])
        sideViewSVG = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[
            {"label": "WindingSide", "fill": "Orange",
                "stroke": "Orange", "stroke-width": 0},
        ])
        windingViewSVG = self.__getSVGFromFreeCad(fileName="TopViewStator.svg", faces=[
            {"label": "StatorSegment", "fill": "SteelBlue",
                "stroke": "SteelBlue", "stroke-width": 1},
            {"label": "Terminal", "fill": "None",
                "stroke": "red", "stroke-width": 1},
            {"label": "SlotWindingsIsolation", "fill": "DarkRed",
                "stroke": "DarkRed", "stroke-width": 0},
            {"label": "SlotWindingsConductor", "fill": "Orange",
                "stroke": "Orange", "stroke-width": 0},
        ])

        FreeCAD.ActiveDocument.saveAs(
            os.path.join(self.tempDirPath, "tmp.FCStd"))

        # Close FreeCad document
        FreeCAD.closeDocument(self.templateName)
        # Delete the folder and files
        # self.__deleteTempFolder()

        output = dict()
        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)
        output["Winding View"] = windingViewSVG

        return output
