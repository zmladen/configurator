from flask import jsonify, make_response
from flask_restx import Namespace, Resource
from fakeDatabases.service import getAllParts

api = Namespace("parts", description="Gets all parts from the database.")

@api.route("/")
class MaterialsView(Resource):
    def get(self):
        try:
            parts = getAllParts()

            return make_response(jsonify(message="Parts successfully loaded.", data=parts), 200)
        except:
            return make_response(jsonify("Parts could not be loaded."), 400)
