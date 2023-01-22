import os
import json
from flask import jsonify
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import getAllBrushes, token_required


api = Namespace("parts/brushes",
                description="Gets all brush parts from the database.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}


@api.route("/")
class chokes(Resource):
    # @token_required
    # @api.doc(params=custom_header1)
    def get(self):
        return getAllBrushes()