class machineType:
    bldcInnerRunner = 1
    bldcOuterRunner = 2
    dcInnerRunner = 3
    dcOuterRunner = 4


class phaseConnection:
    star = 1
    delta = 2


class coilConnection:
    serial = 1
    parallel = 2


class headType:
    round = 1
    straight = 2


class terminalType:
    leftright = 1
    topbottom = 2
    single = 3
    dc = 4


class terminalPosition:
    left = 1
    right = 2
    top = 3
    bottom = 4
    single = 5


class terminalDirection:
    input = 1
    output = 2


class segmentType:
    line = 1
    spline = 2
    angulararc = 3
    arccircle = 4
    arccircle_cw = 5
    arccircle_ccw = 6


class statorType:
    stator1 = 1
    stator2 = 2
    stator3 = 3
    stator4 = 4
    stator5 = 5
    stator6 = 6
    stator7 = 7
    # DC motor, inner-runner, straight back
    stator8 = 8


class rotorType:
    rotor1 = 1
    rotor2 = 2
    rotor3 = 3
    rotor4 = 4
    rotor5 = 5
    rotor6 = 6
    rotor7 = 7
    rotor11 = 11  # tRotorClampingPoleShoe
    # DC motor, inner-runner, magnet segment
    rotor8 = 8
    rotor9 = 9
    rotor10 = 10


class sectorType:
    sector1 = 1
    sector2 = 2
    # DC motor, inner-runner, straight-back
    sector3 = 2


class pocketType:
    pocket1 = 1
    pocket2 = 2
    pocket3 = 3
    pocket4 = 4
    pocket5 = 5
    pocket6 = 6
    pocket7 = 7
    pocket8 = 8
    # DC motor, inner-runner, straight-back
    pocket9 = 9


class testType:
    block120 = 1
    block180 = 2
    sinusoidal = 3
    noload = 4
    cogging = 5


class magnetizationType:
    diametral = 1
    radial = 2
    lateral = 3
    custom = 4


class signalValues:
    rms = 1
    avg = 2
    max = 3
    min = 4
    p2p = 5
    thd = 6


class plotType:
    singleYaxis = 1
    multyYaxis = 2
    transient = 3
    performance = 4
    map = 5
