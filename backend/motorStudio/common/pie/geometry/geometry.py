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
    def __init__(self, pie, partName="Shaft"):
        """Geometry class to control the freecad pie templates. Supported freecad version 0.18."""

        self.pie=pie
        self.templateName = "pie1"
        self.tempDirPath = os.path.join(os.getcwd(), "motorStudio", "common", "pie", "geometry", "templates", "freecad", "temp")
        self.partName=partName
        self.activeDocument = None
        self.svg = None

        self.openDocument()

    def __setSpreadsheetParameters(self):
        try:
            self.activeDocument.Spreadsheet.set('outerDiameter', str(self.pie.outerDiameter))
            self.activeDocument.Spreadsheet.set('segmentNumber', str(self.pie.segmentNumber))
            self.activeDocument.Spreadsheet.set('length', str(self.pie.length))
            self.activeDocument.recompute()
        except Exception as e:
            print(str(e))
            self.closeDocument()

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(), "motorStudio", "common", "pie", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))
        self.tempTemplateName = self.templateName + "_" + ''.join(random.sample((string.ascii_uppercase+string.digits),6))
        self.freecadTemplatePath = os.path.join(os.getcwd(), "motorStudio", "common", "pie", "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
        shutil.copy(orginalFreecadTemplatePath, self.freecadTemplatePath)


        if self.activeDocument == None:
            FreeCAD.open(self.freecadTemplatePath)
            FreeCAD.setActiveDocument(self.tempTemplateName)
            self.activeDocument = FreeCAD.getDocument(self.tempTemplateName)
            self.__setSpreadsheetParameters()

    def closeDocument(self):
        FreeCAD.closeDocument(self.tempTemplateName)
        self.__deleteTempFolder()
        self.activeDocument = None

    def __deleteTempFolder(self):
        try:
            shutil.rmtree(self.tempDirPath, ignore_errors=True)
        except OSError as e:
            print("Error: %s : %s" % (self.tempDirPath, e.strerror))

    def __createTempFolder(self):
        os.makedirs(self.tempDirPath, exist_ok=True)

    def __getSVGFromFreeCad(self, fileName=None, faces=[]):
        try:
            if fileName==None:
                print("Please define the name of the SVG file.")
                return ""
            else:
                __objs__ = []
                for face in faces:
                    __objs__.append(self.activeDocument.getObject(self.activeDocument.getObjectsByLabel(face["label"])[0].Name))

                # Export SVG to file
                importSVG.export(__objs__, os.path.join(self.tempDirPath, fileName))
                del __objs__

                # Read and modify attributes
                return svg.modifySVGAttributes(fileName=fileName, tempDirPath=self.tempDirPath, faces=faces)
        except Exception as e:
            print(str(e))
            self.closeDocument()

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        for group in root.findall("g"):
            title=group.find("title")
            if title.text == "b'%s'" %("PieSketch"):
                for i in range(1, self.pie.segmentNumber):
                    group_tmp = ElementTree.fromstring(ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" %(i * 360/self.pie.segmentNumber)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" %(rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __getSTEPFromFreeCAD(self, surfaceLabel, sketchLabel, productName):
        sketchObjects = self.activeDocument.getObjectsByLabel(sketchLabel)
        surfaceObjects = self.activeDocument.getObjectsByLabel(surfaceLabel)

        if len(sketchObjects) and len(surfaceObjects):
            sketch = self.activeDocument.getObject(sketchObjects[0].Name)
            surface = self.activeDocument.getObject(surfaceObjects[0].Name)

            if sketch.recompute() == True:
                Import.export([surface],os.path.join(self.tempDirPath, "%s.step" %(surfaceLabel)))
                f = open(os.path.join(self.tempDirPath, "%s.step" %(surfaceLabel)), "r")
                content = f.read()
                f.close()
                return content.replace(surfaceLabel, productName)
            else:
                return None
        else:
            return None

    def getSTEPs(self):

        self.openDocument()

        ring = self.__getSTEPFromFreeCAD("PieSketch_Surface", "PieSketch", "%s_Segment" %(self.partName))

        # Close FreeCad document
        self.closeDocument()

        return {
         "%s Segment" %(self.partName):ring
        }

    def getDXFs(self):

        self.openDocument()
        # Export the geometry
        importDXF.export([self.activeDocument.getObject(self.activeDocument.getObjectsByLabel("PieSketch")[0].Name)],
                            os.path.join(self.tempDirPath, "%s.dxf" %(self.partName)))

        f = open(os.path.join(self.tempDirPath, "%s.dxf" %(self.partName)), "r")
        text = f.read()
        f.close()

        self.closeDocument()

        return {
         "%s Segment" %(self.partName):text
        }

    def setSVG(self):
        # Get the svg
        topViewSVG = self.__getSVGFromFreeCad(fileName="TopView%s.svg" %(self.partName), faces=[
            {"label":"PieSketch", "fill": "LightSeaGreen", "stroke":"LightSeaGreen", "stroke-width":1}
        ])
        sideViewSVG = self.__getSVGFromFreeCad(fileName="TopView%s.svg" %(self.partName), faces=[
            {"label":"PieSide", "fill": "LightSeaGreen", "stroke":"LightSeaGreen", "stroke-width":1}
        ])

        output = dict()
        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)

        self.svg=output
