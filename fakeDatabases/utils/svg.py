import os
from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree
# from xml.etree.ElementTree import fromstring, ElementTree


def modifySVGAttributes(fileName, tempDirPath, faces):

    xml = ElementTree.parse(os.path.join(tempDirPath, fileName))
    # ElementTree.register_namespace('', "http://www.w3.org/2000/svg")
    svg = xml.getroot()
    # Strip the namespace information in element tags
    stripNs(svg)

    # Loop over faces. In freecad v0.18, each face is exported as <g/> group element which has <path/> and <title/> elements with label name.
    for face in faces:
        # Get all title elements (each <g/> element hasa title and path)
        for i, group in enumerate(svg.findall("g")):
            # Find the title with given label name
            # print(i,group)
            # print(group.find("title"), group.find("path"), group.find("circle"))
            title = group.find("title")
            paths = group.findall("path")
            circles = group.findall("circle")

            if title.text == "b'%s'" % (face["label"]):
                # Get the parh element within the same <g/>
                style = "stroke:%s;stroke-width:%s;stroke-miterlimit:4;stroke-dasharray:%s;fill:%s;fill-rule: evenodd;fill-opacity:%s " % (face.get(
                    "stroke", "black"), face.get("stroke-width", 1), face.get("stroke-dasharray", "none"), face["fill"], face.get("fill-opacity", 1))

                for path in paths:
                    path.set("vector-effect", "non-scaling-stroke")
                    # Change the style attribute. Defined in freecad
                    path.set("style", style)
                for circle in circles:
                    circle.set("vector-effect", "non-scaling-stroke")
                    # Change the style attribute. Defined in freecad
                    circle.set("style", style)

                # Rotate-Copy the group if "Number of Segment" is defined
                for i in range(1, face.get("Number of Segments", 1)):
                    # print(face["label"], i, face["Number of Segments"], i * 360/face["Number of Segments"])
                    group_tmp = ElementTree.fromstring(
                        ElementTree.tostring(group))
                    transform_tmp = group_tmp.get("transform")
                    transform_tmp += " rotate(%s)" % (i *
                                                      360/face["Number of Segments"])
                    # print(transform_tmp)
                    group_tmp.set("transform", transform_tmp)
                    svg.append(group_tmp)

    # Set width and height to 100% to fit the containing element
    svg.set('width', '100%')
    svg.set('height', '100%')

    return ElementTree.tostring(svg, encoding='utf8', method='xml').decode("utf-8")


def getSVGFromFreeCad(FreeCAD=None, importSVG=None, fileName=None, tempDirPath=None, faces=[]):

    if fileName == None:
        print("Please define the name of the SVG file.")
        return ""
    else:
        __objs__ = []
        for face in faces:
            __objs__.append(FreeCAD.ActiveDocument.getObject(
                FreeCAD.ActiveDocument.getObjectsByLabel(face["label"])[0].Name))

        # Export SVG to file
        importSVG.export(__objs__, os.path.join(tempDirPath, fileName))
        del __objs__

        # Read and modify attributes
        return modifySVGAttributes(fileName=fileName, tempDirPath=tempDirPath, faces=faces)


def mergeSVGs(svgStrings):
    """ First svg in the list is used to set viewBox and transform of all other files.
    It has to contain at least one group element. This can be improved in the future."""

    xml = ElementTree.ElementTree(ElementTree.fromstring(svgStrings[0]))
    root = xml.getroot()
    stripNs(root)  # Strip the namespace information in element tags
    group = root.findall("g")[0]
    transform = group.get("transform")
    translate = [item for item in transform.split() if "translate" in item][0]

    for svgString in svgStrings[1:]:
        if svgString != None:
            xml = ElementTree.ElementTree(ElementTree.fromstring(svgString))
            root_tmp = xml.getroot()
            # Strip the namespace information in element tags
            stripNs(root_tmp)

            for child in root_tmp:
                child.set("transform", translate + " " + ' '.join(
                    [item for item in child.get("transform").split() if "translate" not in item]))
                root.append(child)

    mydata = ElementTree.tostring(
        root, encoding='utf8', method='xml').decode("utf-8")
    # with open('test.svg', 'w+') as fh:
    #     fh.write(mydata)

    return mydata


def stripNs(el):
    ''' Recursively search this element tree, removing namespaces.
    https://stackoverflow.com/questions/32546622/suppress-namespace-in-elementtree '''
    if el.tag.startswith("{"):
        el.tag = el.tag.split('}', 1)[1]  # strip namespace
    for k in el.attrib.keys():
        if k.startswith("{"):
            k2 = k.split('}', 1)[1]
            el.attrib[k2] = el.attrib[k]
            del el.attrib[k]
    for child in el:
        stripNs(child)
