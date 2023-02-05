from flask import jsonify, make_response
from flask_restx import Namespace, Resource
from fakeDatabases.service import getAllMaterials

api = Namespace("materials", description="Gets all materials from the database.")

@api.route("/")
class MaterialsView(Resource):
    def get(self):
        try:
            materials = getAllMaterials()

            return make_response(jsonify(message="Materials successfully loaded.", data=materials), 200)
        except:
            return make_response(jsonify("Materials could not be loaded."), 400)
