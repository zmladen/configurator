import os
import json
from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import getAllReferenceMachines, token_required
from motorStudio.utilities.functions import *


api = Namespace("products/referenceMachines", description="Gets all reference machines in the database.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class referenceMachinesView(Resource):
    # @token_required
    # @api.doc(params=custom_header1)
    def get(self):

        machines = getAllReferenceMachines()

        return machines, 201, {"Access-Control-Allow-Origin": "*"}
