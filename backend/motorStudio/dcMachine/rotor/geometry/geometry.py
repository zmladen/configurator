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
import random
import string

# import importDXF

class geometry(object):
    def __init__(self, rotor):
        """Geometry class to control the freecad rotor templates. Supported freecad version 0.18."""

        self.rotor=rotor
        self.activeDocument = None
        self.svg = None
        self.templateName = "rotor1"
        self.tempDirPath = os.path.join(os.getcwd(), "motorStudio", "dcMachine", "rotor", "geometry", "templates", "freecad", "temp")

        self.openDocument()

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(), "motorStudio", "dcMachine", "rotor", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

        self.tempTemplateName = self.templateName + "_" + ''.join(random.sample((string.ascii_uppercase+string.digits),6))
        self.freecadTemplatePath = os.path.join(os.getcwd(), "motorStudio", "dcMachine", "rotor", "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
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

    def getMagnetArea(self):
        try:
            __magnet__ = self.activeDocument.getObject(self.activeDocument.getObjectsByLabel("Magnet_Surface")[0].Name)
            area = __magnet__.Shape.Area
            return area
        except Exception as e:
            self.closeDocument()

    def __setSpreadsheetParameters(self):
        try:
            self.activeDocument.Spreadsheet.set('poleNumber', str(self.rotor.poleNumber))
            self.activeDocument.Spreadsheet.set('innerDiameter', str(self.rotor.innerDiameter))
            self.activeDocument.Spreadsheet.set('stackLength', str(self.rotor.stacklength))
            self.activeDocument.Spreadsheet.set('stackingFactor', str(self.rotor.stackingFactor))
            self.activeDocument.Spreadsheet.set('magnetBackAngle', str(self.rotor.pole.pockets[0].magnet.backAngle))
            self.activeDocument.Spreadsheet.set('magnetEdgeAngle', str(self.rotor.pole.pockets[0].magnet.edgeAngle))
            self.activeDocument.Spreadsheet.set('magnetCutSide', str(self.rotor.pole.pockets[0].magnet.cutSide))
            self.activeDocument.Spreadsheet.set('magnetTopAirgap', str(self.rotor.pole.pockets[0].magnet.topAirgap))
            self.activeDocument.Spreadsheet.set('magnetEdgeAirgap', str(self.rotor.pole.pockets[0].magnet.edgeAirgap))
            self.activeDocument.Spreadsheet.set('magnetOffset', str(self.rotor.pole.pockets[0].magnet.offset))
            self.activeDocument.Spreadsheet.set('magnetLength', str(self.rotor.pole.pockets[0].magnet.length))
            self.activeDocument.Spreadsheet.set('magnetThickness', str(self.rotor.pole.pockets[0].magnet.height))
            self.activeDocument.Spreadsheet.set('magnetEmbrace', str(self.rotor.pole.pockets[0].magnet.embrace))
            if (self.rotor.pole.pockets[0].magnet.frontAngle < 360 / self.rotor.poleNumber * self.rotor.pole.pockets[0].magnet.embrace/100):
                self.activeDocument.Spreadsheet.set('magnetFrontAngle', str(self.rotor.pole.pockets[0].magnet.frontAngle))
            else:
                self.activeDocument.Spreadsheet.set('magnetFrontAngle', str(self.rotor.pole.pockets[0].magnet.frontAngle*0.99))

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

    def __getSTEPFromFreeCAD(self, surfaceLabel, sketchLabel, productName):
        try:
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
        except Exception as e:
            print(str(e))

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        for group in root.findall("g"):
            title=group.find("title")
            if title.text == "b'%s'" %("RotorSegment") or title.text == "b'%s'" %("MagnetSegment"):
                for i in range(1, self.rotor.poleNumber):
                    group_tmp = ElementTree.fromstring(ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" %(i * 360/self.rotor.poleNumber)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" %(rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __getDXFFromFreeCAD(self, label):
        objects = self.activeDocument.getObjectsByLabel(label)

        if len(objects):
            sketch = self.activeDocument.getObject(objects[0].Name)
            importDXF.export([sketch], os.path.join(self.tempDirPath, "%s.dxf" %(label)))
            f = open(os.path.join(self.tempDirPath, "%s.dxf" %(label)), "r")
            content = f.read()
            f.close()
            return content
        else:
            return None

    def getSTEPs(self):
        self.openDocument()

        rotorSegment = self.__getSTEPFromFreeCAD("Rotor_Surface", None, "Rotor_Segment")
        magnetSegment = self.__getSTEPFromFreeCAD("Magnet_Surface", None, "Magnet_Segment")

        # Close FreeCad document
        self.closeDocument()

        return {
         "Magnet Segment":magnetSegment,
         "Rotor Segment": rotorSegment,
        }

    def getDXFs(self):
        pass

    def setSVG(self):
        # Get the svg
        topViewSVG = self.__getSVGFromFreeCad(fileName="TopViewRotor.svg", faces=[
            {"label":"RotorSegment", "fill": "white", "stroke":"black", "stroke-width":0},
            {"label":"MagnetSegment", "fill": "aqua", "stroke":"black", "stroke-width":0},
            {"label":"BoundingBox", "fill": "none", "stroke":"none", "stroke-width":0},
        ])

        sideViewSVG = self.__getSVGFromFreeCad(fileName="TopViewRotor.svg", faces=[
            {"label":"MagnetSide", "fill": "aqua", "stroke":"black", "stroke-width":0},
        ])


        output = dict()
        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)

        self.svg=output
