import datetime
from flask import Flask, request, jsonify, make_response
import os
import uuid
import json
import jwt
import jinja2
import math
import base64
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
fakeReferenceMachinesDatabaseURL = os.path.normpath(os.path.join(os.getcwd(), "..\\fakeDatabases", "products", "machines"))
fakeElectronicsDatabaseURL = os.path.join(os.getcwd(), "..\\fakeDatabases", "parts", "bldc", "electronics")

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

def deleteUser(user):

    users = getAllUsers()

    new_users = [d for d in users if d['id'] != user["id"]]

    with open(fakeUserDatabaseURL, "w") as outfile:
        json.dump({"users": new_users}, outfile, indent=4)

    return new_users

def editUser(user):
    users = json.load(open(fakeUserDatabaseURL))["users"]

    index = -1

    for i, item in enumerate(users):
        if item["id"] == user["id"]:
            index = i
            break

    if index != -1:
        users[index] = user
        with open(fakeUserDatabaseURL, "w") as outfile:
            json.dump({"users": users}, outfile, indent=4)
        return user
    else:
        return False

def addNewUser(user):
    """Gets the user by ID."""
    users = json.load(open(fakeUserDatabaseURL))["users"]

    # data = {}
    # data["firstname"] = user["firstname"]
    # data["lastname"] = user["lastname"]
    # data["email"] = user["email"]
    # data["admin"] = False
    user["created"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user["password"] = generate_password_hash(
        user["password"], method="sha256")
    user["id"] = str(uuid.uuid4())

    if not doesUserExist(user["email"]):
        users.append(user)
        with open(fakeUserDatabaseURL, "w") as outfile:
            json.dump({"users": users}, outfile, indent=4)
        return user

    return False

def getAllParts():

    return getAllChokes() + getAllBrushes() + getAllWires()

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

def getAllWires():
    return json.load(open(fakeWiresDatabaseURL))["wires"]

def getAllMachines():
    controlcircuits = getControlCircuits()
    materials = getAllMaterials()
    chokes = getAllChokes()
    brushes = getAllBrushes()
    phaseConnections = [
      { "name": "star", "id": "6ef70fa6-cbf5-4450-b121-dfa1f41d0988" },
      { "name": "delta", "id": "ccf0dde7-eae8-4877-8c5b-ddab35903deb" }
    ]
    coilConnections = [
      { "name": "serial", "id": "b0ce8956-02d8-4b7d-a785-15bef81a569c" },
      { "name": "parallel", "id": "7384b066-3929-403f-949b-f9f1a484350d" }
    ]

    referenceMachines = []
    for path, subdirs, files in os.walk(fakeReferenceMachinesDatabaseURL):
        for filename in files:
            if filename.endswith(".json"):
                machine = json.load(open(os.path.join(path, filename)))
                referenceMachines.append(__getMachineParametersBasedOnId(machine, True, controlcircuits, materials, phaseConnections, coilConnections, brushes, chokes))

    for machine in referenceMachines:
        if "Induced Voltage" in machine["design"]["Nameplate"]:
            pp = machine["design"]["Rotor"]["Pole Number"] / 2
            refSpeed = machine["design"]["Nameplate"]["Induced Voltage"]["speed (rpm)"]
            voltages = machine["design"]["Nameplate"]["Induced Voltage"]["VA"]["VA (V)"]
            angles = machine["design"]["Nameplate"]["Induced Voltage"]["VA"]["angle (deg)"]
            # time = [60 / pp * 180 * item / refSpeed for item in angles]
            # time = [1 / pp * 2 * math.pi / 180 * item * 60 / 2 / math.pi / refSpeed for item in angles]
            time = [(item * math.pi / 180) / (2 * math.pi * refSpeed / 60) for item in angles]
            if len(time):
                machine["design"]["Nameplate"]["Fourier Coefficients EMF"] = getFFTCoefficients(time, voltages, 15)

    return referenceMachines

def __getMachineParametersBasedOnId(machine=None, replaceECU=True, controlcircuits=[], materials=[], phaseConnections=[], coilConnections=[], brushes=[], chokes=[]):

    if replaceECU and 'Control Circuit' in machine["design"]:
        controlCircuitId = machine["design"]['Control Circuit']['Used']['id']
        machine["design"]['Control Circuit']['Used'] = next(
            (x for x in controlcircuits if x["id"] == controlCircuitId), None)

    if replaceECU and 'Winding' in machine["design"]:
        if machine["type"]["name"] == "bldc":
            phaseConnId = machine["design"]['Winding']['Phase Connection']['Used']['id']
            machine["design"]['Winding']['Phase Connection']['Used'] = next(
                (x for x in phaseConnections if x["id"] == phaseConnId), None)

            coilConnId = machine["design"]['Winding']['Coil Connection']['Used']['id']
            machine["design"]['Winding']['Coil Connection']['Used'] = next(
                (x for x in coilConnections if x["id"] == coilConnId), None)

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

def getControlCircuits():
    filenames = os.listdir(fakeElectronicsDatabaseURL)
    electronics = []
    for filename in filenames:
        if filename.endswith(".json"):
            electronics.append(
                json.load(
                    open(os.path.join(fakeElectronicsDatabaseURL, filename)))
            )
    return electronics

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
