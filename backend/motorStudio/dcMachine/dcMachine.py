import json
from utils import *
from fractions import gcd
from ..enums import *
from ..common.mechanics import *
from ..common.environment import *
from ..common.ring import *
from ..common.pie import *
from .stator import *
from .rotor import *
from .commutationSystem import *
from .winding import *
from utils import svg
from .rotor.geometry import geometry as rotorGeometry
from .stator.geometry import geometry as statorGeometry
from .commutationSystem.geometry import geometry as commutationSystemGeometry
from ..common.ring.geometry import geometry as ringGeometry
from ..common.pie.geometry import geometry as pieGeometry


class dcMachine(object):
    """This is a geometry class. It is used as a container for all other modules / classes necessary to define the drive geometry.
    :param dict data: JSON dictionary used for the object initialization. Default value is empty string."""

    def __init__(self, data={}, recomputeGeometry=True):
        """ Constructor for the bldc machine object with the needed parameters """
        self.type = machineType.dcInnerRunner
        self.useSymmetry = True
        self.considerStampingEffects = False
        self.permeabilityReductionFactor = 1
        self.lossesIncreaseFactor = 1
        self.cuttingThickness = 0.1
        self.stator = stator(statorType.stator7)
        self.rotor = rotor(rotorType.rotor8)
        self.housing = ring(segmentNumber=self.stator.slotNumber)
        self.shaft = pie(segmentNumber=self.rotor.poleNumber)
        self.innerRegion = pie(segmentNumber=self.rotor.poleNumber)
        self.region = pie(segmentNumber=self.stator.slotNumber)
        self.band = pie(segmentNumber=self.rotor.poleNumber)
        self.nameplate = None
        self.environment = environment()
        self.mechanics = mechanics()
        self.winding = winding(self.stator, self.rotor,
                               symmetryNumber=self.symmetryNumber)
        self.commutationSystem = commutationSystem(winding=self.winding)
        self.geometry = None

        if not data == {}:
            self.readJSON(data["design"])

        if recomputeGeometry == True:
            self.stator.geometry = statorGeometry.geometry(
                stator=self.stator, winding=self.winding)
            # self.winding.coil.setSlotCentroid()
            self.winding.getWireCoordinates()
            self.stator.geometry.setSVG()
            self.stator.setArea()
            self.stator.sector.slot.setArea()

            # print(self.winding.coil.slotCentroid,
            #       self.winding.coil.slotCentroid1)
            # self.stator.geometry.saveTemp()
            # self.stator.geometry.closeDocument()

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

            self.commutationSystem.geometry = commutationSystemGeometry.geometry(
                commutationSystem=self.commutationSystem)
            self.commutationSystem.geometry.setSVG()
            self.commutationSystem.geometry.closeDocument()

            self.geometry = self.setGeometry()

        # self.innerRegion.symmetryNumber = self.rotor.poleNumber
        # self.region.symmetryNumber = self.stator.slotNumber
        # self.region.outerDiameter = self.housing.outerDiameter * 1.1
        #
        # if (self.type == machineType.dcInnerRunner):
        #     self.band = ring(symmetryNumber=self.rotor.poleNumber)
        #     self.housing.symmetryNumber = self.rotor.poleNumber
        #     self.shaft.symmetryNumber = self.stator.slotNumber
        #     self.band.outerDiameter = self.housing.outerDiameter * 1.01
        #     self.band.innerDiameter = self.rotor.innerDiameter - (self.rotor.innerDiameter - self.stator.outerDiameter) / 6.0
        #     self.innerRegion = ring(symmetryNumber=self.rotor.poleNumber)
        #     self.innerRegion.outerDiameter = self.housing.outerDiameter * 1.005
        #     self.innerRegion.innerDiameter = self.rotor.innerDiameter - (self.rotor.innerDiameter - self.stator.outerDiameter) / 8.0
        #
        # self.innerRegion.color = "#fdfdfd"
        # self.region.color = "#fdfdfd"
        # self.band.color = "#fdfdfd"
        # self.housing.color = "#CC99C9"
        # self.shaft.color = "#FF6663"
        # self.rotor.pole.color = "#393f8c"
        # self.stator.sector.color = "#393f8c"

    @property
    def initialPosition(self):
        return 0

    @property
    def symmetryNumber(self):
        """Calculates the symmetry number of the machine."""
        if self.useSymmetry:
            return gcd(self.rotor.poleNumber, self.stator.slotNumber)
        else:
            return 1

    def applyTemperature(self, temperature=25):
        """Applies the ambient temperature to all parts."""
        self.stator.material.temperature = temperature
        self.rotor.material.temperature = temperature
        self.housing.material.temperature = temperature
        self.winding.coil.wire.material.temperature = temperature
        self.commutationSystem.temperature = temperature
        self.commutationSystem.applyTemperature(temperature)
        for pocket in self.rotor.pole.pockets:
            pocket.magnet.material.temperature = temperature

    def getGeometryData(self):
        statorDXFs = self.stator.geometry.getDXFs()
        rotorDXFs = self.rotor.geometry.getDXFs()
        shaftDXFs = self.shaft.geometry.getDXFs()

        return {
            "Stator Segment": {
                "DXF": statorDXFs["Stator Segment"]
            },
            "Rotor Segment": {
                "DXF": rotorDXFs["Rotor Segment"]
            },
            "Magnet Segment": {
                "DXF": rotorDXFs["Magnet Segment"]
            },
            "Shaft Segment": {
                "DXF": shaftDXFs["Shaft Segment"]
            }
        }

    def getCADGeometryData(self):
        # statorDXFs = self.stator.geometry.getDXFs()
        # rotorDXFs = self.rotor.geometry.getDXFs()
        # shaftDXFs = self.shaft.geometry.getDXFs()
        # housingDXFs = self.housing.geometry.getDXFs()

        statorSTEPs = self.stator.geometry.getSTEPs()
        rotorSTEPs = self.rotor.geometry.getSTEPs()
        shaftSTEPs = self.shaft.geometry.getSTEPs()
        housingSTEPs = self.housing.geometry.getSTEPs()

        output = {
            "Stator_Segment": {"DXF": None, "STEP": statorSTEPs["Stator Segment"]},
            "Rotor_Segment": {"DXF": None, "STEP": rotorSTEPs["Rotor Segment"]},
            "Magnet_Segment": {"DXF": None, "STEP": rotorSTEPs["Magnet Segment"]},
            "Shaft_Segment": {"DXF": None, "STEP": shaftSTEPs["Shaft Segment"]},
            "Terminal": {"DXF": None, "STEP": statorSTEPs["Terminal"]},
            "Tooth_Line": {"DXF": None, "STEP": statorSTEPs["Tooth Line"]},
            "Yoke_Line": {"DXF": None, "STEP": statorSTEPs["Yoke Line"]},
            "Housing_Segment": {"DXF": None, "STEP": housingSTEPs["Housing Segment"]},
        }

        return output

    def setGeometry(self):
        return {
            "SVG": {
                "Top View": svg.mergeSVGs([
                    self.housing.geometry.svg["Top View"],
                    self.stator.geometry.svg["Top View"],
                    self.rotor.geometry.svg["Top View"],
                    self.shaft.geometry.svg["Top View"],
                    self.commutationSystem.geometry.svg["Top View"],
                    # self.separationcan.geometry.svg["Top View"] if self.separationcan.useInModel else None
                ]),
                "Side View": svg.mergeSVGs([
                    self.shaft.geometry.svg["Side View"],
                    self.housing.geometry.svg["Side View"],
                    self.stator.geometry.svg["Side View"],
                    self.rotor.geometry.svg["Side View"],
                    self.commutationSystem.geometry.svg["Side View"],
                    # self.separationcan.geometry.svg["Side View"] if self.separationcan.useInModel else None
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
            self.innerStator = stator(data=data["Stator"])
        if "Rotor" in data:
            self.rotor = rotor(data=data["Rotor"])
            self.innerRotor = rotor(data=data["Rotor"])
        if "Housing" in data:
            self.housing = ring(
                data=data["Housing"], segmentNumber=self.stator.slotNumber)
        if "Shaft" in data:
            self.shaft = pie(data=data["Shaft"],
                             segmentNumber=self.stator.slotNumber)
        if "Winding" in data:
            self.winding = winding(
                self.stator, self.rotor, data=data["Winding"])
        if "Commutation System" in data:
            self.commutationSystem = commutationSystem(
                data=data["Commutation System"], winding=self.winding)
        if "Nameplate" in data:
            self.nameplate = data["Nameplate"]
        if "Environment" in data:
            self.environment = environment(data=data["Environment"])
        if "Mechanics" in data:
            self.mechanics = mechanics(data=data["Mechanics"])
        if "Use Symmetry" in data:
            self.useSymmetry = float(data["Use Symmetry"])

    def reprJSON(self):
        """ Creates json representation of the object. """

        newObject = {
            "Inner Stator": self.innerStator,
            "Stator": self.stator,
            "Rotor": self.rotor,
            "Housing": self.housing,
            "Shaft": self.shaft,
            "Winding": self.winding,
            "Mechanics": self.mechanics,
            "Environment": self.environment,
            "Symmetry Number": self.symmetryNumber,
            "Use Symmetry": self.useSymmetry,
            "Region": self.region,
            "Inner Region": self.innerRegion,
            "Band": self.band,
            "Commutation System": self.commutationSystem,
            "Weight": {
                "Stator (kg)": 0,  # self.stator.getWeight(),
                "Rotor (kg)": 0,  # self.rotor.getWeight(),
                "Magnets (kg)": 0,  # self.rotor.getMagnetsWeight(),
                "Winding (kg)": 0,  # self.winding.getWeight(),
                "Housing (kg)": self.housing.getWeight(),
                "Separation Can (kg)": 0,  # self.separationcan.getWeight(),
                "Shaft (kg)": 0,  # self.shaft.getWeight(),
                "Total (kg)": 0  # self.stator.getWeight() + variation.rotor.getWeight() + variation.rotor.getMagnetsWeight() + variation.winding.getWeight() + variation.housing.getWeight() + variation.separationcan.getWeight() + variation.shaft.getWeight()
            },
            "Geometry": self.geometry,
        }

        return json.loads(json.dumps(newObject, cls=ComplexEncoder, indent=3))
