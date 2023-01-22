import math
import json
import numpy as np
from scipy import interpolate
from .serializers import *
from .functions import *
import matplotlib.pyplot as plt

DEG2RAD = math.pi / 180
RAD2DEG = 180 / math.pi


def ke(cn_EMF, refSpeed, position, initangle, phaseadvance):
    # 0 - Real, 1 - Imaginary
    # a0 = 2.0 * self.cn_EMF[0][0]
    Ampl, ii = 0, 1
    delta = (initangle - phaseadvance) * DEG2RAD
    position = position * DEG2RAD
    for ii in range(1, len(cn_EMF)):
        an = 2.0 * cn_EMF[ii]["real"]
        bn = -2.0 * cn_EMF[ii]["imag"]
        Ampl += an * math.cos(ii * position + ii * delta) + \
            bn * math.sin(ii * position + ii * delta)

    return 30 * Ampl / (math.pi * refSpeed)


def ke60degAverage(cn_EMF, refSpeed, initangle, phaseadvance):
    positions = np.linspace(60, 120, 60)
    sum = 0
    for position in positions:
        sum += ke(cn_EMF, refSpeed, position, 0, phaseadvance)
    return sum / positions.size


def _Ea(cn_EMF, refSpeed, angleCorrection, poleNumber, angleMech):
    angleEl = (poleNumber / 2) * angleMech
    return (math.pi * refSpeed / 30) * ke(cn_EMF, refSpeed, angleEl, 0, angleCorrection)


def _Eb(cn_EMF, refSpeed, angleCorrection, poleNumber, angleMech):
    angleEl = (poleNumber / 2) * angleMech
    return (math.pi * refSpeed / 30) * ke(cn_EMF, refSpeed, angleEl, -120, angleCorrection)


def _Ec(cn_EMF, refSpeed, angleCorrection, poleNumber, angleMech):
    angleEl = (poleNumber / 2) * angleMech
    return (math.pi * refSpeed / 30) * ke(cn_EMF, refSpeed, angleEl, -240, angleCorrection)


def applyScalingLaws(variation, reference, settings):
    """Material and temperature factors are the same."""
    variation.applyTemperature(
        temperature=variation.environment.ambientTemperature)
    airgapCorrectionFactor = 1

    windingRatio = variation.winding.coil.usedWindingNumber / \
        reference.winding.coil.usedWindingNumber
    lengthRatio = variation.stator.stacklength / reference.stator.stacklength
    wireGaugeRatio = 1.0 / \
        math.pow(variation.winding.coil.wire.gauge["Conductor Diameter (mm)"] /
                 reference.winding.coil.wire.gauge["Conductor Diameter (mm)"], 2)
    wireStrechingRatio = 1.0 / math.pow((1 - variation.winding.coil.wireStreching / 100) / (
        1 - reference.winding.coil.wireStreching / 100), 2)
    multipleWiresRatio = 1.0 / \
        (variation.winding.coil.numberOfMultipleWires /
         reference.winding.coil.numberOfMultipleWires)
    magnetTempMatFactor = variation.rotor.pole.pockets[0].magnet.material.br / \
        reference.rotor.pole.pockets[0].magnet.material.br
    wireTempMatFactor = variation.winding.coil.wire.material.resistivity / \
        reference.winding.coil.wire.material.resistivity
    overhangRef = reference.effectiveOverhang
    overhang = variation.effectiveOverhang
    idealOverhang = variation.idealOverhang
    # overhangRef = 100 * float(reference.rotor.stacklength - reference.rotor.axialMisalignment - reference.stator.stacklength) / reference.stator.stacklength
    # overhang = 100 * float(variation.rotor.stacklength - variation.rotor.axialMisalignment - variation.stator.stacklength) / variation.stator.stacklength
    # idealOverhang = 100 * float(variation.rotor.stacklength - variation.stator.stacklength) / variation.stator.stacklength

    if reference.winding.cableResistance > 0:
        resistanceFactorCable = variation.winding.cableResistance / \
            reference.winding.cableResistance
    else:
        resistanceFactorCable = 1

    resistanceFactor = windingRatio * wireGaugeRatio * \
        wireTempMatFactor * multipleWiresRatio * wireStrechingRatio
    voltageFactor = windingRatio * lengthRatio * airgapCorrectionFactor * \
        magnetTempMatFactor * (1 + overhang / 100) / (1 + overhangRef / 100)
    inductanceFactor = math.pow(windingRatio, 2) * lengthRatio
    fluxDensityFactor = airgapCorrectionFactor * magnetTempMatFactor * \
        (1 + overhang / 100) / (1 + overhangRef / 100)

    coggingFactor = variation.overlapping / \
        reference.overlapping * magnetTempMatFactor

    if (reference.winding.coilConnection["name"] != variation.winding.coilConnection["name"]):
        if variation.winding.coilConnection["name"] == "parallel":
            # Reference is serial, variation is parallel
            voltageFactor = voltageFactor / variation.winding.numberParallelCoils
            resistanceFactor = resistanceFactor / variation.winding.numberParallelCoils ** 2
            inductanceFactor = inductanceFactor / variation.winding.numberParallelCoils ** 2

        else:
            # Reference is parallel, Variation is serial
            voltageFactor = voltageFactor * reference.winding.numberParallelCoils
            resistanceFactor = resistanceFactor * reference.winding.numberParallelCoils ** 2
            inductanceFactor = inductanceFactor * reference.winding.numberParallelCoils ** 2
    else:
        if variation.winding.coilConnection["name"] == "parallel":
            # Reference is parallel, variation is parallel
            voltageFactor = voltageFactor / \
                (variation.winding.numberParallelCoils /
                 reference.winding.numberParallelCoils)
            resistanceFactor = resistanceFactor / \
                (variation.winding.numberParallelCoils /
                 reference.winding.numberParallelCoils) ** 2
            inductanceFactor = inductanceFactor / \
                (variation.winding.numberParallelCoils /
                 reference.winding.numberParallelCoils) ** 2
        else:
            # Reference is serial, Variation is serial
            voltageFactor = voltageFactor
            resistanceFactor = resistanceFactor
            inductanceFactor = inductanceFactor

    earef, ebref, ecref = [], [], []
    earef_terminal, earef_terminal, earef_terminal = [], [], []

    if "Induced Voltage" not in reference.nameplate:
        return reference.nameplate

    refSpeed = reference.nameplate["Induced Voltage"]["speed (rpm)"]

    # Check if only 1 period is calculated. If not take only the first period. FFT Works only if one period is used.
    numberOfPeriods, Na = 1, len(
        reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"])
    if reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"][-1] > 360 / (reference.rotor.poleNumber / 2):
        numberOfPeriods = int(round(reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"][-1] / (
            360 / (reference.rotor.poleNumber / 2))))  # Round to closest integer

    time = [(item * math.pi / 180) / (2 * math.pi * refSpeed / 60)
            for item in variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"][:Na//numberOfPeriods]]

    # Includes effects of: temperature, winding and coil connection! Only delta to star transformation needs to be considerered.

    deltaR_Phase = variation.winding.getPhaseResistanceForAddedLength(
        variation.stator.stacklength - reference.stator.stacklength)
    # print("deltaR_Phase", deltaR_Phase)

    # Connection resistance should not be transformed
    R_conn = variation.winding.getPhaseConnectionResistance()

    # Cable resistance should not be transformed
    R_cable = reference.winding.cableResistance

    if variation.winding.phaseConnection["name"] == "delta":
        # Transform the induced voltage to equivalent star connection.
        # It is neccessary to shift the resulting data by 30deg.el.
        # Angle correction synchronises the signal of the FFT transform with the real data.
        # **************************************************************************************
        cn_EMF_Ref = getFFTCoefficients(
            time, reference.nameplate["Induced Voltage"]["VA"]["VA (V)"][:Na//numberOfPeriods], 25)
        angleCorrection = -30 + \
            reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"][0] * (
                reference.rotor.poleNumber / 2)

        for angle in np.linspace(0, 360 / reference.rotor.poleNumber * 2, Na//2):
            ea = _Ea(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)
            eb = _Eb(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)
            ec = _Ec(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)
            earef.append((ea - ec) / 3)
            ebref.append((eb - ea) / 3)
            ecref.append((ec - eb) / 3)

        variation.nameplate["Resistance (Ohm)"] = (
            (reference.nameplate["Resistance (Ohm)"] - R_conn - R_cable) * resistanceFactor + deltaR_Phase + R_conn) / 3 + R_cable * resistanceFactorCable

        variation.nameplate["Ld (H)"] = reference.nameplate["Ld (H)"] * \
            inductanceFactor / 3
        variation.nameplate["Lq (H)"] = reference.nameplate["Lq (H)"] * \
            inductanceFactor / 3
        # variation.nameplate["ke (V*s/rad)"] = (
        #     reference.nameplate["ke (V*s/rad)"] * voltageFactor) / math.sqrt(3)

    else:

        cn_EMF_Ref = getFFTCoefficients(
            time, reference.nameplate["Induced Voltage"]["VA"]["VA (V)"][:Na//numberOfPeriods], 25)
        angleCorrection = 0 + \
            reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"][0] * (
                reference.rotor.poleNumber / 2)

        for angle in np.linspace(0, 360 / reference.rotor.poleNumber * 2, Na//2):
            ea = _Ea(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)
            eb = _Eb(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)
            ec = _Ec(cn_EMF_Ref, refSpeed, angleCorrection,
                     variation.rotor.poleNumber, angle)

            temp_a = ea - eb
            temp_b = eb - ec
            temp_c = ec - ea

            earef_terminal.append(temp_a)
            earef_terminal.append(temp_b)
            earef_terminal.append(temp_c)

            # Convert back terinal to phase. The same as deta to star!
            earef.append((temp_a - temp_c) / 3)
            ebref.append((temp_b - temp_a) / 3)
            ecref.append((temp_c - temp_b) / 3)

        variation.nameplate["Resistance (Ohm)"] = (
            (reference.nameplate["Resistance (Ohm)"] - R_conn - R_cable) * resistanceFactor) + deltaR_Phase + R_conn + R_cable * resistanceFactorCable

        variation.nameplate["Ld (H)"] = reference.nameplate["Ld (H)"] * \
            inductanceFactor
        variation.nameplate["Lq (H)"] = reference.nameplate["Lq (H)"] * \
            inductanceFactor
        # variation.nameplate["ke (V*s/rad)"] = (
        #     reference.nameplate["ke (V*s/rad)"] * voltageFactor)

        # No transformation needed.
        # To calculate ke use terminal voltage
        #

        # earef = reference.nameplate["Induced Voltage"]["VA"]["VA (V)"]
        # ebref = reference.nameplate["Induced Voltage"]["VB"]["VB (V)"]
        # ecref = reference.nameplate["Induced Voltage"]["VC"]["VC (V)"]

    # print(earef_terminal)

    # print(earef)
    variation.nameplate["Induced Voltage"]["VA"]["VA (V)"] = list(
        map(lambda x: x * voltageFactor, earef))
    variation.nameplate["Induced Voltage"]["VB"]["VB (V)"] = list(
        map(lambda x: x * voltageFactor, ebref))
    variation.nameplate["Induced Voltage"]["VC"]["VC (V)"] = list(
        map(lambda x: x * voltageFactor, ecref))

    coggingRef = reference.nameplate.get("Cogging Torque", {}).get(
        "Data", {}).get("Cogging Torque (Nm)", [])

    # Calculate ke from the Va signal!
    variation.nameplate["ke (V*s/rad)"] = max(
        variation.nameplate["Induced Voltage"]["VA"]["VA (V)"]) / (2 * math.pi * refSpeed / 60)

    # print("ke", variation.nameplate["ke (V*s/rad)"], max(
    #     variation.nameplate["Induced Voltage"]["VA"]["VA (V)"]), "voltage factor", voltageFactor, "peak", max(earef))

    # print(reference.nameplate["Induced Voltage"]["VA"]["VA (V)"])
    if len(coggingRef) != 0:
        variation.nameplate["Cogging Torque"]["Data"]["Cogging Torque (Nm)"] = list(
            map(lambda x: x * coggingFactor, coggingRef))

    phaseAdvance = variation.controlcircuit.phaseAdvance

    # Get the coefficents for the equivalent star model.
    cn_EMF = getFFTCoefficients(
        time, variation.nameplate["Induced Voltage"]["VA"]["VA (V)"], 20)
    ke60deg = ke60degAverage(cn_EMF, refSpeed, 0, phaseAdvance)

    variation.nameplate["Fourier Coefficients EMF"] = cn_EMF
    # For large phase advance values the maxSpeed estimation might be to low. This is why the correction is used.
    variation.nameplate["Maximal Speed (rpm)"] = 1 * \
        variation.controlcircuit.Vdc / ke60deg * 30 / math.pi / math.sqrt(3)
    variation.nameplate["Minimal Speed (rpm)"] = 0.05 * \
        variation.controlcircuit.Vdc / ke60deg * 30 / math.pi / math.sqrt(3)
    variation.nameplate["Maximal Torque (Nm)"] = 3.0 / math.sqrt(
        2.0) * variation.nameplate["ke (V*s/rad)"] * variation.controlcircuit.ImaxTransistorRMS
    variation.nameplate["Minimal Torque (Nm)"] = 0
    variation.nameplate["Btooth (T)"] = reference.nameplate["Btooth (T)"] * \
        fluxDensityFactor
    variation.nameplate["Byoke (T)"] = reference.nameplate["Byoke (T)"] * \
        fluxDensityFactor
    variation.nameplate["Ideal Overhang (%)"] = idealOverhang
    variation.nameplate["Effective Overhang (%)"] = overhang

    # print(settings)
    # print(variation.nameplate["Scaling Factors"])

    if (settings.get("Use Correction Factors", True) == False):
        variation.nameplate["Resistance (Ohm)"] /= variation.nameplate["Scaling Factors"]["Resistance"]
        variation.nameplate["Ld (H)"] /= variation.nameplate["Scaling Factors"]["Ld"]
        variation.nameplate["Lq (H)"] /= variation.nameplate["Scaling Factors"]["Lq"]
        variation.nameplate["ke (V*s/rad)"] /= variation.nameplate["Scaling Factors"]["Induced Voltage"]

        variation.nameplate["Induced Voltage"]["VA"]["VA (V)"] = list(
            map(lambda x: x * voltageFactor, variation.nameplate["Induced Voltage"]["VA"]["VA (V)"]))
        variation.nameplate["Induced Voltage"]["VB"]["VB (V)"] = list(
            map(lambda x: x * voltageFactor, variation.nameplate["Induced Voltage"]["VB"]["VB (V)"]))
        variation.nameplate["Induced Voltage"]["VC"]["VC (V)"] = list(
            map(lambda x: x * voltageFactor, variation.nameplate["Induced Voltage"]["VC"]["VC (V)"]))
    # if hasattr(variation, 'settings'):
    #     print(variation.settings)

    # Use this to calculate terminal values in the machine detail view.
    # All validated variations should have this set to true!
    # Reference machines do not have this field, i.e. it is considerered to be false.
    variation.nameplate["Equivalent Star"] = True

    return variation.nameplate


def validate(variation, reference, settings={}):
    output = {"design": variation.reprJSON()}
    # output["design"]["Nameplate"] = applyScalingLaws(variation, reference)

    if reference != None:
        output["design"]["Nameplate"] = applyScalingLaws(
            variation, reference, settings)

    return json.loads(json.dumps(output, cls=ComplexEncoder, indent=3))


def applyScalingLawsDC(variation, reference):
    """Applies scaling laws on the variation with respect to the reference machine.

    Nameplate resistance contains the following resistances: armature, choke, brushes, connection, cable and source resistances.
    When definig the database object, the user enters the total resistance for the nameplate. In order to take into account the changes of the choke,
    brushes, connection and source resistance changes during machine design, these resistances are substracted and added again (the new values) in This
    validation function. All the correction factors entered by the user are added to the winding. i.e. armature resistance.
    """

    variation.applyTemperature(
        temperature=variation.environment.ambientTemperature)
    deltaR = variation.winding.getArmatureResistanceForAddedLength(
        variation.stator.stacklength - reference.stator.stacklength)

    airgapCorrectionFactor = 1
    windingRatio = variation.winding.coil.usedWindingNumber / \
        reference.winding.coil.usedWindingNumber
    lengthRatio = variation.stator.stacklength / reference.stator.stacklength
    wireGaugeRatio = 1.0 / \
        math.pow(variation.winding.coil.wire.gauge["Conductor Diameter (mm)"] /
                 reference.winding.coil.wire.gauge["Conductor Diameter (mm)"], 2)
    wireStrechingRatio = 1.0 / math.pow((1 - variation.winding.coil.wireStreching / 100) / (
        1 - reference.winding.coil.wireStreching / 100), 2)
    multipleWiresRatio = 1.0 / \
        (variation.winding.coil.numberOfMultipleWires /
         reference.winding.coil.numberOfMultipleWires)
    magnetTempMatFactor = variation.rotor.pole.pockets[0].magnet.material.br / \
        reference.rotor.pole.pockets[0].magnet.material.br
    wireTempMatFactor = variation.winding.coil.wire.material.resistivity / \
        reference.winding.coil.wire.material.resistivity
    displacementAngleFactor = math.cos(variation.commutationSystem.commutator.displacementAngle * math.pi/180.0) / \
        math.cos(
            reference.commutationSystem.commutator.displacementAngle * math.pi/180.0)
    resistanceFactor = windingRatio * wireGaugeRatio * \
        wireTempMatFactor * multipleWiresRatio * wireStrechingRatio
    voltageFactor = windingRatio * lengthRatio * airgapCorrectionFactor * \
        magnetTempMatFactor * displacementAngleFactor
    inductanceFactor = math.pow(windingRatio, 2) * lengthRatio
    fluxDensityFactor = airgapCorrectionFactor * magnetTempMatFactor

    variation.nameplate["Inductance (H)"] = reference.nameplate["Inductance (H)"] * \
        inductanceFactor
    variation.nameplate["ke (V*s/rad)"] = reference.nameplate["ke (V*s/rad)"] * \
        voltageFactor
    variation.nameplate["Btooth (T)"] = reference.nameplate["Btooth (T)"] * \
        fluxDensityFactor
    variation.nameplate["Byoke (T)"] = reference.nameplate["Byoke (T)"] * \
        fluxDensityFactor
    variation.nameplate["Resistance (Ohm)"] = (reference.nameplate["Resistance (Ohm)"] -
                                               reference.commutationSystem.totalResistance + deltaR) * resistanceFactor + variation.commutationSystem.totalResistance

    return variation.nameplate


def validateDC(variation, reference):
    output = {"design": variation.reprJSON()}
    output["design"]["Nameplate"] = applyScalingLawsDC(variation, reference)

    return json.loads(json.dumps(output, cls=ComplexEncoder, indent=3))
