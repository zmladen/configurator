import jwt, json,datetime, PyPDF2, numpy, re
from io import BytesIO
from flask import request, make_response, jsonify
from flask_restx import Namespace, Resource, fields
from ...app import app

api = Namespace("machines/scrapPDF", description="Scraps the machine data from the available PDFs.")

definitions = {
    "General" : [
        {"name":"Type", "search":"Type", "unit":None, "german":"Baureihe", "pattern": r'\w\.\w{2}\.\w{3}\.\w{3}'},
        {"name":"Variants", "search":"Type", "unit":None, "german":"Baureihe", "pattern": r'[-+]?(?:\d*\.*\d+)', "remove": r'\w\.\w{2}\.\w{3}\.\w{3}'}
    ],
    "Characteristics": [
        {"search":"Rated voltage", "unit":"V", "german":"Nennspannung", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Rated power", "unit":"W", "german":"Nennleistung", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Rated torque", "unit":"Ncm", "german":"Nenndrehmoment", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Rated speed", "unit":"rpm", "german":"Nenndrehzahl", "pattern": r'[-+]?(?:\d*\.*\d+)', "remove":"min-1"},
        {"search":"Rated current", "unit":"A", "german":"Nennstrom", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ],
    "No load characteristics" :[
        {"search":"No load speed", "unit":"rpm/min-1", "german":"Leerlaufdrehzahl", "pattern": r'[-+]?(?:\d*\.*\d+)', "remove":"min-1"},
        {"search":"No load current", "unit":"A", "german":"Leerlaufstrom", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ],
    "Stall characteristics" :[
        {"search":"Stall torque", "unit":"Ncm", "german":"Anlaufmoment", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Stall current", "unit":"A", "german":"Anlaufstrom", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ],
    "Performance characteristics" :[
        {"search":"max. Output power", "unit":"W", "german":"max. Abgabeleistung", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"max. Constant torque", "unit":"A", "german":"max. Dauerdrehmoment", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ],
    "Motor parameters" :[
        {"search":"Weight", "unit":"g", "german":"Gewicht", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Rotor inertia", "unit":"gcm2", "german":"Läuferträgheitsmoment", "pattern": r'[-+]?(?:\d*\.*\d+)', "remove":"gcm2"},
        {"search":"Terminal resistance", "unit":"Ohm", "german":"Anschlusswiderstand", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Inductance", "unit":"mH", "german":"Induktivität", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Mech. time constant", "unit":"ms", "german":"Mech. Zeitkonstante", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Electr. time constant", "unit":"ms", "german":"Elektr. Zeitkonstante", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Speed regulation constant", "unit":"rpm/Ncm", "german":"Drehzahregelkonstante", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Torque constant", "unit":"Nc/A", "german":"Drehmomentkonstante", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Thermal resistance", "unit":"K/W", "german":"Thermischer Widerstand", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Thermal time constant", "unit":"min", "german":"Thermische Zeitkonstante", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Axial play", "unit":"mm", "german":"Axialspiel", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Direction of rotation", "unit":None, "german":"Drehrichtung"},
    ],
    "Design" :[
        {"search":"Commutator", "unit":None, "german":"Kollektor"},
        {"search":"RFI Protection", "unit":None, "german":"Grundentstörung"},
        {"search":"Insulation class", "unit":None, "german":"Isolierstoffklasse"},
        {"search":"Protection class", "unit":None, "german":"Schutzart"},
        {"search":"Commutation", "unit":None, "german":"Kommutierung"},
        {"search":"Armature", "unit":None, "german":"Anker"},
        {"search":"Magnet system", "unit":None, "german":"Magnetsystem"},
        {"search":"Bearings", "unit":None, "german":"Motorlager"},
        {"search":"Housing", "unit":None, "german":"Gehäuse"},
        {"search":"End shields", "unit":None, "german":"Lagerschilde"},
        {"search":"Life expectancy", "unit":"h", "german":"Lebensdauer", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ],
    "Operational conditions" :[
        {"search":"Temperature range", "unit":"°C", "german":"Temperaturbereich", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search":"Axial force", "unit":"N", "german":"Axialkraft", "pattern": r'[-+]?(?:\d*\.*\d+)'},
        {"search": "Radial force, 10 mm from mounting surface", "unit":"N", "german":"Radialkraft, 10 mm ab Anschraubfläche", "pattern": r'[-+]?(?:\d*\.*\d+)'}
    ]
}

removeList = ["min-1", "gcm2"]

def getParameterNames():
    parameters = []
    for key in definitions:
        for item in definitions[key]:
            parameters.append(item)
    
    return parameters

def parameterInString(string, item_list):
    for item in item_list:
        # if item["search"].lower() in string.lower():
        #     return item
        if item["search"] in string:
            return item

    return False

def removeStrings(string, remove_string):
    new_string = string.replace(remove_string, "")
    try:
        new_string = re.sub(remove_string, '', new_string)
    except re.error:
        print(re.error)

    return new_string

def extractNumbers(string, pattern):
    return [item for item in re.findall(pattern, string)]

def getTextFromPDF(content):
    pdf_reader = PyPDF2.PdfReader(content)

    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    # print(text.encode("utf-8"))
    return text

def scrapPDF(text):
    list_of_parameters = getParameterNames()
    table_list = text.split("\n")

    output = {}
    for parameter in getParameterNames():
        for intex, item in enumerate(table_list):
            if parameterInString(item, [parameter]):
                line = item.replace(parameter["search"],"").replace(parameter["german"],"")
                # If "name" not given use "search" as a key value
                name = parameter.get("name", parameter["search"])

                if parameter.get("pattern", False):
                    if parameter.get("remove", False):
                        output[name] = extractNumbers(removeStrings(line, parameter["remove"]), parameter["pattern"])
                    else:
                        output[name] = extractNumbers(line, parameter["pattern"])
                else:
                    output[name] = line 
    return output

def createOutput(data):
    output = {}
    try:
        for i, variant in enumerate(data["Variants"]):
            mType = data["Type"][0].replace('XXX', variant)
            output[mType] ={"Type": mType}
            for key in data:
                if key != "Type" and key != "Variants":
                    if type(data[key]) == list:
                        if len(data[key]) > 1:
                            output[mType][key] = data[key][i]
                        else:
                            output[mType][key] = data[key][0]
                    else:
                        output[mType][key] = data[key]
        return output
    
    except:
        return None


@api.route("/")
class ScrapPDFView(Resource):

    def post(self):
        """Scraps the machine data according to the PDF format."""
        
        # Dict has to contain the "pdf" key
        file = request.files['pdf'] 
        pdf_content = file.read()

        text = getTextFromPDF(BytesIO(pdf_content))
        data = scrapPDF(text)
        output = createOutput(data)

        print(data)

        if output:
            return make_response(jsonify(message="Data successfully scraped.", data=output), 200)

        return make_response(jsonify("Data could not be scraped. Please enter machine values by hand."), 400)
