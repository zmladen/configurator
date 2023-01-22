import os, json
from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import getAllMaterials, token_required

api = Namespace("material", description="Gets all materials from the database.")

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
        # if not current_user["admin"]:
        #     return jsonify({"message":"Cannot perform that action"})

        return getAllMaterials()
