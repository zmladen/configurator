import os
import json
from flask import request, jsonify, make_response
# from flask_restplus import Namespace, Resource, fields
from flask_restx import Namespace, Resource, fields
from fakeDatabases.service import token_required
from motorStudio.pmMachine import *
from analyticalSolvers.dqModel import *


api = Namespace("saveas/msa", description="Saves the dictionary object to a file.")


def saveAs(path, data):
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


@api.route("/")
class saveAsView(Resource):

    def post(self):
        data = request.get_json()
        try:
            saveAs(data['path'], data['content'])
            return make_response("Data saved successfully.", 200)
        except ValueError:
            return make_response("Could not calculate the performance of the machine. Please check the data.", 400)
