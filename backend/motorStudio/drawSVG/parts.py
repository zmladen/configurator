import os
import sys
import svgwrite
from svgwrite import cm, mm
from enums.enums import *
from utilities import *
from pmMachine.terminal import *


class parts(object):
    """
    Class plotobjects. It contains the methods to plot single objects of the drive geometry package, e.g. slot, sector, terminal, etc.
    """

    def __init__(self, project):
        self.project = project
        self.imageSize = ('9cm', '9cm')

    def drawMachineXY(self, **kwargs):
        """Plots the rotor object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorPole = kwargs.pop('fillColorPole', 'red')
        fillColorPocket = kwargs.pop('fillColorPocket', 'white')
        fillColorMagnet = kwargs.pop('fillColorMagnet', 'green')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)

        bb = boundingBox([point(-self.project.machine.housing.outerDiameter / 2, -self.project.machine.housing.outerDiameter / 2), point(self.project.machine.housing.outerDiameter / 2, self.project.machine.housing.outerDiameter / 2)])
        self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.layoutImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                 margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
        self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        self.drawHousingXY()
        self.drawStatorXY()
        self.drawLayoutXY()
        self.drawRotorXY()

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawMachineXZ(self, **kwargs):
        """Plots the rotor object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorPole = kwargs.pop('fillColorPole', 'red')
        fillColorPocket = kwargs.pop('fillColorPocket', 'white')
        fillColorMagnet = kwargs.pop('fillColorMagnet', 'green')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)

        maxHeight = self.project.machine.housing.outerDiameter
        maxWidth = self.project.machine.housing.stacklength + 2 * (self.project.machine.winding.axialOverhang + self.project.machine.winding.coil.axialHeight)

        if maxHeight >= maxWidth:
            bb = boundingBox([point(-maxHeight / 2, -maxHeight / 2), point(maxHeight / 2, maxHeight / 2)])
        else:
            bb = boundingBox([point(-maxWidth / 2, -maxWidth / 2), point(maxWidth / 2, maxWidth / 2)])

        self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.layoutImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                 margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
        self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        self.drawHousingXZ()
        self.drawStatorXZ()
        self.drawRotorXZ()

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawHousingXY(self, **kwargs):
        """Plots the housing object. The colors are mapped to the corresponding phase letters."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.stator.outerDiameter / 2, -self.project.machine.stator.outerDiameter / 2), point(self.project.machine.stator.outerDiameter / 2, self.project.machine.stator.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.statorImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                     margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        # Plot wires
        self.__drawCircle(center=point(0, 0), radius=self.project.machine.housing.outerDiameter / 2, strokeColor=strokeColor, fillColor=self.project.machine.housing.color)
        self.__drawCircle(center=point(0, 0), radius=self.project.machine.housing.innerDiameter / 2, strokeColor=strokeColor, fillColor='#FFFFFF')

        # self.dwg.save()
        return self.dwg.tostring()

    def drawHousingXZ(self, **kwargs):
        """Plots the stator object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColor = kwargs.pop('fillColor', 'blue')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.housing.outerDiameter / 2, -self.project.machine.housing.outerDiameter / 2), point(self.project.machine.housing.outerDiameter / 2, self.project.machine.housing.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.statorImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                     margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        # Top sheets
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.housing.stacklength / 2,
            y_bottom_left=self.project.machine.housing.innerDiameter / 2,
            width=self.project.machine.housing.stacklength,
            height=(self.project.machine.housing.outerDiameter - self.project.machine.housing.innerDiameter) / 2,
            fillColor=fillColor,
        )

        # Bottom sheets
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.housing.stacklength / 2,
            y_bottom_left=-self.project.machine.housing.outerDiameter / 2,
            width=self.project.machine.housing.stacklength,
            height=(self.project.machine.housing.outerDiameter - self.project.machine.housing.innerDiameter) / 2,
            fillColor=fillColor,
        )

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawLayoutXY(self, **kwargs):
        """Plots the winding layout object. The colors are mapped to the corresponding phase letters."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.housing.outerDiameter / 2, -self.project.machine.housing.outerDiameter / 2), point(self.project.machine.housing.outerDiameter / 2, self.project.machine.housing.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.statorImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                     margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        for coil in self.project.machine.winding.layout.coils:
            self.__drawPolylineSegment(object=coil['input'], position=coil['input'].position, strokeColor=strokeColor, fillColor=self.project.machine.winding.phaseColors[coil['input'].phaseLetter])
            self.__drawPolylineSegment(object=coil['output'], position=coil['output'].position, strokeColor=strokeColor, fillColor=self.project.machine.winding.phaseColors[coil['output'].phaseLetter])

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawStatorXY(self, **kwargs):
        """Plots the stator object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorSector = kwargs.pop('fillColorSector', 'red')
        fillColorTerminal = kwargs.pop('fillColorTerminal', 'white')
        fillColorSlot = kwargs.pop('fillColorSlot', 'white')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.stator.outerDiameter / 2, -self.project.machine.stator.outerDiameter / 2), point(self.project.machine.stator.outerDiameter / 2, self.project.machine.stator.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(filename, size=self.imageSize, viewBox=(str(bb.minx - margin[0]) + ' ' + str(-bb.maxy - margin[3]
                                                                                                                             ) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        for position in range(self.project.machine.stator.slotNumber):
            self.__drawPolylineSegment(object=self.project.machine.stator.sector, position=position, strokeColor=strokeColor, fillColor=fillColorSector)
            self.__drawPolylineSegment(object=self.project.machine.stator.sector.slot, position=position, strokeColor=strokeColor, fillColor=fillColorSlot)

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawStatorXZ(self, **kwargs):
        """Plots the stator object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorSector = kwargs.pop('fillColorSector', 'red')
        fillColorOverhang = kwargs.pop('fillColorOverhang', 'white')
        fillColorSlot = kwargs.pop('fillColorSlot', 'green')
        fillColorCoilHeight = kwargs.pop('fillColorCoilHeight', 'orange')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.stator.outerDiameter / 2, -self.project.machine.stator.outerDiameter / 2), point(self.project.machine.stator.outerDiameter / 2, self.project.machine.stator.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.statorImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                     margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        # Top sheets
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2,
            y_bottom_left=self.project.machine.stator.innerDiameter / 2,
            width=self.project.machine.stator.stacklength,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2
        )

        # Bottom sheets
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2,
            y_bottom_left=-self.project.machine.stator.outerDiameter / 2,
            width=self.project.machine.stator.stacklength,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2
        )

        # Overhang top left
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2 - self.project.machine.winding.axialOverhang,
            y_bottom_left=self.project.machine.stator.innerDiameter / 2,
            width=self.project.machine.winding.axialOverhang,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorOverhang,
        )

        # Overhang top right
        self.__drawRectangle(
            x_bottom_left=self.project.machine.stator.stacklength / 2,
            y_bottom_left=self.project.machine.stator.innerDiameter / 2,
            width=self.project.machine.winding.axialOverhang,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorOverhang,
        )

        # Overhang bottom left
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2 - self.project.machine.winding.axialOverhang,
            y_bottom_left=-self.project.machine.stator.outerDiameter / 2,
            width=self.project.machine.winding.axialOverhang,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorOverhang,
        )

        # Overhang bottom right
        self.__drawRectangle(
            x_bottom_left=self.project.machine.stator.stacklength / 2,
            y_bottom_left=-self.project.machine.stator.outerDiameter / 2,
            width=self.project.machine.winding.axialOverhang,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorOverhang,
        )

        # End-winding top left
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2 - self.project.machine.winding.axialOverhang - self.project.machine.winding.coil.axialHeight,
            y_bottom_left=self.project.machine.stator.innerDiameter / 2,
            width=self.project.machine.winding.coil.axialHeight,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorCoilHeight,
        )

        # End-winding top right
        self.__drawRectangle(
            x_bottom_left=self.project.machine.stator.stacklength / 2 + self.project.machine.winding.axialOverhang,
            y_bottom_left=self.project.machine.stator.innerDiameter / 2,
            width=self.project.machine.winding.coil.axialHeight,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorCoilHeight,
        )

        # End-winding bottom left
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.stator.stacklength / 2 - self.project.machine.winding.axialOverhang - self.project.machine.winding.coil.axialHeight,
            y_bottom_left=-self.project.machine.stator.outerDiameter / 2,
            width=self.project.machine.winding.coil.axialHeight,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorCoilHeight,
        )

        # End-winding bottom right
        self.__drawRectangle(
            x_bottom_left=self.project.machine.stator.stacklength / 2 + self.project.machine.winding.axialOverhang,
            y_bottom_left=-self.project.machine.stator.outerDiameter / 2,
            width=self.project.machine.winding.coil.axialHeight,
            height=(self.project.machine.stator.outerDiameter - self.project.machine.stator.innerDiameter) / 2,
            fillColor=fillColorCoilHeight,
        )

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawRotorXY(self, **kwargs):
        """Plots the rotor object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorPole = kwargs.pop('fillColorPole', 'red')
        fillColorPocket = kwargs.pop('fillColorPocket', 'white')
        fillColorMagnet = kwargs.pop('fillColorMagnet', 'green')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.rotor.outerDiameter / 2, -self.project.machine.rotor.outerDiameter / 2), point(self.project.machine.rotor.outerDiameter / 2, self.project.machine.rotor.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(filename, size=self.imageSize, viewBox=(str(bb.minx - margin[0]) + ' ' + str(-bb.maxy - margin[3]
                                                                                                                             ) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        for position in range(self.project.machine.rotor.poleNumber):
            self.__drawPolylineSegment(object=self.project.machine.rotor.pole, position=position, strokeColor=strokeColor, fillColor=fillColorPole)
            for pocket in self.project.machine.rotor.pole.pockets:
                self.__drawPolylineSegment(object=pocket, position=position, strokeColor=strokeColor, fillColor=fillColorPocket)
                self.__drawPolylineSegment(object=pocket.magnet, position=position, strokeColor=strokeColor, fillColor=fillColorMagnet)

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawRotorXZ(self, **kwargs):
        """Plots the rotor object."""

        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        strokeColor = kwargs.pop('strokeColor', 'black')
        fillColorPole = kwargs.pop('fillColorPole', 'red')
        fillColorPocket = kwargs.pop('fillColorPocket', 'white')
        fillColorMagnet = kwargs.pop('fillColorMagnet', 'green')
        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        createNewGroup = kwargs.pop('createNewGroup', False)

        if createNewGroup:
            bb = boundingBox([point(-self.project.machine.stator.outerDiameter / 2, -self.project.machine.stator.outerDiameter / 2), point(self.project.machine.stator.outerDiameter / 2, self.project.machine.stator.outerDiameter / 2)])
            # Create dwg canvas and group.
            self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.statorImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                                     margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
            self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=strokeWidth, fill='red', transform='translate(0, 0), scale(1,-1)'))

        # Steel sheets top
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.rotor.stacklength / 2,
            y_bottom_left=self.project.machine.rotor.innerDiameter / 2,
            width=self.project.machine.rotor.stacklength,
            height=self.project.machine.rotor.outerDiameter / 2 - self.project.machine.rotor.pole.pockets[0].magnet.height - self.project.machine.rotor.innerDiameter / 2
        )

        # Steel sheets bottom
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.rotor.stacklength / 2,
            y_bottom_left=-self.project.machine.rotor.outerDiameter / 2 + self.project.machine.rotor.pole.pockets[0].magnet.height,
            width=self.project.machine.rotor.stacklength,
            height=self.project.machine.rotor.outerDiameter / 2 - self.project.machine.rotor.pole.pockets[0].magnet.height - self.project.machine.rotor.innerDiameter / 2
        )

        # Magnet bottom
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.rotor.stacklength / 2,
            y_bottom_left=-self.project.machine.rotor.outerDiameter / 2,
            width=self.project.machine.rotor.stacklength,
            height=self.project.machine.rotor.pole.pockets[0].magnet.height,
            fillColor=fillColorMagnet,
        )

        # Magnet bottom
        self.__drawRectangle(
            x_bottom_left=-self.project.machine.rotor.stacklength / 2,
            y_bottom_left=self.project.machine.rotor.outerDiameter / 2 - self.project.machine.rotor.pole.pockets[0].magnet.height,
            width=self.project.machine.rotor.stacklength,
            height=self.project.machine.rotor.pole.pockets[0].magnet.height,
            fillColor=fillColorMagnet,
        )
        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def drawSlotXY(self, **kwargs):
        """Plots the slot with the wires."""

        margin = kwargs.pop('margin', (1, 1, 1, 1))
        filename = kwargs.pop('filename', None)
        bb = boundingBox.__polylinesegments__(self.project.machine.stator.sector.slot.getCoordinates()['polylineSegments'])

        # Create dwg canvas and group.
        self.dwg = svgwrite.drawing.Drawing(self.project.imageDirectory + "\\" + self.project.slotImageName, size=self.imageSize, viewBox=(str(bb.minx -
                                                                                                                                               margin[0]) + ' ' + str(-bb.maxy - margin[3]) + ' ' + str(bb.maxx - bb.minx + 2 * margin[2]) + ' ' + str(bb.maxy - bb.miny + 2 * margin[1])))
        self.group = self.dwg.add(self.dwg.g(id='path', stroke='white', stroke_width=0.01, fill='red', transform='translate(0, 0), scale(1,-1)'))

        self.__drawPolylineSegment(object=self.project.machine.stator.sector.slot, position=0, strokeColor='#BCD1CF', fillColor='#BCD1CF')
        self.__drawPolylineSegment(object=terminalLeft(self.project.machine.stator, self.project.machine.winding), position=0, strokeColor='#F46763', fillColor='yellow')
        self.__drawPolylineSegment(object=terminalRight(self.project.machine.stator, self.project.machine.winding), position=0, strokeColor='#F46763', fillColor='yellow')

        # Plot wires
        for p in terminalLeft(self.project.machine.stator, self.project.machine.winding).getWireCoordinates()['coordinates']:
            self.__drawCircle(center=p, radius=self.project.machine.winding.coil.wire.isolationDiameter / 2, strokeColor='#F43B1C', fillColor='#F43B1C')
            self.__drawCircle(center=p, radius=self.project.machine.winding.coil.wire.conductorDiameter / 2, strokeColor='#F43B1C', fillColor='#CBB884')

        for p in terminalRight(self.project.machine.stator, self.project.machine.winding).getWireCoordinates()['coordinates']:
            self.__drawCircle(center=p, radius=self.project.machine.winding.coil.wire.isolationDiameter / 2, strokeColor='#F43B1C', fillColor='#F43B1C')
            self.__drawCircle(center=p, radius=self.project.machine.winding.coil.wire.conductorDiameter / 2, strokeColor='#F43B1C', fillColor='#CBB884')

        if filename != None:
            self.dwg.save()
            return None
        else:
            return self.dwg.tostring()

    def __drawPolylineSegment(self, **kwargs):
        """
        Plots the object.
        Depending on the filename the method either returns the path (when filename is None) or saves an SVG image to the directory path defined by the filename.

        :param filename: string. Filename of the SVG image. The default value is None, i.e. no picture will be saved.
        :param position: int. Position of the slot to be plotted. Default value is 0.
        :param strokeColor: string. Color for the stroke. Default value is black.
        :param fillColor: string. Fill color of the object. Default value is red.
        :param 4-tuple margin: margin = (left, top, right, bottom) in %.
        :returs: None
        """
        object, strokeColor, fillColor, position = kwargs['object'], kwargs['strokeColor'], kwargs['fillColor'], kwargs['position']
        pathstring = self.__path(object.getCoordinates(position)['polylineSegments'])
        self.group.add(self.dwg.path(d=pathstring, stroke=strokeColor, fill=fillColor))

    def __drawCircle(self, **kwargs):
        """
        Plots the wire object.
        Depending on the filename the method either returns the path (when filename is None) or saves an SVG image to the directory path defined by the filename.

        :param filename: string. Filename of the SVG image. The default value is None, i.e. no picture will be saved.
        :param position: int. Position of the slot to be plotted. Default value is 0.
        :param strokeColor: string. Color for the stroke. Default value is black.
        :param fillColor: string. Fill color of the object. Default value is red.
        :returs: None
        """
        center, radius, strokeColor, fillColor = kwargs['center'], kwargs['radius'], kwargs['strokeColor'], kwargs['fillColor']
        self.group.add(self.dwg.circle((center.X, center.Y), radius, stroke_width=0.01, stroke=strokeColor, fill=fillColor))

    def __drawRectangle(self, **kwargs):
        x_bottom_left = kwargs.pop('x_bottom_left', 0)
        y_bottom_left = kwargs.pop('y_bottom_left', 0)
        width = kwargs.pop('width', 10)
        height = kwargs.pop('height', 10)
        strokeColor = kwargs.pop('strokeColor', 'black')
        strokeWidth = kwargs.pop('strokeWidth', 0.1)
        fillColor = kwargs.pop('fillColor', 'red')

        self.group.add(self.dwg.rect(insert=(x_bottom_left, y_bottom_left), size=(width, height), fill=fillColor, stroke=strokeColor, stroke_width=strokeWidth))

    def __path(self, segments):
        """Gets the path string based on the polylineSegments."""
        mypath = []
        for segment in segments:
            if (segment['type'] == segmentType.line):
                self.__addLine(mypath, p0=(segment['points'][0].X, segment['points'][0].Y), p1=(segment['points'][1].X, segment['points'][1].Y))
            if (segment['type'] == segmentType.arccircle):
                self.__add3PointArcCircle(mypath, p0=segment['points'][0], p1=segment['points'][1], p2=segment['points'][2])
        mypath.append(" Z")

        return mypath

    def __addLine(self, mypath, p0, p1):
        """Adds an line that bulges to the right as it moves from p0 to p1."""
        args = {'x0': p0[0], 'y0': p0[1], 'x1': p1[0], 'y1': p1[1]}

        if len(mypath) == 0:
            mypath.append("M %(x0)f, %(y0)f L %(x1)f, %(y1)f" % args)
        else:
            mypath.append(" L %(x1)f, %(y1)f" % args)

    def __add3PointArcCircle(self, mypath, p0, p1, p2):
        """Adds an arccircle that passe through 3 points."""
        c = circle.__3points__(p0, p1, p2)
        """ Rotate all points to 90 deg. """
        arcslope = p1.getRelativeSlope360(c.center)
        p0_rot = p0.rotateArroundPointCopy(c.center, -arcslope + 90)
        p2_rot = p2.rotateArroundPointCopy(c.center, -arcslope + 90)
        if (p0_rot.getRelativeSlope360(c.center) - p2_rot.getRelativeSlope360(c.center) > 0):
            sweep_flag = 0
        else:
            sweep_flag = 1

        if (arcslope == 0 and not p0.X == p2.X and not p0.Y == p2.Y):
            large_arc_flag = 1
        else:
            large_arc_flag = 0

        args = {'x0': p0.X, 'y0': p0.Y, 'xradius': c.radius, 'yradius': c.radius, 'ellipseRotation': 0, 'large_arc_flag': large_arc_flag, 'sweep_flag': sweep_flag, 'x1': (p2.X - p0.X), 'y1': (p2.Y - p0.Y)}
        if len(mypath) == 0:
            mypath.append("M %(x0)f, %(y0)f a %(xradius)f, %(yradius)f %(ellipseRotation)d %(large_arc_flag)d, %(sweep_flag)d, %(x1)f, %(y1)f" % args)
        else:
            mypath.append(" a %(xradius)f, %(yradius)f %(ellipseRotation)f %(large_arc_flag)d, %(sweep_flag)d, %(x1)f, %(y1)f" % args)
