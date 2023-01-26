import os
import json
from flask import request, jsonify, make_response
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import getAllReferenceMachines, token_required
from motorStudio.pmMachine import *
from analyticalSolvers.dqModel import *
from analyticalSolvers.dcModel import *
from analyticalSolvers.blckModel import *
# from analyticalSolvers.__blckModel import *

api = Namespace("analytical/models",
                description="Calculates the machine performance analytically.")


@api.route("/")
class dqModelView(Resource):
    def post(self):
        data = request.get_json()

        for variation in data["variations"]:

            # Delete old results if exists
            variation.pop("result", None)

            print("before")
            print(variation["design"]["Environment"]
                  ["Ambient Temperature (C)"])
            if variation["type"]["name"] == "bldc":
                controlcircuitId = variation["design"]['Control Circuit']['Used']['Control Algorithm']['id']
                if (controlcircuitId == "0123749a-4fc7-44fa-b7c5-e2e60fef989e"):
                    model = dqModel(
                        data={"variation": variation, "loads": data["loads"]})
                    variation["results"] = model.calculatePerformance()
                else:
                    model = blckModel(
                        data={"variation": variation, "loads": data["loads"]})
                    variation["results"] = model.calculatePerformance()
            else:
                model = dcModel(
                    data={"variation": variation, "loads": data["loads"]})
                variation["results"] = model.calculatePerformance()

            print("after")
            print(variation["design"]["Environment"]
                  ["Ambient Temperature (C)"])
        try:
            return make_response(jsonify({"variations": data["variations"]}), 200)
        except ValueError:
            return make_response("Could not calculate the performance of the machine. Please check the data.", 400)
