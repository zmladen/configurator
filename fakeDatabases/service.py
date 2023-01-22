from flask import Flask, request, jsonify, make_response
import os, uuid, json, jwt, jinja2, math, base64
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from apis.app import app
from motorStudio.utilities.functions import *
import numpy as np

fakeUserDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), os.pardir, "fakeDatabases", "users", "users.json"))
fakeMaterialDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "materials"))
fakeChokesDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "parts", "dc", "chokes"))
fakeBrushesMaterialsDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "parts", "dc", "brushes"))
fakeCommutatorMaterialsDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "materials", "commutator"))
fakeMagnetMaterialsDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "materials", "magnets"))
fakeMetalMaterialsDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "materials", "metals"))
fakeReferenceMachineTypesURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "machineTypes", "machineTypes.json"))
fakeWiresDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "parts", "wires", "wires.json"))
fakeReferenceMachinesDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "products", "referenceMachines"))


def getAllWires():
    return json.load(open(fakeWiresDatabaseURL))["wires"]


def getAllUsers():
    return json.load(open(fakeUserDatabaseURL))["users"]


def getUser(fieldname, value):
    """Gets the user by ID."""

    users = json.load(open(fakeUserDatabaseURL))["users"]

    for user in users:
        if user[fieldname] == value:
            return user

    return None


def doesUserExist(email):
    for user in json.load(open(fakeUserDatabaseURL))["users"]:
        if user["email"] == email:
            return True
    return False


def addNewUser(user):
    """Gets the user by ID."""
    users = json.load(open(fakeUserDatabaseURL))["users"]

    data = {}
    data["firstname"] = user["firstname"]
    data["lastname"] = user["lastname"]
    data["email"] = user["email"]
    data["admin"] = False
    data["password"] = generate_password_hash(
        user["password"], method="sha256")
    data["public_id"] = str(uuid.uuid4())

    if not doesUserExist(data["email"]):
        users.append(data)
        with open(fakeUserDatabaseURL, "w") as outfile:
            json.dump({"users": users}, outfile, indent=4)
        return data

    return False


def getAllMaterials():

    return getAllCommutatorMaterials() + getAllMetalMaterials() + getAllMagnetMaterials()


def getAllCommutatorMaterials():
    commutator = []
    for path, subdirs, files in os.walk(fakeCommutatorMaterialsDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                material = json.load(open(os.path.join(path, filename)))
                commutator.append(material)

    return commutator


def getAllChokes():
    chokes = []
    for path, subdirs, files in os.walk(fakeChokesDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                choke = json.load(open(os.path.join(path, filename)))
                chokes.append(choke)

    return chokes


def getAllBrushes():
    brushes = []
    for path, subdirs, files in os.walk(fakeBrushesMaterialsDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                material = json.load(open(os.path.join(path, filename)))
                brushes.append(material)

    return brushes


def getAllMetalMaterials():
    metals = []
    for path, subdirs, files in os.walk(fakeMetalMaterialsDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                material = json.load(open(os.path.join(path, filename)))
                metals.append(material)

    return metals


def getAllMagnetMaterials():
    magnets = []
    for path, subdirs, files in os.walk(fakeMagnetMaterialsDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                material = json.load(open(os.path.join(path, filename)))
                magnets.append(material)

    return magnets


def getAllReferenceMachines():
    controlcircuits = getControlCircuits()
    materials = getAllMaterials()
    phaseConnections = getPhaseConnections()
    coilConnections = getCoilConnections()
    chokes = getAllChokes()
    brushes = getAllBrushes()

    referenceMachines = []
    for path, subdirs, files in os.walk(fakeReferenceMachinesDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                machine = json.load(open(os.path.join(path, filename)))
                referenceMachines.append(__getMachineParametersBasedOnId(machine, True, controlcircuits, materials, phaseConnections, coilConnections, brushes, chokes))

    for machine in referenceMachines:
        if "Induced Voltage" in machine["design"]["Nameplate"]:
            pp = machine["design"]["Rotor"]["Pole Number"] / 2
            refSpeed = machine["design"]["Nameplate"][
                "Induced Voltage"]["speed (rpm)"]
            voltages = machine["design"]["Nameplate"][
                "Induced Voltage"]["VA"]["VA (V)"]
            angles = machine["design"]["Nameplate"][
                "Induced Voltage"]["VA"]["angle (deg)"]
            # time = [60 / pp * 180 * item / refSpeed for item in angles]
            # time = [1 / pp * 2 * math.pi / 180 * item * 60 / 2 / math.pi / refSpeed for item in angles]
            time = [(item * math.pi / 180) / (2 * math.pi * refSpeed / 60)
                    for item in angles]
            if len(time):
                machine["design"]["Nameplate"]["Fourier Coefficients EMF"] = getFFTCoefficients(
                    time, voltages, 15)

    return referenceMachines


def __getMachineParametersBasedOnId(machine=None, replaceECU=True, controlcircuits=[], materials=[], phaseConnections=[], coilConnections=[], brushes=[], chokes=[]):

    windingMatId = machine["design"]['Winding']['Coil']['Wire']['Material']['Used']["id"]
    machine["design"]['Winding']['Coil']['Wire']['Material']['Used'] = next(
        (x for x in materials if x["id"] == windingMatId), None)

    housingMatId = machine["design"]['Housing']['Material']['Used']["id"]
    machine["design"]['Housing']['Material']['Used'] = next(
        (x for x in materials if x["id"] == housingMatId), None)

    shaftMatId = machine["design"]['Shaft']['Material']['Used']["id"]
    machine["design"]['Shaft']['Material']['Used'] = next(
        (x for x in materials if x["id"] == shaftMatId), None)

    if 'Separation Can' in machine["design"]:
        sepCanMatId = machine["design"]['Separation Can']['Material']['Used']["id"]
        machine["design"]['Separation Can']['Material']['Used'] = next(
            (x for x in materials if x["id"] == sepCanMatId), None)

    statorCanMatId = machine["design"]['Stator']['Material']['Used']["id"]
    machine["design"]['Stator']['Material']['Used'] = next(
        (x for x in materials if x["id"] == statorCanMatId), None)

    rotorMatId = machine["design"]['Rotor']['Material']['Used']["id"]
    machine["design"]['Rotor']['Material']['Used'] = next(
        (x for x in materials if x["id"] == rotorMatId), None)

    for i, pocket in enumerate(machine["design"]['Rotor']['Pole']['Pockets']):
        magnetMatId = pocket['Magnet']['Material']['Used']["id"]
        machine["design"]['Rotor']['Pole']['Pockets'][i]['Magnet']['Material']['Used'] = next(
            (x for x in materials if x["id"] == magnetMatId), None)

    if machine["type"]["name"] == "dc":
        collectorMatId = machine["design"]["Commutation System"]['Commutator']['Material']['Used']["id"]
        machine["design"]["Commutation System"]['Commutator']['Material']['Used'] = next(
            (x for x in materials if x["id"] == collectorMatId), None)
        brushId = machine["design"]["Commutation System"]['Commutator']['Brushes']['Used']["id"]
        machine["design"]["Commutation System"]['Commutator']['Brushes']['Used'] = next(
            (x for x in brushes if x["id"] == brushId), None)

        chokeId = machine["design"]["Commutation System"]['Choke']['Used']["id"]
        machine["design"]["Commutation System"]['Choke']['Used'] = next(
            (x for x in chokes if x["id"] == chokeId), None)

    return machine


def getMachine(fieldname, value):
    """Gets the machine by, e.g. ID."""
    machines = getAllReferenceMachines()

    for machine in machines:
        if machine[fieldname] == value:
            return machine

    return None


def getAllMachineTypes():
    return json.load(open(fakeReferenceMachineTypesURL))["types"]


def getAllMaterialTypes():
    return json.load(open(fakeMaterialTypesURL))["types"]


def getMaterial(fieldname, value):
    for material in getAllMaterials():
        if material[fieldname] == value:
            return material


def token_required(f):
    @ wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"})

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = getUser("public_id", data["public_id"])
        except:
            return jsonify({"message": "Token is invalid!"})

        return f(*args, current_user, **kwargs)

    return decorated
