import os
import json
from flask import request, jsonify, make_response
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import token_required
from motorStudio.dcMachine import *
from motorStudio.utilities import *

api = Namespace("validate/dc", description="Validates the dc machine parameters.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class validateView(Resource):
    def post(self):
        data = request.get_json()
        variation = dcMachine(data=data["variation"])

        if data["reference"]:
            reference = dcMachine(data=data["reference"])
        else:
            reference = dcMachine(data=data["variation"])


        try:
            return make_response(jsonify({"data": validateDC(variation=variation, reference=reference)}), 200, )
        except ValueError:
            return make_response("Could not validate the machine. Please check the data.", 400)
