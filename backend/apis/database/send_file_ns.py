import os
import json
from flask import jsonify, send_file, send_from_directory, safe_join, abort, request
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import token_required

api = Namespace("database/sendfile", description="Sends the file from the database with a given path.")


@api.route("/")
class sendFile(Resource):
    def post(self):
        data = request.get_json()
        path = data["path"] + "\\" + data["name"]
        # result = send_file(path, as_attachment=True)
        return send_from_directory(directory=data["path"], filename=data["name"])
