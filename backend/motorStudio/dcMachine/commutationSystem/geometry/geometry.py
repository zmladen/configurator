import os
import shutil
from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
from math import pi, cos, sin, sqrt
from utils import spiral, circle, point, svg, functions
import numpy as np
import FreeCAD
import importSVG
import Part
import Sketcher
import random
import string


class geometry(object):
    def __init__(self, commutationSystem):
        """Geometry class to control the freecad commutationSystem templates. Supported freecad version 0.18."""

        self.commutationSystem = commutationSystem
        self.templateName = "commutationSystem1"
        self.activeDocument = None
        self.svg = None
        self.tempDirPath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "commutationSystem", "geometry", "templates", "freecad", "temp")

        self.openDocument()

    def __setSpreadsheetParameters(self):
        self.activeDocument.Spreadsheet.set('segmentNumber', str(
            self.commutationSystem.commutator.numberOfSegments))
        self.activeDocument.Spreadsheet.set('outerDiameter', str(
            self.commutationSystem.commutator.outerDiameter))
        self.activeDocument.Spreadsheet.set('innerDiameter', str(
            self.commutationSystem.commutator.innerDiameter))
        self.activeDocument.Spreadsheet.set(
            'length', str(self.commutationSystem.commutator.length))

        self.activeDocument.Spreadsheet.set('brushWidth', str(
            self.commutationSystem.commutator.brushes.width))
        self.activeDocument.Spreadsheet.set('brushHeight', str(
            self.commutationSystem.commutator.brushes.height))
        self.activeDocument.Spreadsheet.set('brushLength', str(
            self.commutationSystem.commutator.brushes.length))
        self.activeDocument.Spreadsheet.set('commutatorDisplacementAngle', str(
            self.commutationSystem.commutator.displacementAngle))
        self.activeDocument.Spreadsheet.set('commutatorIsolationThickness', str(
            self.commutationSystem.commutator.isolationThickness))

        self.activeDocument.Spreadsheet.set('stackDistance', str(
            self.commutationSystem.commutator.stackDistance))
        self.activeDocument.Spreadsheet.set('statorStackLength', str(
            self.commutationSystem.commutator.winding.stator.stacklength))
        self.activeDocument.recompute()

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "dcMachine", "commutationSystem", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

        self.tempTemplateName = self.templateName + "_" + \
            ''.join(random.sample((string.ascii_uppercase+string.digits), 6))
        self.freecadTemplatePath = os.path.join(os.getcwd(), "motorStudio", "dcMachine", "commutationSystem",
                                                "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
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
        FreeCAD.closeDocument(self.tempTemplateName)
        self.__deleteTempFolder()
        self.activeDocument = None

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

    def __modifySVG(self, freeCadSVG="", addCommutatorNumbers=False, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("CommutatorSegment"):
                for i in range(self.commutationSystem.commutator.numberOfSegments):
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i * 360 /
                                                      self.commutationSystem.commutator.numberOfSegments)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)
                root.remove(group)

            if title.text == "b'%s'" % ("BrushTop"):
                for i in range(1, self.commutationSystem.commutator.numberOfBrushes):
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i * 360 /
                                                      self.commutationSystem.commutator.numberOfBrushes)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" % (rotateView)
            group.set("transform", transform)

        if addCommutatorNumbers:
            # Ad commutator nunmbers
            centroid = self.__getCommutatiorSegmentCentroid()
            c = point(centroid[0], centroid[1])
            for i in range(self.commutationSystem.commutator.numberOfSegments):
                segmentAngle = 360/self.commutationSystem.commutator.numberOfSegments
                text = ElementTree.Element("text")
                text.text = str(i+1)
                p = c.rotateCopy(
                    i * 360/self.commutationSystem.commutator.numberOfSegments)
                text.set("x", str(p.X))
                text.set("y", str(-p.Y))
                text.set("transform", "")
                text.set("text-anchor", "middle")
                text.set("alignment-baseline", "central")
                text.set("font-size", "3px")
                text.set("style", "fill:white")
                root.append(text)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __getCommutatiorSegmentCentroid(self):

        __object__ = self.activeDocument.getObject(
            self.activeDocument.getObjectsByLabel("CommutatorSegment")[0].Name)

        coord = []
        for v in __object__.Shape.Vertexes:
            coord.append((v.X, v.Y, v.Z))

        return functions.getCentroidOfList(coord)

    def setSVG(self):

        # Get the svg
        topViewSVG = svg.getSVGFromFreeCad(FreeCAD=FreeCAD, importSVG=importSVG, fileName="TopViewStator.svg", tempDirPath=self.tempDirPath, faces=[
            {"label": "BrushTop", "fill": "Silver", "stroke": "Silver",
                "fill-opacity": 1, "stroke-width": 0},
            {"label": "CommutatorSegment", "fill": "Fuchsia",
                "stroke": "white", "stroke-width": 0},
        ])
        sideViewSVG = svg.getSVGFromFreeCad(FreeCAD=FreeCAD, importSVG=importSVG, fileName="TopViewStator.svg", tempDirPath=self.tempDirPath, faces=[
            {"label": "CommutatorSide", "fill": "Fuchsia",
                "stroke": "Fuchsia", "stroke-width": 0},
            {"label": "BrushesSide", "fill": "Silver",
                "stroke": "Silver", "stroke-width": 0},
        ])

        output = dict()
        output["Top View"] = self.__modifySVG(
            topViewSVG, addCommutatorNumbers=True)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)
        self.svg = output
