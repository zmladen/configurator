import jwt, json
import datetime
from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import addNewUser, getAllUsers, deleteUser
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

    # @api.expect(user)
    def delete(self):
        print("Delete")
        
        data = json.loads(request.data)

        try:
            users = deleteUser(data)
            return make_response(jsonify(message="User successfully deleted.", data=users), 200)
        except:
            return make_response(jsonify("User with the E-Mail: {} could not be deleted."), 400)


    @api.expect(user)
    def put(self):
        """Creates the new or edits and existing user."""
        data = request.get_json()
        
        data["telephone"] = {
            "office": data["officeTelephone"],
            "mobile": data["mobileTelephone"]
        }

        del data["officeTelephone"]
        del data["mobileTelephone"]

        print(data)
        # user = addNewUser(data)

        # if user:
        #     r = make_response("New user successfully added.", 200)
        #     token = jwt.encode(
        #         {
        #             "id": user["id"],
        #             "firstname": user["firstname"],
        #             "lastname": user["lastname"],
        #             "email": user["email"],
        #             "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        #         },
        #         app.config["SECRET_KEY"],
        #     )
        #     r.headers.set("x-auth-token", token)
        #     r.headers.set("access-control-expose-headers", "x-auth-token")
        #     return r

        return make_response(jsonify("User successfully updated."), 200)


    @api.expect(user)
    def post(self):
        """Creates the new or edits and existing user."""
        data = request.get_json()
        
        data["telephone"] = {
            "office": data["officeTelephone"],
            "mobile": data["mobileTelephone"]
        }

        del data["officeTelephone"]
        del data["mobileTelephone"]

        user = addNewUser(data)

        if user:
            r = make_response(jsonify("New user successfully added."), 200)
            token = jwt.encode(
                {
                    "id": user["id"],
                    "firstname": user["firstname"],
                    "lastname": user["lastname"],
                    "email": user["email"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                },
                app.config["SECRET_KEY"],
            )
            r.headers.set("x-auth-token", token)
            r.headers.set("access-control-expose-headers", "x-auth-token")
            # return r

            return make_response(jsonify("New user successfully added."), 200)

        return make_response(jsonify("User with the E-Mail: {} already exists. Please use another E-Mail.".format(data["email"])), 400)

    # @token_required
    # @api.doc(params=custom_header1)
    # @api.expect(user)
    # def get(self, current_user):
    def get(self):
        """Gets all users."""

        return {'users': getAllUsers()}, 200