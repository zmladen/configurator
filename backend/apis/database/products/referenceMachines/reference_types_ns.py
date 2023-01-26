import os
import json
from flask import jsonify
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource
from fakeDatabases.service import getAllMachineTypes, token_required


api = Namespace("products/referenceMachines/types", description="Gets all types of the reference machines.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class referenceMachinesTypeView(Resource):
    # @token_required
    # @api.doc(params=custom_header1)
    def get(self):
        return getAllMachineTypes()
