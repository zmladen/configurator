# from fractions import gcd
import math
from ..enums import *
from ..common.ring import *
from ..common.pie import *
from ..common.mechanics import *
from ..common.environment import *
from .controlcircuit import *
from .stator import *
from .rotor import *
from .winding import *
from utils import *
from utils import svg
from .stator.geometry import geometry as statorGeometry
from .rotor.geometry import geometry as rotorGeometry
from ..common.ring.geometry import geometry as ringGeometry
from ..common.pie.geometry import geometry as pieGeometry


class pmMachine(object):
    """This is a geometry class. It is used as a container for all other modules / classes necessary to define the drive geometry.
    :param dict data: JSON dictionary used for the object initialization. Default value is empty string."""

    def __init__(self, data={}, recomputeGeometry=True):
        """Constructor for the bldc machine object with the needed parameters"""

        self.type = machineType.bldcInnerRunner
        self.useSymmetry = True
        self.nameplate = None

        if not data == {}:
            self.readJSON(data["design"])
        else:
            self.stator = stator(statorType.stator6)
            self.rotor = rotor(rotorType.rotor1)
            self.shaft = pie(segmentNumber=self.rotor.poleNumber)
            self.winding = winding(
                self.stator, self.rotor, symmetryNumber=self.symmetryNumber)
            self.housing = ring(segmentNumber=self.stator.slotNumber)
            self.separationcan = ring(segmentNumber=self.stator.slotNumber)
            self.controlcircuit = None
            self.environment = environment()
            self.mechanics = mechanics()

        self.innerRegion = pie(segmentNumber=self.rotor.poleNumber)
        self.region = pie(segmentNumber=self.stator.slotNumber)
        self.band = pie(segmentNumber=self.rotor.poleNumber)

        self.innerRegion.segmentNumber = self.rotor.poleNumber
        self.region.segmentNumber = self.stator.slotNumber
        self.region.outerDiameter = self.housing.outerDiameter * 1.1
        self.separationcan.length = self.stator.stacklength

        if (self.stator.type == statorType.stator5):
            # Outer-Runner
            self.band = ring(segmentNumber=self.rotor.poleNumber)
            self.housing.length = self.rotor.stacklength
            self.separationcan.segmentNumber = self.rotor.poleNumber
            self.housing.segmentNumber = self.rotor.poleNumber
            self.shaft.segmentNumber = self.stator.slotNumber
            self.band.outerDiameter = self.housing.outerDiameter * 1.01
            self.band.innerDiameter = self.rotor.innerDiameter - \
                (self.rotor.innerDiameter - self.stator.outerDiameter) / 2.0
            self.innerRegion = ring(segmentNumber=self.rotor.poleNumber)
            self.innerRegion.outerDiameter = self.housing.outerDiameter * 1.005
            self.innerRegion.innerDiameter = self.rotor.innerDiameter - \
                (self.rotor.innerDiameter - self.stator.outerDiameter) / 3.0
            self.housing.axialMisalignment = self.rotor.axialMisalignment

        else:
            # Inner-Runner
            self.housing.length = self.stator.stacklength
            self.separationcan.segmentNumber = self.stator.slotNumber
            self.housing.segmentNumber = self.stator.slotNumber
            self.shaft.segmentNumber = self.rotor.poleNumber
            self.band.segmentNumber = self.rotor.poleNumber
            self.band.outerDiameter = self.rotor.outerDiameter + \
                (self.stator.innerDiameter - self.rotor.outerDiameter) / 4.0
            self.innerRegion.outerDiameter = self.rotor.outerDiameter + \
                (self.band.outerDiameter - self.rotor.outerDiameter) / 2.0

        if recomputeGeometry == True:
            self.stator.geometry = statorGeometry.geometry(
                stator=self.stator, winding=self.winding)
            self.winding.getWireCoordinates()
            self.stator.geometry.setSVG()
            self.stator.setArea()
            self.stator.sector.slot.setArea()
            # self.stator.geometry.saveTemp()
            self.stator.geometry.closeDocument()

            self.rotor.geometry = rotorGeometry.geometry(rotor=self.rotor)
            self.rotor.geometry.setSVG()
            self.rotor.setArea()
            self.rotor.pole.pockets[0].magnet.setArea()
            # self.rotor.geometry.saveTemp()
            self.rotor.geometry.closeDocument()

            self.housing.geometry = ringGeometry.geometry(
                ring=self.housing, partName="Housing")
            self.housing.geometry.setSVG()
            self.housing.geometry.closeDocument()

            self.shaft.geometry = pieGeometry.geometry(
                pie=self.shaft, partName="Shaft")
            self.shaft.geometry.setSVG()
            self.shaft.geometry.closeDocument()

            self.separationcan.geometry = ringGeometry.geometry(
                ring=self.separationcan, partName="Separation-Can")
            self.separationcan.geometry.setSVG()
            self.separationcan.geometry.closeDocument()

            self.geometry = self.setGeometry()

            print("initialPosition", self.initialPosition)

    @property
    def idealOverhang(self):
        """Calculates the ideal overhan (%)"""
        return round(100 * (self.rotor.stacklength - self.stator.stacklength) / self.stator.stacklength, 3)

    @property
    def effectiveOverhang(self):
        """Calculates the ideal overhan (%)"""
        leftLimit = -self.rotor.stacklength / 2 + self.rotor.axialMisalignment
        rightLimit = self.rotor.stacklength / 2 + self.rotor.axialMisalignment

        if leftLimit < -self.stator.stacklength / 2 or rightLimit > self.stator.stacklength / 2.0:
            # One of the rotor edges lies outside of the stator
            if self.rotor.axialMisalignment >= 0:
                # Move to right
                return round(100 * (self.rotor.stacklength - self.rotor.axialMisalignment - self.stator.stacklength) / self.stator.stacklength, 3)
            else:
                # Move to left
                return round(100 * (self.rotor.stacklength + self.rotor.axialMisalignment - self.stator.stacklength) / self.stator.stacklength, 3)
        else:
            # Rotor is within the stator limits. Axial misalignment has no effect on the effective overhang!
            return round(100 * (self.rotor.stacklength - self.stator.stacklength) / self.stator.stacklength, 3)

    @property
    def overlapping(self):
        """Calculates the overlapping between stator and rotor (mm)"""
        leftLimit = -self.rotor.stacklength / 2 + self.rotor.axialMisalignment
        rightLimit = self.rotor.stacklength / 2 + self.rotor.axialMisalignment

        if leftLimit <= -self.stator.stacklength / 2 and rightLimit >= self.stator.stacklength / 2:
            # Rotor is outside the stator limits. Stator and rotor overlapp only on stator length
            return self.stator.stacklength
        elif (leftLimit > -self.stator.stacklength / 2 and rightLimit < self.stator.stacklength / 2):
            # Rotor is within the stator limits. Stator and rotor overlapp only on rotor length
            return self.rotor.stacklength
        elif leftLimit <= -self.stator.stacklength / 2 and rightLimit < self.stator.stacklength / 2:
            return rightLimit + self.stator.stacklength / 2
        else:
            return abs(leftLimit - self.stator.stacklength / 2)

    def __getReferentCoil1Angle(self):
        """At this angle rotor alignes with the first coil of phase A.
        In case of single tooth winding (coilSpan==1) it is always the first tooth.

        In case of distributed winding the position is calculated based on the winding scheme.
        """
        angleSlot1 = self.stator.segmentAngle / 2
        angleSlot2 = angleSlot1 + self.winding.coilSpan * self.stator.segmentAngle

        # print(angleSlot1, angleSlot2)
        return (angleSlot1 + angleSlot2) / 2

    @property
    def initialPosition(self):
        """Calculates the initial position of the rotor so that the flux in phaseA is at maxumum (deg)."""
        table = self.winding.layout.getConnectionTable()["table"]
        phaseAngle_el = 0.0

        for raw in table:
            if raw["phase"] == "A":
                phaseAngle_el += raw["angle"] / self.winding.coilsPerPhase

        relativePhaseAngleDisplacementMech = phaseAngle_el / \
            (self.rotor.poleNumber / 2.0)

        wantedPolePosition = self.__getReferentCoil1Angle() + \
            relativePhaseAngleDisplacementMech

        if self.rotor.type == rotorType.rotor3:
            currentPolePosition = self.rotor.segmentAngle
        else:
            currentPolePosition = self.rotor.segmentAngle / 2.0

        return wantedPolePosition - currentPolePosition

    @property
    def symmetryNumber(self):
        """Calculates the symmetry number of the machine."""
        if self.useSymmetry:
            return math.gcd(self.rotor.poleNumber, self.stator.slotNumber)
        else:
            return 1

    @property
    def isBalanced(self):
        """ Calculates if the combination of the pole number, slot number and winding number is possible. """
        if self.winding.phaseOffset != None:
            return True
        else:
            return False

    def applyTemperature(self, temperature=25):
        """Applies the ambient temperature to all parts."""
        self.stator.material.temperature = temperature
        self.rotor.material.temperature = temperature
        self.housing.material.temperature = temperature
        self.separationcan.material.temperature = temperature
        self.winding.coil.wire.material.temperature = temperature
        # self.controlcircuit.temperature = temperature

        for pocket in self.rotor.pole.pockets:
            pocket.magnet.material.temperature = temperature

    def getCADGeometryData(self):
        # statorDXFs = self.stator.geometry.getDXFs()
        # rotorDXFs = self.rotor.geometry.getDXFs()
        # shaftDXFs = self.shaft.geometry.getDXFs()
        # sepCanDXFs = self.separationcan.geometry.getDXFs()
        # housingDXFs = self.housing.geometry.getDXFs()

        statorSTEPs = self.stator.geometry.getSTEPs()
        rotorSTEPs = self.rotor.geometry.getSTEPs()
        shaftSTEPs = self.shaft.geometry.getSTEPs()
        sepCanSTEPs = self.separationcan.geometry.getSTEPs()
        housingSTEPs = self.housing.geometry.getSTEPs()

        output = {
            "Stator_Segment": {"DXF": None, "STEP": statorSTEPs["Stator Segment"]},
            "Spoke_Closing_Bridge": {"DXF": None, "STEP": statorSTEPs["Spoke Closing Bridge"]},
            "Spoke_Left_Connection": {"DXF": None, "STEP": statorSTEPs["Spoke Left Connection"]},
            "Spoke_Right_Connection": {"DXF": None, "STEP": statorSTEPs["Spoke Right Connection"]},
            "Rotor_Segment": {"DXF": None, "STEP": rotorSTEPs["Rotor Segment"]},
            "Shaft_Segment": {"DXF": None, "STEP": shaftSTEPs["Shaft Segment"]},
            "Terminal_Left": {"DXF": None, "STEP": statorSTEPs["Terminal Left"]},
            "Terminal_Right": {"DXF": None, "STEP": statorSTEPs["Terminal Right"]},
            "Tooth_Line": {"DXF": None, "STEP": statorSTEPs["Tooth Line"]},
            "Yoke_Line": {"DXF": None, "STEP": statorSTEPs["Yoke Line"]},
            "Separation_Can_Segment": {"DXF": None, "STEP": sepCanSTEPs["Separation-Can Segment"] if self.separationcan.useInModel else None},
            "Housing_Segment": {"DXF": None, "STEP": housingSTEPs["Housing Segment"]},
        }

        # "Magnet Segment" has been changed to array. v-rotor has two magnets per pole

        if len(rotorSTEPs["Magnet Segment"]) == 1:
            output["Magnet_Segment"] = {"DXF": None,
                                        "STEP": rotorSTEPs["Magnet Segment"][0]}
        if len(rotorSTEPs["Magnet Segment"]) == 2:
            output["Magnet_Left_Segment"] = {
                "DXF": None, "STEP": rotorSTEPs["Magnet Segment"][0]}
            output["Magnet_Right_Segment"] = {
                "DXF": None, "STEP": rotorSTEPs["Magnet Segment"][1]}

        # for index, magnetSegment in enumerate(rotorSTEPs["Magnet Segment"]):
        #     output["Magnet_Segment_%s" %
        #            (index)] = {"DXF": None, "STEP": magnetSegment}

        # if rotorDXFs["Pocket Segment"] != None:
        #     output["Pocket Segment"] = {"DXF": rotorDXFs["Pocket Segment"]}

        return output

    def setGeometry(self):
        return {
            "SVG": {
                "Top View": svg.mergeSVGs([
                    self.housing.geometry.svg["Top View"],
                    self.stator.geometry.svg["Top View"],
                    self.rotor.geometry.svg["Top View"],
                    self.shaft.geometry.svg["Top View"],
                    self.separationcan.geometry.svg["Top View"] if self.separationcan.useInModel else None
                ]),
                "Side View": svg.mergeSVGs([
                    self.shaft.geometry.svg["Side View"],
                    self.housing.geometry.svg["Side View"],
                    self.stator.geometry.svg["Side View"],
                    self.rotor.geometry.svg["Side View"],
                    self.separationcan.geometry.svg["Side View"] if self.separationcan.useInModel else None
                ]),
                "Winding View": svg.mergeSVGs([
                    self.stator.geometry.svg["Winding View"],
                ])
            },
        }

    def readJSON(self, data):
        """ Reads the JSON data and assigns the instance variables. """
        if "Stator" in data:
            self.stator = stator(data=data["Stator"])
        if "Rotor" in data:
            self.rotor = rotor(data=data["Rotor"])
        if "Housing" in data:
            self.housing = ring(
                data=data["Housing"], segmentNumber=self.stator.slotNumber, partName="Housing")
        if "Shaft" in data:
            self.shaft = pie(
                data=data["Shaft"], segmentNumber=self.rotor.poleNumber, partName="Shaft")
        if "Separation Can" in data:
            self.separationcan = ring(
                data=data["Separation Can"], segmentNumber=self.stator.slotNumber, partName="Separation-Can")
        if "Winding" in data:
            self.winding = winding(
                self.stator, self.rotor, data=data["Winding"])
        if "Control Circuit" in data:
            self.controlcircuit = controlcircuit(data["Control Circuit"])
        if "Nameplate" in data:
            self.nameplate = data["Nameplate"]
        if "Environment" in data:
            self.environment = environment(data=data["Environment"])
        if "Mechanics" in data:
            self.mechanics = mechanics(data=data["Mechanics"])
        if "Use Symmetry" in data:
            self.useSymmetry = float(data["Use Symmetry"])
        if "Consider Stamping Effects" in data:
            self.considerStampingEffects = float(
                data["Consider Stamping Effects"])
        if "Permeability Reduction (%)" in data:
            self.permeabilityReduction = float(
                data["Permeability Reduction (%)"])
        if "Cutting Thickness (mm)" in data:
            self.cuttingThickness = float(data["Cutting Thickness (mm)"])
        if "Magnetization Losses Increase (%)" in data:
            self.magnetizationLossesIncrease = float(
                data["Magnetization Losses Increase (%)"])
        if "Geometry" in data:
            self.geometry = data["Geometry"]

    def reprJSON(self):
        """ Creates json representation of the object. """
        newObject = {
            "Stator": self.stator,
            "Rotor": self.rotor,
            "Housing": self.housing,
            "Shaft": self.shaft,
            "Separation Can": self.separationcan,
            "Winding": self.winding,
            "Control Circuit": self.controlcircuit,
            "Environment": self.environment,
            "Mechanics": self.mechanics,
            "Use Symmetry": self.useSymmetry,
            "Ideal Overhang (%)": self.idealOverhang,
            "Effective Overhang (%)": self.effectiveOverhang,
            "Initial Position (deg)": self.initialPosition,
            "Overlapping (mm)": self.overlapping,
            "Symmetry Number": self.symmetryNumber,
            "Region": self.region,
            "Band": self.band,
            "Inner Region": self.innerRegion,
            "Geometry": self.geometry,
            "Weight": {
                "Stator (kg)": self.stator.getWeight(),
                "Rotor (kg)": self.rotor.getWeight(),
                "Magnets (kg)": self.rotor.pole.pockets[0].magnet.getWeight() * self.rotor.poleNumber,
                "Winding (kg)": self.winding.getWeight()
            },
            "Modelica Parameters": {
                "ke (V*s/rad)": {
                    "value": self.nameplate.get("ke (V*s/rad)", None) if self.nameplate else None,
                    "info": "Phase peak value"
                },
                "Phase Resistance (Ohm)": self.nameplate.get("Resistance (Ohm)", None) if self.nameplate else None,
                "Ld (H)": self.nameplate.get("Ld (H)", None) if self.nameplate else None,
                "Lq (H)": self.nameplate.get("Lq (H)", None) if self.nameplate else None,
                "Winding Connection": self.winding.phaseConnection["name"],
                "Stator Volume (m3)": self.stator.volume * 1e-9,
                "Rotor Volume (m3)": self.rotor.volume * 1e-9,
                "Btooth (T)": self.nameplate.get("Btooth (T)", None) if self.nameplate else None,
                "Byoke (T)": self.nameplate.get("Byoke (T)", None) if self.nameplate else None,
            }
        }

        # Nameplate values only when scaling in Motor studio analytic. Make name plate also for MSN!!!
        return json.loads(json.dumps(newObject, cls=ComplexEncoder, indent=3))
