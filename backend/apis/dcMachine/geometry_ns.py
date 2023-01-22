import os
import json
from flask import request, jsonify, make_response
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import getAllReferenceMachines, token_required
from motorStudio.dcMachine import *
from motorStudio.utilities import *

api = Namespace("validate/dc/geometry", description="Validates the dc machine parameters.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class geometryView(Resource):
    def post(self):
        data = request.get_json()
        machine = dcMachine(data=data)

        try:
            return make_response(jsonify(machine.getCADGeometryData()), 200, )
        except ValueError:
            return make_response("Could not validate the machine. Please check the data.", 400)
