from ...enums import terminalDirection


class terminal:
    """
    Terminal class. Used to define the boundaries for the winding layout. Additionally, terminal is used in FEM simulations to apply excitations.
    Terminal is just a base class that holds important parameters for all terminal shapes.

    :ivar string color: Hex color code of the terminal.
    :ivar `stator` stator: Stator object needed for the coordinate calculations.
    :ivar `winding` winding: Winding object needed for the coordinate calculations.
    :ivar char phaseLetter: Letter that defines the phase to which the terminal belongs. Default value is 'A'
    :ivar int position: Position defines the slot position to which the terminal belongs. Default value is 0.
    :ivar `terminalDirection` direction: Defines the direction of the wires (or current) inside the terminal. Default value is terminalDirection.input.
    """

    def __init__(self, stator, winding, phaseLetter='A', position=0, direction=terminalDirection.input):
        self.stator = stator
        self.winding = winding
        self.phaseLetter = phaseLetter
        self.position = position
        self.direction = direction
        self.windingAngle = winding.windingAngle  # deg
        self.heightRatio = winding.heightRatio / 100
        self.layers = 1  # calculated in the get wire coordinates

    @property
    def name(self):
        """Sets the name of the terminal"""
        if self.direction == terminalDirection.input:
            return self.phaseLetter + "_%s_" % (self.__class__.__name__) + str(self.position)
        else:
            return self.phaseLetter + "_%s_" % (self.__class__.__name__) + str(self.position)

    @property
    def color(self):
        return self.winding.phaseColors[self.phaseLetter]

    @property
    def polarityType(self):
        if (self.direction == terminalDirection.input):
            return "Positive"
        else:
            return "Negative"

    @property
    def phase(self):
        """Sets the name of the phase to which the terminal belongs."""
        return self.phaseLetter

    def reprJSON(self):
        """ Creates json representation of the object. """

        return {
            "Isolation Coordinates": self.getCoordinates(self.position + 1),
        }
