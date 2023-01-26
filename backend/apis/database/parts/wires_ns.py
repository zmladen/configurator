import os, json
from flask import jsonify
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import getAllWires, token_required


api = Namespace(
    "wires", description="Gets all wire gauges from the database."
)

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class wiresView(Resource):
    # @token_required
    # @api.doc(params=custom_header1)
    def get(self):
        return getAllWires()
