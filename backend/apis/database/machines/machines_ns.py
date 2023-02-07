from flask import jsonify, make_response
from flask_restx import Namespace, Resource
from fakeDatabases.service import getAllMachines

api = Namespace("machines", description="Gets all reference machines from the database.")

@api.route("/")
class MachinesView(Resource):
    def get(self):
        try:
            machines = getAllMachines()

            return make_response(jsonify(message="Machines successfully loaded.", data=machines), 200)
        except:
            return make_response(jsonify("Machines could not be loaded."), 400)
