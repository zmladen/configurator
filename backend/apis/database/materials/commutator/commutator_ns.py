import os
import json
from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import getAllCommutatorMaterials, token_required

api = Namespace("material/commutator", description="Gets all commutator materials from the database.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class MaterialsView(Resource):
    # @token_required
    # @api.doc(params=custom_header1)
    def get(self):
        return getAllCommutatorMaterials()
