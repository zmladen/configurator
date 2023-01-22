from motorStudio.enums import *
from materials import *
from motorStudio.virtualTests import *


class ansysMaterials:
    """Class ansysmat. It contains the methods to define materials that are used for the calculation."""

    def __init__(self, oDesktop, machine=None, geometries=None, virtualTest=None):
        """Constructor for the bldc machine object with the needed parametersself.
        :param machine type: machine."""
        self.machine = machine
        self.geometries = geometries
        self.reducedMaterialMark = "*"
        self.oDesktop = oDesktop
        self.virtualTest = virtualTest

    def assignAll(self, oProject, temperature):
        """Assignes all materials to parts.
        :param oProject type: AnsysAPI."""
        oDesign = oProject.GetActiveDesign()
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        # for part in oEditor.GetMatchedObjectName("%s*"%(self.geometries.partNames["Rotor Cutting"])):
        #     self.__assignMaterialToPart(oEditor, part, metal(data=self.machine["design"]["Rotor"]["Material"], temperature=temperature), reduced=True)

        # print("GetMatchedObjectName", oEditor.GetMatchedObjectName(
        #     "%s*" % (self.geometries.partNames["Magnets"])))

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Spoke Closing Bridge"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Stator"]["Material"], temperature=temperature), reduced=True)

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Spoke Left Connection"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Stator"]["Material"], temperature=temperature), reduced=True)

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Spoke Right Connection"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Stator"]["Material"], temperature=temperature), reduced=True)

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Stator"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Stator"]["Material"], temperature=temperature))

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Rotor"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Rotor"]["Material"], temperature=temperature))

        for magnetPart in self.geometries.partNames["Magnets"]:
            for part in oEditor.GetMatchedObjectName("%s*" % (magnetPart)):
                self.__assignMaterialToPart(oEditor, part, magnet(
                    data=self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Material"], temperature=temperature))

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Housing"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Housing"]["Material"], temperature=temperature))

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Separation-Can"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Separation Can"]["Material"], temperature=temperature))

        for part in oEditor.GetMatchedObjectName("%s*" % (self.geometries.partNames["Shaft"])):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Shaft"]["Material"], temperature=temperature))

        for part in oEditor.GetMatchedObjectName("Phase*"):
            self.__assignMaterialToPart(oEditor, part, metal(
                data=self.machine["design"]["Winding"]["Coil"]["Wire"]["Material"], temperature=temperature))

    def createAll(self, oProject, temperature):
        """Creates all materials necessary for the calculation."""
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Stator"]["Material"], temperature=temperature))
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Rotor"]["Material"], temperature=temperature))
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Stator"]["Material"], temperature=temperature), reduced=True)
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Rotor"]["Material"], temperature=temperature), reduced=True)
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Shaft"]["Material"], temperature=temperature))
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Separation Can"]["Material"], temperature=temperature))
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Winding"]["Coil"]["Wire"]["Material"], temperature=temperature))
        self.__createMetal(oProject, metal(
            data=self.machine["design"]["Housing"]["Material"], temperature=temperature))

        if type(self.virtualTest) == type(demagnetization()):
            self.__createMagnet(oProject, magnet(isLinear=False,
                                                 data=self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Material"], temperature=temperature))
        else:
            self.__createMagnet(oProject, magnet(
                data=self.machine["design"]["Rotor"]["Pole"]["Pockets"][0]["Magnet"]["Material"], temperature=temperature))

    def __assignMaterialToPart(self, oEditor, part, material, reduced=False):
        """ Assignes the material to the object. """

        if material == None or material.name == "vacuum" or material.name == "Vacuum":
            materialName = "vacuum"
        else:
            materialName = material.infoName

            if reduced:
                materialName += self.reducedMaterialMark

        oEditor.AssignMaterial(["NAME:Selections", "AllowRegionDependentPartSelectionForPMLCreation:=", True, "AllowRegionSelectionForPMLCreation:=", True, "Selections:=", part],
                               ["NAME:Attributes", "MaterialValue:=", "\"%s\"" % (materialName), "SolveInside:=", True, "IsMaterialEditable:=", True, "UseMaterialAppearance:=", False])

    def __createMagnet(self, oProject, material):
        """Creates the permanent magnet material."""
        poleNumber = self.machine["design"]["Rotor"]["Pole Number"]

        if material != None and material.name != "vacuum" and material.name != "Vacuum":
            oDefinitionManager = oProject.GetDefinitionManager()
            core_loss_type = [
                "NAME:core_loss_type", "property_type:=", "ChoiceProperty", "Choice:=", "None"]

            if self.machine["design"]["Rotor"]["Magnetization Type"] == "diametral":
                CSType = "Cartesian"
            else:
                CSType = "Cylindrical"

            if self.machine["design"]["Rotor"]["Magnetization Type"] == "lateral":
                magnitude = str(material.hcb) + "*" + str(1 + self.machine["design"]["Effective Overhang (%)"] / 100.0) + " * exp((-" + str(poleNumber) + " ** 2 / " + str(self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 2.0) + \
                    "mm" + " ** 2" + " / 16) * ((" + str(
                        self.machine["design"]["Rotor"]["Outer Diameter (mm)"] / 2.0) + "mm" + " - R) ** 2))"
                matProperties = ["NAME:" + material.infoName, "CoordinateSystemType:=", CSType,
                                 "BulkOrSurfaceType:=", 1, [
                                     "NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                                 ["NAME:magnetic_coercivity", "property_type:=", "VectorProperty",
                                  "Magnitude:=", magnitude + "A_per_meter",
                                  "DirComp1:=", "sin(" +
                                  str(poleNumber / 2.0) + " * Phi)",
                                  "DirComp2:=", "cos(" +
                                  str(poleNumber / 2.0) + " * Phi)",
                                  "DirComp3:=", "0"],
                                 core_loss_type, "conductivity:=", str(1.0 / material.resistivity),  "mass_density:=", str(material.density)]

            else:
                matProperties = ["NAME:" + material.infoName, "CoordinateSystemType:=", CSType,
                                 "BulkOrSurfaceType:=", 1, [
                                     "NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                                 ["NAME:magnetic_coercivity", "property_type:=", "VectorProperty",
                                  "Magnitude:=", str(material.hcb) + "*" + str(
                                      1 + self.machine["design"]["Effective Overhang (%)"] / 100) + "A_per_meter",
                                  "DirComp1:=", "1 * sgn(X)" if self.machine["design"]["Rotor"][
                                      "Magnetization Type"] == "radial" else "1",
                                  "DirComp2:=", "0",
                                  "DirComp3:=", "0"],
                                 core_loss_type, "conductivity:=", str(1.0 / material.resistivity),  "mass_density:=", str(material.density)]

            if (material.isLinear == True):
                matProperties.append("permeability:=")
                matProperties.append(str(material.ur))
            else:
                curves = material.getDemagnetizationCurve()
                matProperties.append(["NAME:permeability", "property_type:=", "nonlinear", "BType:=", "intrinsic",
                                     "HUnit:=", "A_per_meter", "BUnit:=", "tesla", self.__makeBHArray(curves["J (T)"], curves["H (A/m)"])])

            if(oDefinitionManager.DoesMaterialExist(material.infoName)):
                oDefinitionManager.EditMaterial(
                    material.infoName, matProperties)
            else:
                oDefinitionManager.AddMaterial(matProperties)

    def __createMetal(self, oProject, material, reduced=False):
        """Creates the metal material."""

        if material != None and material.name != "vacuum" and material.name != "Vacuum":
            oDefinitionManager = oProject.GetDefinitionManager()

            if(material.magnLosses == True):
                core_loss_type = ["NAME:core_loss_type", "property_type:=",
                                  "ChoiceProperty", "Choice:=", "Electrical Steel"]
            else:
                core_loss_type = [
                    "NAME:core_loss_type", "property_type:=", "ChoiceProperty", "Choice:=", "None"]

            materialName = material.infoName
            if reduced:
                materialName += self.reducedMaterialMark

            matProperties = ["NAME:" + materialName, "CoordinateSystemType:=", "Cartesian", "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                             ["NAME:magnetic_coercivity", "property_type:=", "VectorProperty", "Magnitude:=",
                                 "0A_per_meter", "DirComp1:=", "1", "DirComp2:=", "0", "DirComp3:=", "0"],
                             core_loss_type,
                             "conductivity:=", str(
                                 1.0 / material.resistivity),      # S/m
                             "core_loss_kh:=", str(material.kh),      # w/m^3
                             "core_loss_kc:=", str(material.ke),      # w/m^3
                             "core_loss_ke:=", str(material.ka),      # w/m^3
                             "core_loss_kdc:=", str(material.kdc),     # w/m^3
                             "mass_density:=", str(
                                 material.density),      # kg/m^3
                             "core_loss_equiv_cut_depth:=", str(
                                 material.cut_depth)  # mm
                             ]

            if material.linear:
                if reduced:
                    matProperties.append("permeability:=")
                    matProperties.append(str(material.ur_max))
                else:
                    matProperties.append("permeability:=")
                    matProperties.append(str(material.ur_max_red))

            else:
                # print(materialName)
                # print(material.b_sf)
                # print(material.h)
                # print(material.permeability)
                # print(material.h_red)

                if reduced:
                    # print("Here1")
                    matProperties.append(["NAME:permeability", "property_type:=", "nonlinear", "BType:=", "normal",
                                         "HUnit:=", "A_per_meter", "BUnit:=", "tesla", self.__makeBHArray(material.b_sf, material.h_red)])
                else:
                    matProperties.append(["NAME:permeability", "property_type:=", "nonlinear", "BType:=", "normal",
                                         "HUnit:=", "A_per_meter", "BUnit:=", "tesla", self.__makeBHArray(material.b_sf, material.h)])

            if(oDefinitionManager.DoesMaterialExist(materialName)):
                oDefinitionManager.EditMaterial(materialName, matProperties)
            else:
                oDefinitionManager.AddMaterial(matProperties)

    def __makeBHArray(self, B, H):
        bh = ["NAME:BHCoordinates"]
        for i in range(len(H)):
            bh.append(["NAME:Coordinate", "X:=", H[i], "Y:=", B[i]])
        return bh
