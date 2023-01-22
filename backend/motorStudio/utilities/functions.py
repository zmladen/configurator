from si_prefix import si_format
from utils import *
from ..enums import *
import json
import matplotlib.pyplot as plt
from scipy import fftpack
import numpy as np
import os
import math


def getPlotPoints(segments, positions=0):
    points = []

    for segment in segments:
        if segment["type"] == enums.segmentType.line:
            for p in segment["points"]:
                points.append(p)
        elif segment["type"] == enums.segmentType.arccircle_ccw:
            p1, p2, p3 = (segment["points"][0], segment["points"][1], segment["points"][2])
            c = circle.__3points__(p1, p2, p3)
            angle = abs(p1.getRelativeSlope360(c.center) - p3.getRelativeSlope360(c.center))
            N = int(round(angle) * 3)
            for i in range(0, N + 1):
                points.append(p1.rotateArroundPointCopy(c.center, i * angle / N))

        else:
            p1, p2, p3 = (segment["points"][0], segment["points"][1], segment["points"][2])
            c = circle.__3points__(p1, p2, p3)
            angle = abs(p1.getRelativeSlope360(c.center) - p3.getRelativeSlope360(c.center))
            N = int(round(angle) * 3)
            if p1.getRelativeSlope360(c.center) < p3.getRelativeSlope360(c.center):
                for i in range(0, N + 1):
                    points.append(p1.rotateArroundPointCopy(c.center, i * angle / N))
            else:
                for i in range(0, N + 1):
                    points.append(p1.rotateArroundPointCopy(c.center, -i * angle / N))

    if positions == 0:
        return points

    listOfPoints = []
    for position in range(positions):
        rPoints = []
        for p in points:
            rPoints.append(p.rotateCopy(-90 + (position + 0.5) * 360.0 / positions))
        listOfPoints.append(rPoints)

    return listOfPoints


def changeECUSvg(filePath, electronic):

    MOSFET = electronic["Parts"]["Power Transistors"]
    Inductance = electronic["Parts"]["Intermediate Circuit Inductances"]
    Capacitance = electronic["Parts"]["Intermediate Circuit Capacitors"]
    Shunts = electronic["Parts"]["Current Shunts"]

    with open(filePath, 'r') as svgFile:
        svgString = svgFile.read()

    svgString = svgString.replace("RDSON", str(si_format(MOSFET["Parameters"]["Rdson (Ohm)"], precision=2)) + "Ohm")
    svgString = svgString.replace("tON", str(si_format(MOSFET["Parameters"]["Rise Time MOSFET (s)"], precision=0)) + "s")
    svgString = svgString.replace("tOFF", str(si_format(MOSFET["Parameters"]["Fall Time MOSFET (s)"], precision=0)) + "s")

    svgString = svgString.replace("RL_Ohm", str(si_format(Inductance["Resistance (Ohm)"], precision=0)) + "Ohm")
    svgString = svgString.replace("L_H", str(si_format(Inductance["Inductance (H)"], precision=0)) + "H")

    svgString = svgString.replace("RDC_Ohm", str(si_format(electronic["Power Source"]["Inner Resistance (Ohm)"], precision=2)) + "Ohm")
    svgString = svgString.replace("VDC_V", str(si_format(electronic["Power Source"]["Supply Voltage (V)"], precision=2)) + "V")

    svgString = svgString.replace("RA_Ohm", str(si_format(electronic["Cable Resistance"]["Resistance (Ohm)"], precision=2)) + "Ohm")
    svgString = svgString.replace("RB_Ohm", str(si_format(electronic["Cable Resistance"]["Resistance (Ohm)"], precision=2)) + "Ohm")
    svgString = svgString.replace("RC_Ohm", str(si_format(electronic["Cable Resistance"]["Resistance (Ohm)"], precision=2)) + "Ohm")

    svgString = svgString.replace("RC_Ohm", str(si_format(Capacitance["Resistance (Ohm)"], precision=0)) + "Ohm")
    svgString = svgString.replace("C_F", str(si_format(Capacitance["Capacitance (F)"], precision=0)) + "F")

    if (Shunts['Total Number'] == 2):
        svgString = svgString.replace("RSH1_Ohm", str(si_format(Shunts["Resistance (Ohm)"], precision=2)) + "Ohm")
        svgString = svgString.replace("RSH2_Ohm", str(si_format(Shunts["Resistance (Ohm)"], precision=2)) + "Ohm")
        svgString = svgString.replace("RSH3_Ohm", "None")
    else:
        svgString = svgString.replace("RSH1_Ohm", "None")
        svgString = svgString.replace("RSH2_Ohm", "None")
        svgString = svgString.replace("RSH3_Ohm", str(si_format(Shunts["Resistance (Ohm)"], precision=2)) + "Ohm")

    return svgString

def getFFTCoefficients(time, amplitude, N):
    # https://pythontic.com/visualization/signals/fouriertransform_fft

    samplingFrequency = 1 / (time[1] - time[0])
    tpCount = len(amplitude)
    values = np.arange(int(tpCount/2))
    timePeriod = tpCount/samplingFrequency
    frequencies = values/timePeriod

    # Frequency domain representation
    fourierTransform = np.fft.fft(amplitude)/len(amplitude)           # Normalize amplitude
    fourierTransform = fourierTransform[range(int(len(amplitude)/2))] # Exclude sampling frequency

    # print(fourierTransform)
    # print(frequencies)
    output = []
    for i, c in enumerate(fourierTransform[:N]):
        output.append({
            "real": c.real,
            "imag": c.imag,
            "ampl": 2 * abs(c),
            "freq": frequencies[i]
        })

    return output

def getFFTCoefficients_old(time, values, N):
    # Returns the N-Fourier coefficients for signal reconstruction.
    # The input signal is a single period! time in seconds!

    f_s = 1 / (time[1] - time[0])  # Sampling rate, or number of measurements per second
    N_s = len(time)    				# Number of samples (in discrete FFT amplitude has to be scaled with N_s)

    coeff = fftpack.fft(values) / N_s
    freqs = fftpack.fftfreq(len(values)) * f_s

    output = []
    for i, c in enumerate(coeff[:N]):
        output.append({
            "real": c.real,
            "imag": c.imag,
            "ampl": 2 * math.sqrt(c.real**2 + c.imag**2),
            "freq": freqs[i]
        })

    return output


def readJSONFile(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data


def fourierFunction(Y, x, t, position=1):
    total = 0
    f = x[1]
    for n in range(1, len(x)):
        if (x[n] >= 0):
            an = 2 * Y.real[n]
            bn = -2 * Y.imag[n]
            shift = (position - 1) * 2 * math.pi / 9.0 * 3
            total += an * np.cos(2 * math.pi * n * f * t + n * shift) + bn * np.sin(2 * math.pi * n * f * t + n * shift)
        else:
            break
        # an = 2 * Y.real[n]
        # bn = -2 * Y.imag[n]
        # shift = 3 * (position - 1) * 2 * math.pi / 9
        # total += an * np.cos(2 * math.pi * n * f * t +  n * shift) / 2 + bn * np.sin(2 * math.pi * n * f * t + n * shift) / 2
    return total


def getClosest(myList, myNumber):
    """Gets the closest number, to a given value, from a list of numbers. List can also contain numbers as strings."""
    if len(myList) > 0:
        closest = myList[0]
        for i in range(1, len(myList)):
            if abs(float(myList[i]) - myNumber) < abs(float(closest) - myNumber):
                closest = myList[i]
        return closest
    else:
        return None


def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0

    if inc == None:
        inc = 1.0

    L = []
    while 1:
        next = start + len(L) * inc
        if inc > 0 and next >= end:
            break
        elif inc < 0 and next <= end:
            break
        L.append(next)

    return L


def areSamePoints(points):
    """ If only one point is different the result is False. """
    pref = points[0]
    for p in points[1:]:
        if (pref.X != p.X or pref.Y != p.Y):
            return False
        else:
            pref = p

    return True

# Delete these functions. Move to utils module.


def avg(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return np.mean(data[N1:N2])


def avg_abs(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return np.mean(np.abs(data[N1:N2]))


def maximum(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return max(data[N1:N2])


def minimum(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return min(data[N1:N2])


def rms(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return np.sqrt(np.mean(np.array(data[N1:N2])**2))


def p2p(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return abs(max(data[N1:N2]) - min(data[N1:N2]))


def thd(data, limits=None):
    """
    Calculates the THD value of the transient signal.
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.fftpack.fft.html
    """
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    N = len(data[N1:N2])
    coeffs = fftpack.fft(data[N1:N2]) / N
    c = np.abs(coeffs[1:N // 2])
    THD = 100 * np.sqrt(np.sum(c[2:]**2)) / c[1]
    return THD
