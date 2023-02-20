import jwt
import json
import datetime
from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import addNewUser, getAllUsers, deleteUser, editUser
from ...app import app

api = Namespace(
    "machines", description="Creates a new machine and gets all machines from the database.")


@api.route("/")
class UsersView(Resource):

    def delete(self):

        data = json.loads(request.data)

        try:
            machines = []
            # users = deleteUser(data)
            return make_response(jsonify(message="Machine successfully deleted.", data=machines), 200)
        except:
            return make_response(jsonify("User with the id: {} could not be deleted."), 400)

    def post(self):
        """Creates the new machine"""

        # Read PDF
        data = request.get_json()
        # Send the data back to initialize the form
        #
        # user = editUser(data)
        
        machine = {}

        if machine:
            return make_response(jsonify(message="Machine successfully added.", data=machine), 200)

        return make_response(jsonify("Machine with the name: {} already exists. Please try again.".format(data["name"])), 400)
