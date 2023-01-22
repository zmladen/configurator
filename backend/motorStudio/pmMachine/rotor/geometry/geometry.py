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
    def __init__(self, rotor):
        """Geometry class to control the freecad rotor templates. Supported freecad version 0.18."""

        self.rotor = rotor
        self.activeDocument = None
        self.svg = None
        self.tempDirPath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "rotor", "geometry", "templates", "freecad", "temp")

        if (self.rotor.type == 1):
            # t-rotor
            self.templateName = "rotor1"
        elif (self.rotor.type == 3):
            # i-rotor
            self.templateName = "rotor2"
        elif (self.rotor.type == 4):
            # s-rotor round back
            self.templateName = "rotor3"
        elif (self.rotor.type == 5):
            # b-rotor
            self.templateName = "rotor5"
        elif (self.rotor.type == 7):
            # outer-runner with block magnet and straight back rotor
            self.templateName = "RotorORBlockMagnetStraightBack"
        elif (self.rotor.type == 8):
            # outer-runner with pocket magnet
            self.templateName = "RotorORBlockPocket"
        elif (self.rotor.type == 9):
            # r-rotor (ringmagnet)
            self.templateName = "RotorIRRingMagnet"
        elif (self.rotor.type == 10):
            # outer-runner with block magnet and straight back rotor
            self.templateName = "RotorORBlockMagnetRoundBack"
        elif (self.rotor.type == 11):
            # outer-runner with block magnet and straight back rotor
            self.templateName = "tRotorClampingPoleShoe"
        elif (self.rotor.type == 12):
            # v-rotor with two magnets
            self.templateName = "vrotor"
        else:
            self.templateName = "rotor1"

        self.openDocument()

    def saveTemp(self):
        self.activeDocument.saveAs(os.path.join(self.tempDirPath, "tmp.FCStd"))

    def openDocument(self):
        # Create the temp folder
        self.__createTempFolder()

        orginalFreecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "rotor", "geometry", "templates", "freecad", "%s.FCStd" % (self.templateName))

        self.tempTemplateName = self.templateName + "_" + \
            ''.join(random.sample((string.ascii_uppercase+string.digits), 6))
        self.freecadTemplatePath = os.path.join(os.getcwd(
        ), "motorStudio", "pmMachine", "rotor", "geometry", "templates", "freecad", "temp", "%s.FCStd" % (self.tempTemplateName))
        shutil.copy(orginalFreecadTemplatePath, self.freecadTemplatePath)

        # print("############################################################")
        # print("Rotor Type:", self.rotor.type, self.activeDocument, self.templateName)
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

    def __setSpreadsheetParameters(self):
        try:
            epsilon = 1e-3
            self.activeDocument.Spreadsheet.set(
                'poleNumber', str(self.rotor.poleNumber))
            self.activeDocument.Spreadsheet.set(
                'outerDiameter', str(self.rotor.outerDiameter))
            self.activeDocument.Spreadsheet.set(
                'innerDiameter', str(self.rotor.innerDiameter))
            self.activeDocument.Spreadsheet.set(
                'stackLength', str(self.rotor.stacklength))
            self.activeDocument.Spreadsheet.set(
                'stackingFactor', str(self.rotor.stackingFactor))
            self.activeDocument.Spreadsheet.set(
                'embrace', str(self.rotor.pole.pockets[0].embrace))
            self.activeDocument.Spreadsheet.set(
                'bridgeCurved', str(self.rotor.pole.pockets[0].bridgeCurved))
            self.activeDocument.Spreadsheet.set(
                'contourRatio', str(self.rotor.pole.contourRatio))
            self.activeDocument.Spreadsheet.set(
                'rib', str(self.rotor.pole.pockets[0].rib))
            self.activeDocument.Spreadsheet.set(
                'ribShaft', str(self.rotor.pole.pockets[0].ribShaft))
            self.activeDocument.Spreadsheet.set(
                'bridgeCurved', str(self.rotor.pole.pockets[0].bridgeCurved))
            self.activeDocument.Spreadsheet.set(
                'magnetWidth', str(self.rotor.pole.pockets[0].magnet.width))
            self.activeDocument.Spreadsheet.set(
                'magnetHeight', str(self.rotor.pole.pockets[0].magnet.height))
            self.activeDocument.Spreadsheet.set('magnetEmbrace', str(
                self.rotor.pole.pockets[0].magnet.embrace))
            self.activeDocument.Spreadsheet.set('magnetContourRatio', str(
                self.rotor.pole.pockets[0].magnet.contourRatio))
            self.activeDocument.Spreadsheet.set(
                'axialMisalignment', str(self.rotor.axialMisalignment))

            if self.rotor.pole.poleSeparation < epsilon:
                self.activeDocument.Spreadsheet.set(
                    'poleSeparation', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'poleSeparation', str(self.rotor.pole.poleSeparation))

            if self.rotor.pole.pockets[0].magnet.airgap < epsilon:
                self.activeDocument.Spreadsheet.set(
                    'magnetAirgap', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'magnetAirgap', str(self.rotor.pole.pockets[0].magnet.airgap))

            if self.rotor.pole.pockets[0].cutTop < epsilon:
                self.activeDocument.Spreadsheet.set('cutTop', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'cutTop', str(self.rotor.pole.pockets[0].cutTop))

            if self.rotor.pole.pockets[0].cutBottom < epsilon:
                self.activeDocument.Spreadsheet.set('cutBottom', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'cutBottom', str(self.rotor.pole.pockets[0].cutBottom))

            if self.rotor.pole.pockets[0].cut < epsilon:
                self.activeDocument.Spreadsheet.set('cut', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'cut', str(self.rotor.pole.pockets[0].cut))

            if self.rotor.pole.pockets[0].moveInwards < epsilon:
                self.activeDocument.Spreadsheet.set(
                    'movePocketInwards', str(epsilon))
            else:
                self.activeDocument.Spreadsheet.set(
                    'movePocketInwards', str(self.rotor.pole.pockets[0].moveInwards))

            if self.rotor.type == 8 or self.rotor.type == 11 or self.rotor.type == 12:
                self.activeDocument.Spreadsheet.set(
                    'magnetContactRatio', str(self.rotor.pole.pockets[0].magnetContactRatio))

            if self.rotor.type == 12:
                self.activeDocument.Spreadsheet.set(
                    'magnetAngle', str(self.rotor.pole.pockets[0].magnetAngle))

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
        try:
            if fileName == None:
                print("Please define the name of the SVG file.")
                return ""
            else:
                __objs__ = []
                for face in faces:
                    objects = self.activeDocument.getObjectsByLabel(
                        face["label"])
                    if len(objects):
                        __objs__.append(
                            self.activeDocument.getObject(objects[0].Name))

                # Export SVG to file
                importSVG.export(__objs__, os.path.join(
                    self.tempDirPath, fileName))
                del __objs__

                # Read and modify attributes
                return svg.modifySVGAttributes(fileName=fileName, tempDirPath=self.tempDirPath, faces=faces)
        except Exception as e:
            self.closeDocument()

    def getRotorArea(self):
        # "Rotor_Surface" has to exists as it is used to caclulate the surface of all manget material
        try:
            __rotor__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("Rotor_Surface")[0].Name)
            area = __rotor__.Shape.Area
            return area * self.rotor.poleNumber
        except Exception as e:
            self.closeDocument()

    def getMagnetArea(self):
        try:
            __magnet__ = self.activeDocument.getObject(
                self.activeDocument.getObjectsByLabel("Magnet_Surface")[0].Name)
            area = __magnet__.Shape.Area
            return area
        except Exception as e:
            self.closeDocument()

    def __modifySVG(self, freeCadSVG, rotateView=0):
        xml = ElementTree.ElementTree(ElementTree.fromstring(freeCadSVG))
        root = xml.getroot()
        svg.stripNs(root)

        for group in root.findall("g"):
            title = group.find("title")
            if title.text == "b'%s'" % ("RotorPoleSketch") or title.text == "b'%s'" % ("MagnetSketch") or title.text == "b'%s'" % ("MagnetSketch1") or title.text == "b'%s'" % ("MagnetSketch2") or title.text == "b'%s'" % ("PocketSketch") or title.text == "b'%s'" % ("RotorSketch"):
                for i in range(1, self.rotor.poleNumber):
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i *
                                                      360/self.rotor.poleNumber)
                    group_tmp.set("transform", transform_tmp)
                    root.append(group_tmp)

            transform = group.get("transform")
            transform += " rotate(%s)" % (rotateView)
            group.set("transform", transform)

        return ElementTree.tostring(root, encoding='utf8', method='xml').decode("utf-8")

    def __getSTEPFromFreeCAD(self, surfaceLabel, sketchLabel, productName):
        if sketchLabel != None:
            # Sketch only to ckeck if the surface object is ok
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
        else:
            surfaceObjects = self.activeDocument.getObjectsByLabel(
                surfaceLabel)

            if len(surfaceObjects):
                surface = self.activeDocument.getObject(surfaceObjects[0].Name)

                Import.export([surface], os.path.join(
                    self.tempDirPath, "%s.step" % (surfaceLabel)))
                f = open(os.path.join(self.tempDirPath, "%s.step" %
                         (surfaceLabel)), "r")
                content = f.read()
                f.close()

                return content.replace(surfaceLabel, productName)
            else:
                return None

    def __getDXFFromFreeCAD(self, label):
        objects = self.activeDocument.getObjectsByLabel(label)

        if len(objects):
            sketch = self.activeDocument.getObject(objects[0].Name)
            importDXF.export([sketch], os.path.join(
                self.tempDirPath, "%s.dxf" % (label)))
            f = open(os.path.join(self.tempDirPath, "%s.dxf" % (label)), "r")
            content = f.read()
            f.close()
            return content
        else:
            return None

    def getSTEPs(self):

        self.openDocument()

        rotorSegment = self.__getSTEPFromFreeCAD(
            "Rotor_Surface", None, "Rotor_Segment")

        if (self.rotor.type == 12):
            magnetSegment1 = self.__getSTEPFromFreeCAD(
                "Magnet_Surface1", None, "Magnet_Segment1")

            magnetSegment2 = self.__getSTEPFromFreeCAD(
                "Magnet_Surface2", None, "Magnet_Segment2")

            # Close FreeCad document
            self.closeDocument()

            return {
                "Magnet Segment": [magnetSegment1, magnetSegment2],
                "Rotor Segment": rotorSegment,
            }
        else:
            magnetSegment = self.__getSTEPFromFreeCAD(
                "Magnet_Surface", None, "Magnet_Segment")

            # Close FreeCad document
            self.closeDocument()

            return {
                "Magnet Segment": [magnetSegment],
                "Rotor Segment": rotorSegment,
            }

    def getDXFs(self):

        self.openDocument()

        # Export the geometry
        rotorSegment = self.__getDXFFromFreeCAD("RotorPoleSketch")
        magnetSegment = self.__getDXFFromFreeCAD("MagnetSketch")
        pocketSegment = self.__getDXFFromFreeCAD("PocketSketch")

        # Close FreeCad document
        self.closeDocument()

        return {
            "Magnet Segment": magnetSegment,
            "Rotor Segment": rotorSegment,
            "Pocket Segment": pocketSegment
        }

    def setSVG(self):
        # Get the svg
        topViewSVG = self.__getSVGFromFreeCad(fileName="TopViewRotor.svg", faces=[
            {"label": "RotorSketch", "fill": "LightSteelBlue",
                "stroke": "LightSteelBlue", "stroke-width": 1},
            {"label": "RotorPoleSketch", "fill": "LightSteelBlue",
                "stroke": "LightSteelBlue", "stroke-width": 1},
            {"label": "PocketSketch", "fill": "white",
                "stroke": "black", "stroke-width": 0},
            {"label": "MagnetSketch", "fill": "Khaki",
                "stroke": "black", "stroke-width": 0},
            {"label": "MagnetSketch1", "fill": "Khaki",
                "stroke": "black", "stroke-width": 0},
            {"label": "MagnetSketch2", "fill": "Khaki",
                "stroke": "black", "stroke-width": 0},
            {"label": "BoundingBox", "fill": "none",
                "stroke": "none", "stroke-width": 0},
        ])

        sideViewSVG = self.__getSVGFromFreeCad(fileName="TopViewRotor.svg", faces=[
            {"label": "RotorSideSketch", "fill": "LightSteelBlue",
                "stroke": "black", "stroke-width": 0},
            {"label": "MagnetSideSketch", "fill": "Khaki",
                "stroke": "black", "stroke-width": 0},
        ])

        # FreeCAD.ActiveDocument.saveAs(os.path.join(self.tempDirPath, "tmp.FCStd"))

        output = dict()
        output["Top View"] = self.__modifySVG(topViewSVG)
        output["Side View"] = self.__modifySVG(sideViewSVG, rotateView=0)

        self.svg = output
