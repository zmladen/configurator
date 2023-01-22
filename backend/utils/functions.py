import math
import json
from .point import point
from .circle import circle
from scipy import fftpack
import numpy as np


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
            L.append(next)
            break
        elif inc < 0 and next <= end:
            L.append(next)
            break
        L.append(next)

    return L


def getCentroidDict(points):
    """ Calculates the centroid of tuple of points """
    x, y = 0, 0
    for p in points:
        x += p["x"]
        y += p["y"]

    return point(x / len(points), y / len(points))


def getCentroid(points):
    """ Calculates the centroid of tuple of points """
    x, y = 0, 0
    for p in points:
        x += p.X
        y += p.Y

    return point(x / len(points), y / len(points))


def getCentroidOfList(points):
    """ Calculates the centroid of list of tuples (x, y, z) """
    x, y = 0, 0
    for p in points:
        x += p[0]
        y += p[1]

    return (x / len(points), y / len(points))


def readJSONFile(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data


def areaPolygon(vertices):
    """Calculates the area of an arbitrary polygon given its verticies."""
    area = 0.0
    for i in range(-1, len(vertices) - 1):
        area += vertices[i].X * (vertices[i + 1].Y - vertices[i - 1].Y)
    return abs(area) / 2.0


def getMidPoint(p1, p2):
    """ Calculates the centroid of tuple of points """
    return point((p1.X + p2.X) / 2, (p1.Y + p2.Y) / 2)


def areSamePoints(points):
    """ If only one point is different the result is False. """
    pref = points[0]
    for p in points[1:]:
        if pref.X != p.X or pref.Y != p.Y:
            return False
        else:
            pref = p

    return True


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + int(lv / 3)], 16) for i in range(0, lv, int(lv / 3)))


def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb


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


def p2p(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    return abs(max(data[N1:N2]) - min(data[N1:N2]))


def rms(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    sum2 = 0
    N = len(data[N1:N2])
    for i in data[N1:N2]:
        sum2 += i**2
    return math.sqrt(sum2 / N)


def avg(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    sum = 0
    N = len(data[N1:N2])
    for i in data[N1:N2]:
        sum += i
    return sum / N


def avg_abs(data, limits=None):
    if limits == None:
        N1, N2 = 0, len(data)
    else:
        (N1, N2) = limits

    sum = 0
    N = len(data[N1:N2])
    for i in data[N1:N2]:
        sum += abs(i)

    return sum / N


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
    c = [abs(i) for i in coeffs[1:N // 2]]

    sum2 = 0
    Nc = len(c)
    for i in c:
        sum2 += i**2
    THD = 100 * math.sqrt(sum2 / Nc) / c[1]

    return THD


def getFFTCoefficients1(time, values, N, Np):
    # Returns the N-Fourier coefficients for signal reconstruction.
    # The input signal is a single period! time in seconds!
    # Np is the number of calculated electrical periods
    # https://www.ritchievink.com/blog/2017/04/23/understanding-the-fourier-transform-by-example/

    # time = time[:int(len(time)//Np)]
    # values = values[:int(len(values)//Np)]

    # Sampling rate, or number of measurements per second
    f_s = 1 / (time[1] - time[0])
    # Number of samples (in discrete FFT amplitude has to be scaled with N_s)
    N_s = len(time)

    coeff = fftpack.fft(values) / N_s
    freqs = fftpack.fftfreq(len(values)) * f_s

    output = []
    for i, c in enumerate(coeff[:N]):
        output.append({
            "real": c.real,
            "imag": c.imag,
            "ampl1": 2 * math.sqrt(c.real**2 + c.imag**2),
            "ampl": abs(c),
            "freq": freqs[i]
        })

    return output


def getFFTCoefficients(time, amplitude, N):
    # https://pythontic.com/visualization/signals/fouriertransform_fft

    samplingFrequency = 1 / (time[1] - time[0])
    tpCount = len(amplitude)
    values = np.arange(int(tpCount/2))
    timePeriod = tpCount/samplingFrequency
    frequencies = values/timePeriod

    # Frequency domain representation
    fourierTransform = np.fft.fft(
        amplitude)/len(amplitude)           # Normalize amplitude
    fourierTransform = fourierTransform[range(
        int(len(amplitude)/2))]  # Exclude sampling frequency

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
