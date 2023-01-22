import math
from operator import pos
# from fractions import gcd
from ...terminal import *
from ....enums import terminalType, terminalPosition, terminalDirection
from .wdggenerator import *
from .analyse import *


class layout(object):
    """Layout class. It is used to calculate the winding layout of the machine"""

    def __init__(self,  winding):
        self.winding = winding
        self.rotor = self.winding.rotor
        self.stator = self.winding.stator
        self.K0 = self.winding.phaseOffset
        self.numberOfHarmonics = self.stator.slotNumber
        self.numberOfSectors = self.winding.symmetryNumber
        self.scheme = self.getFullCoiledScheme_3phase()
        # self.scheme = self.getAllSchemes()[0]
        # self.getAllSchemes()
        # print(self.scheme)
        # wdg = genwdg(Q=self.stator.slotNumber, P=self.rotor.poleNumber, m=3,
        #              w=self.winding.coilSpan, layers=self.winding.layers, empty_slots=0)

        # nu, Ei, wf, phase = calc_kw(self.stator.slotNumber,
        #                             wdg['phases'], 1, self.rotor.poleNumber/2, 1, get_init_config())

        # print(Ei, wf, phase)
        # print(Ei)

    @property
    def coils_delete(self):
        """Assigns the connection table to terminal objects. Returns the tuple of coils. Each coil is a dictionary of two terminals (input and output)."""
        connectionTable = self.getConnectionTable()

        coils = ()
        if (self.winding.coil.terminalType == terminalType.leftright):
            # print("Pocetak ************************************************************")
            for coil in connectionTable['table']:
                # print(coil)
                terminal = {}
                if (coil['inPosition'] == terminalPosition.left):
                    terminal['input'] = terminalLeft(
                        self.stator, self.winding, coil['phase'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalRight(
                        self.stator, self.winding, coil['phase'], coil['outSlot'], terminalDirection.output)
                else:
                    terminal['input'] = terminalRight(
                        self.stator, self.winding, coil['phase'], coil['inSlot'], terminalDirection.input)
                    terminal['output'] = terminalLeft(
                        self.stator, self.winding, coil['phase'], coil['outSlot'], terminalDirection.output)
                # print(terminal['input'].name, terminal['output'].name)
                coils += (terminal, )
        elif (self.winding.coil.terminalType == terminalType.topbottom):
            pass
        elif (self.winding.coil.terminalType == terminalType.single):
            pass
        else:
            print("Terminal type is not known!")
            return None
        # print("Kraj ************************************************************", len(coils))

        return coils

    def getAngleFromPositions(self, inSlot, outSlot):
        """Returns the relative angle of the coil having positioned in inSlot and outSlot.
        The angle is relative to the first coil of the phase A (see D. Hanselman - Brushless Permanent Magnet Motor Design 2ed.pdf). """
        positions = self.getReferenceCoilPositions()

        for p in positions:
            phaseSlots = np.sort([inSlot, outSlot])
            tableSlots = np.sort(np.array([p["inSlot"], p["outSlot"]]))

            if (phaseSlots == tableSlots).all():
                return p["angle"]

    def getConnectionTable(self):
        """
        Calculates the connection table of the slot winding.

        :ivar dictionary coils: Dictionary that contains the winding table.
        :ivar n-tuple wf: tuple that contains the dictionary with information about the winding factors for the connection table.
        :return dictionary table: table = {'coils' : coils, 'wf' : wf}

        Example of the coils dictionary::
            >>> coils = { 'phase' : phaseLetter, 'angle' : angle_el_degr, 'inSlot' : position, 'outSlot' : position}
        Example of the wf tuple::
            >>> wf = ({"pf" : round(pitchFactor, 3), "df" : round(distributionFactor, 3)}, )


        {'phases': [[[1, 4, 7, 10], [-2, -5, -8, -11]], [[2, 5, 8, 11], [-3, -6, -9, -12]], [[3, 6,
            9, 12], [-4, -7, -10, -1]]], 'wstep': 1, 'valid': True, 'error': '', 'info': '', 'Qes': 0}
        Machine 9N6P (coil)
        .. code-block:: python

            {'phase': 'A', 'angle': 0.0, 'inSlot': 0,
                'outSlot': 1, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 1,
                'outSlot': 2, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 2,
                'outSlot': 3, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'A', 'angle': 0.0, 'inSlot': 3,
                'outSlot': 4, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 4,
                'outSlot': 5, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 5,
                'outSlot': 6, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'A', 'angle': 0.0, 'inSlot': 6,
                'outSlot': 7, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 7,
                'outSlot': 8, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 8,
                'outSlot': 0, 'inPosition': 1, 'outPosition': 2}

        """

        wdg = genwdg(Q=self.stator.slotNumber, P=self.rotor.poleNumber, m=3,
                     w=self.winding.coilSpan, layers=self.winding.layers, empty_slots=0)

        table = ()
        coil = 0

        for index, phase in enumerate(wdg["phases"]):
            if self.winding.layers == 2:
                for i in range(len(phase[0])):
                    raw = {}
                    raw["phase"] = self.winding.phaseLetters[index]
                    raw["Coil Number"] = coil
                    raw["angle"] = self.getAngleFromPositions(
                        abs(phase[0][i])-1, abs(phase[1][i])-1)

                    if phase[0][i] > 0:
                        raw["inSlot"] = abs(phase[0][i]) - 1
                        raw["outSlot"] = abs(phase[1][i]) - 1

                        raw['inPosition'] = terminalPosition.left
                        raw['outPosition'] = terminalPosition.right
                    else:
                        raw["outSlot"] = abs(phase[0][i]) - 1
                        raw["inSlot"] = abs(phase[1][i]) - 1

                        raw['inPosition'] = terminalPosition.right
                        raw['outPosition'] = terminalPosition.left

                    coil += 1
                    # print(raw)
                    table += (raw, )

        output = {}
        output['table'] = table
        output['wf'] = self.getWindingFactors(table)

        return output

    def getConnectionTableOld_Delete(self):
        """
        Calculates the connection table of the slot winding.

        :ivar dictionary coils: Dictionary that contains the winding table.
        :ivar n-tuple wf: tuple that contains the dictionary with information about the winding factors for the connection table.
        :return dictionary table: table = {'coils' : coils, 'wf' : wf}

        Example of the coils dictionary::
            >>> coils = { 'phase' : phaseLetter, 'angle' : angle_el_degr, 'inSlot' : position, 'outSlot' : position}
        Example of the wf tuple::
            >>> wf = ({"pf" : round(pitchFactor, 3), "df" : round(distributionFactor, 3)}, )


        {'phases': [[[1, 4, 7, 10], [-2, -5, -8, -11]], [[2, 5, 8, 11], [-3, -6, -9, -12]], [[3, 6, 9, 12], [-4, -7, -10, -1]]], 'wstep': 1, 'valid': True, 'error': '', 'info': '', 'Qes': 0}
        Machine 9N6P (coil)
        .. code-block:: python

            {'phase': 'A', 'angle': 0.0, 'inSlot': 0, 'outSlot': 1, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 1, 'outSlot': 2, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 2, 'outSlot': 3, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'A', 'angle': 0.0, 'inSlot': 3, 'outSlot': 4, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 4, 'outSlot': 5, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 5, 'outSlot': 6, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'A', 'angle': 0.0, 'inSlot': 6, 'outSlot': 7, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'B', 'angle': 0.0, 'inSlot': 7, 'outSlot': 8, 'inPosition': 1, 'outPosition': 2}
            {'phase': 'C', 'angle': 0.0, 'inSlot': 8, 'outSlot': 0, 'inPosition': 1, 'outPosition': 2}

        """

        positions = self.getReferenceCoilPositions()

        table = ()
        coil_counter = 1
        for k in range(int(self.stator.slotNumber)):
            # for k in range(int(self.stator.slotNumber / self.numberOfSectors)):
            if (list(self.scheme)[k] == 'A'):
                for i in range(self.winding.phaseNumber):
                    raw = {}
                    raw["Coil Number"] = coil_counter
                    raw["phase"] = self.winding.phaseLetters[i]
                    raw["angle"] = positions[k]['angle']
                    raw["inSlot"] = (positions[k]['inSlot'] +
                                     i * self.K0) % self.stator.slotNumber
                    raw["outSlot"] = (positions[k]['outSlot'] +
                                      i * self.K0) % self.stator.slotNumber

                    if (self.winding.coil.terminalType == terminalType.leftright):
                        if ((self.scheme.count('A') == 1 or k < self.stator.slotNumber - self.winding.phaseNumber) or positions[k]['inSlot'] != 0 and positions[k]['inSlot'] != 0):
                            if (positions[k]['inSlot'] < positions[k]['outSlot']):
                                raw['inPosition'] = terminalPosition.left
                                raw['outPosition'] = terminalPosition.right
                            else:
                                raw['inPosition'] = terminalPosition.right
                                raw['outPosition'] = terminalPosition.left
                        else:
                            if (positions[k]['inSlot'] < positions[k]['outSlot']):
                                raw['inPosition'] = terminalPosition.right
                                raw['outPosition'] = terminalPosition.left
                            else:
                                raw['inPosition'] = terminalPosition.left
                                raw['outPosition'] = terminalPosition.right
                    elif (self.winding.coil.terminalType == terminalType.topbottom):
                        if ((self.scheme.count('A') == 1 or k < self.stator.slotNumber - self.winding.phaseNumber) or positions[k]['inSlot'] != 0 and positions[k]['inSlot'] != 0):
                            if (positions[k]['inSlot'] < positions[k]['outSlot']):
                                raw['inPosition'] = terminalPosition.bottom
                                raw['outPosition'] = terminalPosition.top
                            else:
                                raw['inPosition'] = terminalPosition.top
                                raw['outPosition'] = terminalPosition.bottom
                        else:
                            if (positions[k]['inSlot'] < positions[k]['outSlot']):
                                raw['inPosition'] = terminalPosition.top
                                raw['outPosition'] = terminalPosition.bottom
                            else:
                                raw['inPosition'] = terminalPosition.bottom
                                raw['outPosition'] = terminalPosition.top
                    elif (self.winding.coil.terminalType == terminalType.single):
                        raw['inPosition'] = terminalPosition.single
                        raw['outPosition'] = terminalPosition.single
                    else:
                        raw['inPosition'] = None
                        raw['outPosition'] = None

                    # print(coil)
                    table += (raw, )
                    coil_counter += 1
        output = {}
        output['table'] = table
        output['wf'] = self.getWindingFactors(table)

        return output

    def getWindingFactors(self, table):
        """
        Calculates the winding factors for the actual connection table. Used in **`getConnectionTable()`**.
        The winding factors are calculated for maximum number of harmonics defined with numberOfHarmonics.

        :param dictionary table: This is connection table for which the winding factors are calculated.

        :ivar n-tuple wf: tuple that contains the dictionary with the information about the winding factors for the connection table.

            Example of the wf tuple::
                >>> wf = ({"pf" : round(pitchFactor, 3), "df" : round(distributionFactor, 3)}, )

        :return n-tuple wf: wf = ({"pf" : round(pitchFactor, 3), "df" : round(distributionFactor, 3)}, ...)
        """
        windingfactors = ()
        for n in range(1, self.numberOfHarmonics + 1):
            re, im, counter = 0, 0, 0
            for k in range(len(table)):
                if (table[k]['phase'] == 'A'):
                    re += math.cos(n * table[k]['angle'] * math.pi / 180)
                    im -= math.sin(n * table[k]['angle'] * math.pi / 180)
                    counter += 1

                pitchFactor = math.sin(
                    math.pi * self.rotor.poleNumber / self.stator.slotNumber / 2 * self.winding.coilSpan)
                distributionFactor = 1 / counter * math.sqrt(re**2 + im**2)

            windingfactors += ({"Harmonic": n, "Pitch Factor": round(pitchFactor, 3),
                               "Distribution Factor": round(distributionFactor, 3)}, )
        return windingfactors

    def getReferenceCoilPositions(self):
        """
        Calculate possible positions for the coils of the reference phase (Phase "A").
        To get the positions of other phases the phase offset has to be used. In fact what is calulated is the table:

        It is also used to calculate the initial position of the rotor. The angles calculates here are relative to the position of the first coil! 

        Reference table example (12 slot, 10 pole machine)::

            =======    ====    ====     ====    ====    ====    ====    ====    ====    ====   ====    ====    ====
            Coil       1       2        3       4       5       6       7       8       9      10      11      12
            -------    ----    ----     ----    ----    ----    ----    ----    ----    ----   ----    ----    ----
            Angle       0       -30      -60     90      60      30      0       -30    -60    90      60      30
            inSlot      1       3        3       4       6       6       8       8       10     10      11      1
            outSlot     2       2        4       5       5       7       7       9       9      11      12      12
            =======    ====    ====     ====    ====    ====    ====    ====    ====    ====   ====    ====    ====

        :ivar n-tuple table: tuple that contains the dictionary with the information about the reference coil positions.

        Example of adding dictionary (can be seen as a row of the table) to the table tuple::
            >>> table += ({"angle" : angle, "inSlot" : inslot, "outSlot": outslot}, )

        :return n-tuple table: table += ({"angle" : angle, "inSlot" : inslot, "outSlot": outslot}, )
        """

        table = ()
        for k in range(self.stator.slotNumber):
            angle = (k * float(self.rotor.poleNumber) /
                     self.stator.slotNumber * 180.0 + 180.0) % 360.0 - 180.0
            if (abs(angle) > 90):
                inslot = (k + self.winding.coilSpan) % self.stator.slotNumber
                outslot = k
                if (angle > 0):
                    angle -= 180
                else:
                    angle += 180
            else:
                inslot = k
                outslot = (
                    k + self.winding.coilSpan) % self.stator.slotNumber

            table += ({"angle": angle, "inSlot": inslot, "outSlot": outslot}, )

        return table

    def isEmpty(self, position, scheme):
        """
        Checks if the slot where the coil should be places is empty. It is used to determine layout schemes in **`getAllSchemes()`**.

        :return bool: True or False
        """
        for i in range(self.winding.phaseNumber):
            if (scheme[(position + i * self.K0) % int(self.stator.slotNumber / self.numberOfSectors)] != '0'):
                return False
        return True

    def setValidScheme(self, position, scheme):
        """
        Sets the valid scheme, i.e. it adds additional phases to the winding scheme pased on the phase offset.

        :param int position: This is the current position of the slot.
        :param string scheme: This is a winding sheme to which new coils are to be added.

        :return None:
        """
        s = list(scheme)
        for i in range(self.winding.phaseNumber):
            s[(position + i * self.K0) % int(self.stator.slotNumber /
                                             self.numberOfSectors)] = self.winding.phaseLetters[i]

        return s

    def initializeSchemes(self):
        """
        Initializes the winding scheme calculation.

        .. note::
            If number of layers is 1 than every even numbered slot is blocked. Blocked slot is shown as "-" in a string.
            Otherwise use every slot. Free slot is shown as "0".

        :return None:
        """
        scheme = self.setValidScheme(
            0, ['0'] * int(self.stator.slotNumber / self.numberOfSectors))
        if (self.winding.layers == 1):
            scheme = ['-' if i % 2 else w for i, w in enumerate(scheme)]
        schemes = [''.join(scheme)]
        return schemes

    def isRotationalDuplicate(self, schemes, scheme):
        """
        Checks if there is already a rotational duplicate of the string in a list os winding schemes.

        :return bool: True or False
        """
        for l in schemes:
            if (scheme in l * 2):
                return True
        return False

    def getAllSchemes(self):
        """
        Calculates all possible winding schemes for the chosen pole and slot number combination.

        .. warning::
            If the number of slot is larger than 36 it may take some time for tha calculation to finish.
            This is because the larger number of slots increase the number of all possible winding combinations.

            This should be used by the expert. More safe is to use full-coiled and half-coiled winding layout functions.
            They always give optimal layout with regard to the winding factor. They are also used by ANSYS.

        :return n-list schemes: list of strings. Each string represents valid winding scheme.
        """
        schemes = self.initializeSchemes()

        for scheme in schemes:
            for position in range(0, int(self.stator.slotNumber / self.numberOfSectors), int(2 / self.winding.layers)):
                if (self.isEmpty(position, list(scheme))):
                    if (not self.isRotationalDuplicate(schemes, ''.join(self.setValidScheme(position, scheme)))):
                        # print(scheme)

                        schemes.append(
                            ''.join(self.setValidScheme(position, scheme)))

        """ Remove schemes from the list with '0' items. """
        schemes = [i for i in schemes if ('0' not in i)]

        #     print(item)
        # """ Sorth layouts based on the resilting winding distribution factor of the base harmonic (1st harmonic). """
        # output = []
        # for layout in layouts:
        #     output.append({'layout' : layout * self.numberOfSectors, 'table' : self.getLayoutTable(layout * self.numberOfSectors)})
        # output.sort(key=lambda x : x['table']['wf'][0]['df'], reverse=True)

        # for item in output:
        #     print(item)
        # layouts = []
        # for layout in output['layout']:
        #     layouts.append(layout)
        return schemes

    def getFullCoiledScheme_3phase(self):
        """ Calculates the full-coiled layout of the 3-phase system. Coils are numbered in CCW direction. All angles are in electrical degrees. That is whay the
            slot angle is multiplied by poleNumber / 2. """

        """ Counters for the layout. """
        A, B, C, a, b, c = 0, 0, 0, 0, 0, 0
        scheme = ''
        for position in range(0, self.stator.slotNumber):
            """ Angle is the position of the current slot in the electrical degrees. """
            angle = position * self.rotor.poleNumber / \
                2 * 360 / self.stator.slotNumber % 360

            if (self.winding.layers == 1 and position % 2):
                scheme += '-'
            else:
                if (angle >= 0 and angle < self.winding.phaseShift / 2):
                    scheme += 'A'
                    A += 1
                elif (angle >= self.winding.phaseShift / 2 and angle < 2 * self.winding.phaseShift / 2):
                    scheme += 'c'
                    c += 1
                elif (angle >= 2 * self.winding.phaseShift / 2 and angle < 3 * self.winding.phaseShift / 2):
                    scheme += 'B'
                    B += 1
                elif (angle >= 3 * self.winding.phaseShift / 2 and angle < 4 * self.winding.phaseShift / 2):
                    scheme += 'a'
                    a += 1
                elif (angle >= 4 * self.winding.phaseShift / 2 and angle < 5 * self.winding.phaseShift / 2):
                    scheme += 'C'
                    C += 1
                else:
                    scheme += 'b'
                    b += 1

        if (A == B == C and a == b == c):
            # return scheme.upper()[:int(self.stator.slotNumber / self.numberOfSectors)]
            return scheme.upper()[:int(self.stator.slotNumber)]

        else:
            print("winding is not balanced!")
            return None

    def getHalfCoiledScheme_3phase(self):
        """ Calculates the full-coiled layout of the 3-phase system. Coils are numbered in CCW direction. All angles are in electrical degrees. That is whay the
            slot angle is multiplied by poleNumber / 2. """

        """ Counters for the layout. """
        A, B, C, a, b, c = 0, 0, 0, 0, 0, 0
        scheme = ''
        for position in range(0, self.stator.slotNumber):
            """ Angle is the position of the current slot in the electrical degrees. """
            angle = position * self.rotor.poleNumber / \
                2 * 360 / self.stator.slotNumber % 360

            if (self.winding.layers == 1 and position % 2):
                scheme += '-'
            else:
                if (angle >= 0 and angle < self.winding.phaseShift / 2):
                    scheme += 'A'
                    A += 1
                elif (angle >= self.winding.phaseShift / 2 and angle < 2 * self.winding.phaseShift / 2):
                    scheme += 'a'
                    a += 1
                elif (angle >= 2 * self.winding.phaseShift / 2 and angle < 3 * self.winding.phaseShift / 2):
                    scheme += 'B'
                    B += 1
                elif (angle >= 3 * self.winding.phaseShift / 2 and angle < 4 * self.winding.phaseShift / 2):
                    scheme += 'b'
                    b += 1
                elif (angle >= 4 * self.winding.phaseShift / 2 and angle < 5 * self.winding.phaseShift / 2):
                    scheme += 'C'
                    C += 1
                else:
                    scheme += 'c'
                    c += 1

        if (A == B == C and a == b == c):
            return scheme.upper()[:int(self.stator.slotNumber / self.numberOfSectors)]
        else:
            print("winding is not balanced!")
            return None

    def reprJSON(self):
        """ Creates json representation of the object. """
        return {
            # "Coils": self.coils,
            "Connection Table": self.getConnectionTable(),
        }
