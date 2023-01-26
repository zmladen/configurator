import os, json, jwt, datetime
from flask import request, jsonify, make_response
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import getUser, addNewUser, fakeUserDatabaseURL
from werkzeug.security import generate_password_hash, check_password_hash
from ...app import app

# from flask import current_app as app

api = Namespace("auth", description="Takes care for login of the user.")

user = api.model(
    "user",
    {
        "email": fields.String(required=True, description="Valid e-mail address"),
        "password": fields.String(required=True, description="User password"),
    },
)


@api.route("/")
class Auth(Resource):
    @api.expect(user)
    def post(self):
        data = request.get_json()
        user = getUser("email", data["email"])

        # Check if the user with the given mail is in the database.
        if not user:
            return make_response("E-Mail could not be found.", 400)

        # Check if email and the password match.
        if check_password_hash(user["password"], data["password"]):
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

            return make_response(jsonify({"token": token}), 200)

        # User and the password do not match.
        return make_response("E-Mail and the password do not mach.", 400)
