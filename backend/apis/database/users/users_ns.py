import os
import json
import jwt
import datetime
from flask import request, jsonify, make_response
from flask_restplus import Namespace, Resource, fields
from fakeDatabases.service import addNewUser, fakeUserDatabaseURL, getAllUsers
from ...app import app

api = Namespace("users", description="Creates a new user and gets all users from the database.")

custom_header1 = {
    "x-access-token": {
        "name": "x-access-token",
        "in": "header",
        "type": "string",
        "description": "jwt token",
    }
}

user = api.model(
    "users",
    {
        "firstname": fields.String(required=True, description="First Name"),
        "lastname": fields.String(required=True, description="Last name"),
        "email": fields.String(required=True, description="Valid e-mail address"),
        "password": fields.String(required=True, description="User password"),
    },
)


@api.route("/")
class UsersView(Resource):
    @api.expect(user)
    def post(self):
        """Creates the new user."""
        data = request.get_json()
        user = addNewUser(data)
        if user:
            r = make_response("New user successfully added.", 200)
            token = jwt.encode(
                {
                    "public_id": user["public_id"],
                    "firstname": user["firstname"],
                    "lastname": user["lastname"],
                    "email": user["email"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                },
                app.config["SECRET_KEY"],
            )
            r.headers.set("x-auth-token", token)
            r.headers.set("access-control-expose-headers", "x-auth-token")
            return r

        return make_response(
            "The user with the E-mail: {} already exists. Use another E-mail address.".format(
                data["email"]
            ),
            400,
        )

    # @token_required
    # @api.doc(params=custom_header1)
    # @api.expect(user)
    # def get(self, current_user):
    def get(self):
        """Gets all users."""
        # output = []
        # for user in getAllUsers():
        #     user_data = {}
        #     user_data["firstname"] = user["firstname"]
        #     user_data["lastname"] = user["lastname"]
        #     user_data["password"] = user["password"]
        #     user_data["email"] = user["email"]
        #     # user_data['admin'] = user["admin"]
        #     output.append(user_data)

        # return {'users': output}, 200


        return {'users': getAllUsers()}, 200