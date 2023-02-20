import PyPDF2
import numpy
import re

definitions = {
    "Characteristics": [
        {"name":"Rated voltage", "unit":"V", "german":"Nennspannung"},
        {"name":"Rated power", "unit":"W", "german":"Nennleistung"},
        {"name":"Rated torque", "unit":"Ncm", "german":"Nenndrehmoment"},
        {"name":"Rated speed", "unit":"rpm", "german":"Nenndrehzahl"},
        {"name":"Rated current", "unit":"A", "german":"Nennstrom"}
    ],
    "No load characteristics" :[
        {"name":"No load speed", "unit":"rpm/min-1", "german":"Leerlaufdrehzahl"},
        {"name":"No load current", "unit":"A", "german":"Leerlaufstrom"}
    ],
    "Stall characteristics" :[
        {"name":"Stall torque", "unit":"Ncm", "german":"Anlaufmoment"},
        {"name":"Stall current", "unit":"A", "german":"Anlaufstrom"}
    ],
    "Performance characteristics" :[
        {"name":"max. Output power", "unit":"W", "german":"max. Abgabeleistung"},
        {"name":"max. Constant torque", "unit":"A", "german":"max. Dauerdrehmoment"}
    ],
    "Motor parameters" :[
        {"name":"Weight", "unit":"g", "german":"Gewicht"},
        {"name":"Rotor inertia", "unit":"gcm2", "german":"Läuferträgheitsmoment"},
        {"name":"Terminal resistance", "unit":"Ohm", "german":"Anschlusswiderstand"},
        {"name":"Inductance", "unit":"mH", "german":"Induktivität"},
        {"name":"Mech. time constant", "unit":"ms", "german":"Mech. Zeitkonstante"},
        {"name":"Electr. time constant", "unit":"ms", "german":"Elektr. Zeitkonstante"},
        {"name":"Speed regulation constant", "unit":"rpm/Ncm", "german":"Drehzahregelkonstante"},
        {"name":"Torque constant", "unit":"Nc/A", "german":"Drehmomentkonstante"},
        {"name":"Thermal resistance", "unit":"K/W", "german":"Thermischer Widerstand"},
        {"name":"Thermal time constant", "unit":"min", "german":"Thermische Zeitkonstante"},
        {"name":"Axial play", "unit":"mm", "german":"Axialspiel"},
        {"name":"Direction of rotation", "unit":None, "german":"Drehrichtung"},
    ],
    "Design" :[
        {"name":"Commutator", "unit":None, "german":"Kollektor"},
        {"name":"RFI Protection", "unit":None, "german":"Grundentstörung"},
        {"name":"Insulation class", "unit":None, "german":"Isolierstoffklasse"},
        {"name":"Protection class", "unit":None, "german":"Schutzart"},
        {"name":"Commutation", "unit":None, "german":"Kommutierung"},
        {"name":"Armature", "unit":None, "german":"Anker"},
        {"name":"Magnet system", "unit":None, "german":"Magnetsystem"},
        {"name":"Bearings", "unit":None, "german":"Motorlager"},
        {"name":"Housing", "unit":None, "german":"Gehäuse"},
        {"name":"End shields", "unit":None, "german":"Lagerschilde"},
        {"name":"Life expectancy", "unit":"h", "german":"Lebensdauer"}
    ],
    "Operational conditions" :[
        {"name":"Temperature range", "unit":"°C", "german":"Temperaturbereich"},
        {"name":"Axial force", "unit":"N", "german":"Axialkraft"},
        {"name": "Radial force, 10 mm from mounting surface", "unit":"N", "german":"Radialkraft, 10 mm ab Anschraubfläche"}
    ]
}

removeList = ["min-1", "gcm2"]

def getParameterNames():
    parameters = []
    for key in definitions:
        for item in definitions[key]:
            parameters.append(item)
    
    return parameters

def getTextFromPDF(content):
    pdf_reader = PyPDF2.PdfReader(content)

    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    # print(text.encode("utf-8"))
    pdf_file.close()

    return text

def parameterInString(string, item_list):
    for item in item_list:
        # if item["name"].lower() in string.lower():
        #     return item

        if item["name"] in string:
            return item

    return False

def removeStrings(string, remove_list):
    for remove_string in remove_list:
        string = string.replace(remove_string, "")
    return string

def extractNumbers(string):
    return [item for item in re.findall(r"[-+]?(?:\d*\.*\d+)", string)]

pdf_file = open(r"example1.pdf", "rb")


text = getTextFromPDF(pdf_file)
list_of_parameters = getParameterNames()

table_list = text.split("\n")

output = {}
for index, item in enumerate(table_list):
    parameter = parameterInString(item, list_of_parameters)
    if parameter:

        line = item.replace(parameter["name"],"").replace(parameter["german"],"")
        if parameter["unit"]:
            output[parameter["name"]] = extractNumbers(removeStrings(line, removeList)) 
        else:
            output[parameter["name"]] = line 


print(output)