from flask import Flask
from flask_restx import Api
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config["SECRET_KEY"] = "thesecret"

api = Api(
    title="Configurator Web Api",
    version="0.0.1",
    description="Python (Flask) based backend for the Bühler Motor GmbH  DC motor configurator.",
)

from .database.materials.magnets.magnets_ns import api as magnets_api
from .database.materials.metals.metals_ns import api as metals_api
from .database.materials.commutator.commutator_ns import api as commutator_api
from .dcMachine.geometry_ns import api as geometry_dc_api
from .dcMachine.validate_ns import api as validate_dc_api
from .saveAs.saveas_msa import api as saveas_msa_api
from .models.analytical_models_ns import api as analytical_models_api
# from .database.products.referenceMachines.reference_types_ns import api as reference_types_api
from .database.machines.machines_ns import api as machines_api
from .database.users.auth_ns import api as auth_api
from .database.materials.materials_ns import api as materials_api
from .database.parts.parts_ns import api as parts_api
from .database.users.users_ns import api as users_api
from .database.machines.scrapPDF_ns import api as scrapPDF_api

api.add_namespace(auth_api)
api.add_namespace(users_api)
api.add_namespace(materials_api)
api.add_namespace(parts_api)
api.add_namespace(machines_api)

api.add_namespace(analytical_models_api)
api.add_namespace(validate_dc_api)
api.add_namespace(geometry_dc_api)
api.add_namespace(scrapPDF_api)
# api.add_namespace(reference_types_api)
# api.add_namespace(commutator_api)
# api.add_namespace(metals_api)
# api.add_namespace(magnets_api)
