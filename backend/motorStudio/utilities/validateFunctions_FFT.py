import math
import enums
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
        an = 2.0 * cn_EMF[ii][0]
        bn = -2.0 * cn_EMF[ii][1]
        Ampl += an * math.cos(ii * position + ii * delta) + bn * math.sin(ii * position + ii * delta)

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


def applyScalingLaws(variation, reference):
    """Material and temperature factors are the same."""
    variation.applyTemperature(temperature=variation.environment["Ambient Temperature (C)"])

    # parallelCoilsRatio = float(variation.winding.numberParallelCoils) / float(reference.winding.numberParallelCoils)
    windingRatio = variation.winding.coil.usedWindingNumber / reference.winding.coil.usedWindingNumber
    lengthRatio = variation.stator.stacklength / reference.stator.stacklength
    wireGaugeRatio = 1.0 / math.pow(variation.winding.coil.wire.gauge["Conductor Diameter (mm)"] / reference.winding.coil.wire.gauge["Conductor Diameter (mm)"], 2)
    magnetTempMatFactor = variation.rotor.pole.pockets[0].magnet.material.br / reference.rotor.pole.pockets[0].magnet.material.br
    wireTempMatFactor = variation.winding.coil.wire.material.conductivity / reference.winding.coil.wire.material.conductivity
    airgapCorrectionFactor = 1
    resistanceFactor = windingRatio * lengthRatio * wireGaugeRatio * wireTempMatFactor
    voltageFactorKe = windingRatio * lengthRatio * airgapCorrectionFactor * magnetTempMatFactor
    voltageFactor = windingRatio * lengthRatio * airgapCorrectionFactor * magnetTempMatFactor
    inductanceFactor = math.pow(windingRatio, 2) * lengthRatio
    earef, ebref, ecref = [], [], []

    if variation.winding.phaseConnection["name"] == "delta":
        # Transform the induced voltage to equivalent star connection.
        # It is neccessary to shift the resulting data by 30deg.el.
        # Angle correction synchronises the signal of the FFT transform with the real data.

        # **************************************************************************************
        refSpeed = variation.nameplate["Induced Voltage"]["speed (rpm)"]
        time = [item * 60 / 2 / math.pi / refSpeed for item in variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"]]
        phaseAdvance = variation.controlcircuit.phaseAdvance
        cn_EMF_Ref = getFFTCoefficients(time, reference.nameplate["Induced Voltage"]["VA"]["VA (V)"], 25)
        angleCorrection = -30 + variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"][0] * (variation.rotor.poleNumber / 2)

        earef, ebref, ecref = [], [], []
        for angle in reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"]:
            ea = _Ea(cn_EMF_Ref, refSpeed, angleCorrection, variation.rotor.poleNumber, angle)
            eb = _Eb(cn_EMF_Ref, refSpeed, angleCorrection, variation.rotor.poleNumber, angle)
            ec = _Ec(cn_EMF_Ref, refSpeed, angleCorrection, variation.rotor.poleNumber, angle)
            earef.append((ea - ec) / 3)
            ebref.append((eb - ea) / 3)
            ecref.append((ec - eb) / 3)

        # Eaaa, Ebbb, Eccc = [], [], []
        # for pos in variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"]:
        #     Eaaa.append(_Ea(cn_EMF, refSpeed, angleCorrection, variation.rotor.poleNumber, pos))
        #     Ebbb.append(_Eb(cn_EMF, refSpeed, angleCorrection, variation.rotor.poleNumber, pos))
        #     Eccc.append(_Ec(cn_EMF, refSpeed, angleCorrection, variation.rotor.poleNumber, pos))
        #
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], Eaaa, '-r')
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], Ebbb, '--g')
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], Eccc, '-.b')
        #
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], variation.nameplate["Induced Voltage"]["VA"]["VA (V)"], '-r')
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], variation.nameplate["Induced Voltage"]["VB"]["VB (V)"], '--g')
        # plt.plot(variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"], variation.nameplate["Induced Voltage"]["VC"]["VC (V)"], '-.b')
        #
        # plt.show()

        # **************************************************************************************

        # Angle = reference.nameplate["Induced Voltage"]["VA"]["angle (deg)"]
        # Ea = reference.nameplate["Induced Voltage"]["VA"]["VA (V)"]
        # Eb = reference.nameplate["Induced Voltage"]["VB"]["VB (V)"]
        # Ec = reference.nameplate["Induced Voltage"]["VC"]["VC (V)"]
        #
        # if Angle != [] and Ea != [] and Eb != [] and Ec != []:
        #     x = [-item for item in Angle[::-1]] + Angle
        #     ea = Ea + Ea
        #     eb = Eb + Eb
        #     ec = Ec + Ec
        #
        #     eai = interpolate.interp1d(x, ea, kind="linear", fill_value="extrapolate")
        #     ebi = interpolate.interp1d(x, eb, kind="linear", fill_value="extrapolate")
        #     eci = interpolate.interp1d(x, ec, kind="linear", fill_value="extrapolate")
        #
        #     # Only use the first half of the transformed data.
        #     angle = [item + 30 / variation.rotor.poleNumber * 2 for item in x[0: len(x) // 2]]
        #     # earef = [(ea[i] - ec[i]) / 3 for i in range (len(angle))]
        #     earef = (eai(angle) - eci(angle)) / 3
        #     ebref = (ebi(angle) - eai(angle)) / 3
        #     ecref = (eci(angle) - ebi(angle)) / 3
        #
        # else:
        #     earef = Ea
        #     ebref = Eb
        #     ecref = Ec

        voltageFactorKe = voltageFactor / math.sqrt(3.0)
        resistanceFactor = resistanceFactor / 3.0
        inductanceFactor = inductanceFactor / 3.0
    else:
        # No transformation needed.
        earef = reference.nameplate["Induced Voltage"]["VA"]["VA (V)"]
        ebref = reference.nameplate["Induced Voltage"]["VB"]["VB (V)"]
        ecref = reference.nameplate["Induced Voltage"]["VC"]["VC (V)"]

    if (reference.winding.coilConnection["name"] != variation.winding.coilConnection["name"]):
        if variation.winding.coilConnection["name"] == "parallel":
            voltageFactorKe = voltageFactorKe / variation.winding.numberParallelCoils
            voltageFactor = voltageFactor / variation.winding.numberParallelCoils
            resistanceFactor = resistanceFactor / variation.winding.numberParallelCoils ** 2
            inductanceFactor = inductanceFactor / variation.winding.numberParallelCoils ** 2
        else:
            voltageFactorKe = voltageFactorKe * variation.winding.numberParallelCoils
            voltageFactor = voltageFactor * variation.winding.numberParallelCoils
            resistanceFactor = resistanceFactor * variation.winding.numberParallelCoils ** 2
            inductanceFactor = inductanceFactor * variation.winding.numberParallelCoils ** 2

    overhangRef = float(reference.rotor.stacklength) / reference.stator.stacklength
    overhang = float(variation.rotor.stacklength) / variation.stator.stacklength
    voltageFactorKe = voltageFactorKe * float(overhang) / overhangRef
    voltageFactor = voltageFactor * float(overhang) / overhangRef

    variation.nameplate["Resistance (Ohm)"] = (reference.nameplate["Resistance (Ohm)"] * resistanceFactor)
    variation.nameplate["ke (V*s/rad)"] = (reference.nameplate["ke (V*s/rad)"] * voltageFactorKe)
    variation.nameplate["Ld (H)"] = reference.nameplate["Ld (H)"] * inductanceFactor
    variation.nameplate["Lq (H)"] = reference.nameplate["Lq (H)"] * inductanceFactor
    variation.nameplate["Induced Voltage"]["VA"]["VA (V)"] = list(map(lambda x: x * voltageFactor, earef))
    variation.nameplate["Induced Voltage"]["VB"]["VB (V)"] = list(map(lambda x: x * voltageFactor, ebref))
    variation.nameplate["Induced Voltage"]["VC"]["VC (V)"] = list(map(lambda x: x * voltageFactor, ecref))
    variation.nameplate["Inductances"]["LAA"]["LAA (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LAA"]["LAA (H)"]))
    variation.nameplate["Inductances"]["LAB"]["LAB (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LAB"]["LAB (H)"]))
    variation.nameplate["Inductances"]["LAC"]["LAC (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LAC"]["LAC (H)"]))
    variation.nameplate["Inductances"]["LBA"]["LBA (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LBA"]["LBA (H)"]))
    variation.nameplate["Inductances"]["LBB"]["LBB (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LBB"]["LBB (H)"]))
    variation.nameplate["Inductances"]["LBC"]["LBC (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LBC"]["LBC (H)"]))
    variation.nameplate["Inductances"]["LCA"]["LCA (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LCA"]["LCA (H)"]))
    variation.nameplate["Inductances"]["LCB"]["LCB (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LCB"]["LCB (H)"]))
    variation.nameplate["Inductances"]["LCC"]["LCC (H)"] = list(map(lambda x: x * inductanceFactor, reference.nameplate["Inductances"]["LCC"]["LCC (H)"]))

    refSpeed = variation.nameplate["Induced Voltage"]["speed (rpm)"]
    time = [item * 60 / 2 / math.pi / refSpeed for item in variation.nameplate["Induced Voltage"]["VA"]["angle (deg)"]]
    phaseAdvance = variation.controlcircuit.phaseAdvance
    cn_EMF = getFFTCoefficients(time, variation.nameplate["Induced Voltage"]["VA"]["VA (V)"], variation.nameplate["Induced Voltage"]["Number of Harmonics"])
    ke60deg = ke60degAverage(cn_EMF, refSpeed, 0, phaseAdvance)
    cn_L = getFFTCoefficients(time, variation.nameplate["Inductances"]["LAA"]["LAA (H)"], variation.nameplate["Inductances"]["Number of Harmonics"])
    cn_M = getFFTCoefficients(time, variation.nameplate["Inductances"]["LAB"]["LAB (H)"], variation.nameplate["Inductances"]["Number of Harmonics"])

    variation.nameplate["Fourier Coefficients L"] = cn_L
    variation.nameplate["Fourier Coefficients M"] = cn_M
    variation.nameplate["Fourier Coefficients EMF"] = cn_EMF
    variation.nameplate["Maximal Speed (rpm)"] = variation.controlcircuit.Vdc / ke60deg * 30 / math.pi / math.sqrt(3)
    variation.nameplate["Minimal Speed (rpm)"] = 0.3 * variation.controlcircuit.Vdc / ke60deg * 30 / math.pi / math.sqrt(3)
    variation.nameplate["Maximal Torque (Nm)"] = 3 / math.sqrt(2) * variation.nameplate["ke (V*s/rad)"] * variation.controlcircuit.ImaxTransistorRMS
    variation.nameplate["Minimal Torque (Nm)"] = 0

    # Use this to calculate terminal values in the machine detail view.
    # All validated variations should have this set to true!
    # Reference machines do not have this field, i.e. it is considerered to be false.
    variation.nameplate["Equivalent Star"] = True

    return variation.nameplate


def validate(variation, reference):
    """Validates the geometry inputs of the machine. If machine is valid returns the json object of the
        machine, otherwise returns None. Also calculates the nameplate of the new machine with respect to the
        reference machine."""

    output = {
        "Stator": variation.stator,
        "Rotor": variation.rotor,
        "Housing": variation.housing,
        "Shaft": variation.shaft,
        "Separation Can": variation.separationcan,
        "Winding": variation.winding,
        "Control Circuit": variation.controlcircuit,
        "Nameplate": applyScalingLaws(variation, reference),
    }

    return json.loads(json.dumps(output, cls=ComplexEncoder, indent=3))
