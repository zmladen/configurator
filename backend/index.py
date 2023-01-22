import os
import sys
import platform
from flask import Flask
from flask_cors import CORS

# Add parent folder because of the fakeDatabase module
sys.path.append("..")

if sys.platform == "win32":
    if platform.architecture()[0] == '32bit':
        # for 32-bit version
        sys.path.append(os.environ["PROGRAMFILES"] + "/FreeCAD 0.19/bin")
        # sys.path.append(os.environ["PROGRAMFILES"] + "/FreeCAD 0.19/bin")

    elif platform.architecture()[0] == '64bit':
        # for 64-bit version
        sys.path.append(os.environ["ProgramW6432"] + "/FreeCAD 0.19/bin")
        # sys.path.append(os.environ["ProgramW6432"] + "/FreeCAD 0.19/bin")
    else:
        raise Exception("Unsupported platform %s" %
                        (platform.architecture()[0]))
elif sys.platform == "linux":
    print("Linux detected")
    sys.path.append("/usr/lib/freecad-python3/lib")
    sys.path.append("/usr/lib/freecad/Mod/Draft")
    sys.path.append("/usr/lib/freecad/Ext")

else:
    print("Platform not supported")


from apis.app import app, api



# cors = CORS(app, resources={r"*": {"origins": "*"}})
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=False)
