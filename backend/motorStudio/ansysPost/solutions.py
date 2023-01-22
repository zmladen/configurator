import os
import re
import json
import numpy
import enums
import jinja2
from json2table import *
from virtualTests import *
import matplotlib.pyplot as plt
import plotly.plotly as py
import plotly.offline as pyoff
import plotly.graph_objs as go
import base64
from si_prefix import si_format
from functools import reduce
from flatten_json import flatten
from json2html import *
import pandas
from collections import defaultdict


class solutions(object):
    """
    Class that holds methods to read the data obtained by performing the virtual tests. The main function is to read the
    existing directory structure and form the solution data in form of JSON file.
    """

    def __init__(self, project):
        """
        :param project: project object. Contains information about the current project and tests that are performed.
        """
        self.project = project
        self.imagesPath = self.project.imageDirectory

    def createHTMLReport(self):
        """ Creates the HTML report of the calculations. """

        self.project.machine.readMaterials(matlibDirectory=self.project.matlibDirectory)

        report = {
            'title': 'Calculation Report',
            'text': 'Motor Studio Numerics',
            'footer': 'Motor Studio&#169 v1.0. Author: Mladen Zec, Bühler Motor GmbH.',
            'sections': [
                {
                    'title': 'Calculation Order',
                    'text': 'Some text describing the section.',
                    'tables': [
                        {
                            'caption': 'Calculation order details.',
                            # 'table':json2html.convert(self.project.calculationOrder.reprJSON(), table_attributes="id=\"info-table\" class=\"table table-sm table-hover table-bordered table-condensed\""),
                            'table': json2table.convert(self.project.calculationOrder.reprJSON(), build_direction="TOP_TO_BOTTOM", table_attributes={"id": "info-table", "style": "width:100%", "class": "able table-sm table-hover table-bordered table-condensed"}),
                        },
                    ],
                    'images': [],
                },
                {
                    'title': 'Summary',
                    'text': 'Summary of the calculations goes here...',
                    'tables': [],
                    'images':[
                        {
                            'class': 'col-sm-4 text-center',
                            'caption': 'Winding arrangement in the slot.',
                            'image': self.project.parts.drawMachineXY(strokeWidth=0.1, strokeColor='none', margin=(1, 1, 1, 1)),
                        },
                        {
                            'class': 'col-sm-4 text-center',
                            'caption': 'Winding arrangement in the slot.',
                            'image': self.project.parts.drawMachineXZ(strokeWidth=0.1, strokeColor='none', margin=(1, 1, 1, 1)),
                        },
                    ],
                },
                self.__section_Geometry_and_Materials(),
                self.__section_Cogging_Test(),
                self.__section_Noload_Test(),
                self.__section_Block120_Test(),
            ],
        }

        data_html = self.__render_jinja_html(r'C:\Users\mzec\Desktop\Motor Studio Numerics\MS\ansysPost\templates', 'template1.html', report=report)

        with open(self.project.reportFile, "w") as fh:
            fh.write(data_html)

    def getPhaseValues(self):
        """ Creates json representation of the object. """
        self.project.test = noload()
        solutions = self.readSolutions(os.path.join(self.project.testsDirectory, type(noload()).__name__))

        if bool(solutions):
            parameterDict = self.getParameters(solutions)
            dataDict = self.getDataDict(solutions)

            temperature = getClosest([tempearture for tempearture in parameterDict], 25)
            speed = getClosest([speed for speed in parameterDict[temperature]], 1000)

            data = {
                'Temperature (C)': float(temperature),
                'Resistance (Ohm)': self.project.machine.winding.resistance,
                'ke (V*s/rad)': maximum(dataDict['Vp_A'][temperature][speed]) / (2 * math.pi * float(speed) / 60),
                'Ld (H)': avg(dataDict['L_d'][temperature][speed]),
                'Lq (H)': avg(dataDict['L_q'][temperature][speed]),
                'Btooth (T)': maximum(dataDict['B_tooth'][temperature][speed]),
                'Byoke (T)': maximum(dataDict['B_yoke'][temperature][speed]),
            }

            for i in range(self.project.machine.winding.phaseNumber):
                data['V%s (V)' % (self.project.machine.winding.phaseLetters[i])] = dataDict['Vp_%s' % (self.project.machine.winding.phaseLetters[i])][temperature][speed]

            for i in range(self.project.machine.winding.phaseNumber):
                for j in range(self.project.machine.winding.phaseNumber):
                    data["L%s%s (H)" % (self.project.machine.winding.phaseLetters[i], self.project.machine.winding.phaseLetters[j])] = dataDict["L_%s%s" %
                                                                                                                                                (self.project.machine.winding.phaseLetters[i], self.project.machine.winding.phaseLetters[j])][temperature][speed]

            return data
        else:
            return {}

    def __section_Geometry_and_Materials(self):
        """Creates dictionary for the geoemtry and materials section."""

        imagesPath = os.path.join(os.getcwd(), "ansysPost", "templates",  "images")

        windingDataTables = self.__getGeometryMaterialTables(self.project.machine.winding, class_string="table-responsive col-sm-3")
        windingDataTables.append(
            {
                'class': 'table-responsive col-sm-6',
                'caption': 'Winding Layout',
                'table': json2html.convert(self.project.machine.winding.layout.getConnectionTable()['table'], table_attributes="id=\"info-table\" class=\"table table-sm table-hover table-bordered table-condensed\""),
            }
        )

        windingDataTables.append(
            {
                'class': 'table-responsive col-sm-6',
                'caption': 'Winfing Factors',
                'table': json2html.convert(self.project.machine.winding.layout.getConnectionTable()['wf'], table_attributes="id=\"info-table\" class=\"table table-sm table-hover table-bordered table-condensed\""),
            }
        )

        return {
            'title': 'Geometry and Materials',
            'text': 'This section contains information about the geometry and the material used to design the electrical machine. The machine parts, for which the material '
                    'is not explicitly stated, are assumed to have vacuum properties (have no impact on the simulation results).',
            'tables': [],
            'images': [],
            'subsections': [
                {
                    'title': 'Calulation Model',
                    'text': 'Geometry is created using the Motor Studio.',
                    'tables': [],
                    'images':[
                        {
                            'class': 'col-sm-6 text-center',
                            'caption': 'Geometry used for the calculation.',
                            'image': self.__getbase64Image(imagePath=self.imagesPath + "\\calculationmodel.png"),
                        },
                        {
                            'class': 'col-sm-6 text-center',
                            'caption': 'Mesh of the caclulation model.',
                            'image': self.__getbase64Image(imagePath=self.imagesPath + "\\calculationmodel.png"),
                        },
                    ],
                },
                {
                    'title': 'Rotor Data',
                    'text': 'Template parameters used to desctibe the rotor geometry.',
                    'tables': self.__getGeometryMaterialTables(self.project.machine.rotor),
                    'images': [
                        {
                            'class': 'col-sm-12 text-center',
                            'caption': 'Mesh of the caclulation model.',
                            'image': '<img src="%s"/>' % (os.path.join(imagesPath, "rotor1.svg")),
                        },

                    ],
                },
                {
                    'title': 'Stator Data',
                    'text': 'Template parameters used to desctibe the stator geometry.',
                    'tables': self.__getGeometryMaterialTables(self.project.machine.stator),
                    'images': [
                        {
                            'class': 'col-sm-12 text-center',
                            'caption': 'Mesh of the caclulation model.',
                            'image': '<img src="%s"/>' % (os.path.join(imagesPath, "stator3.svg")),
                        },
                    ],
                },
                {
                    'title': 'Housing Data',
                    'text': 'Template parameters used to desctibe the housing geometry.',
                    'tables': self.__getGeometryMaterialTables(self.project.machine.housing),
                    'images': [],
                },
                {
                    'title': 'Separation Can Data',
                    'text': 'Template parameters used to desctibe the separation can geometry.',
                    'tables': self.__getGeometryMaterialTables(self.project.machine.separationcan),
                    'images': [],
                },
                {
                    'title': 'Winding Data',
                    'text': 'Model parameters used to desctibe the winding of the machine.',
                    'tables': windingDataTables,
                    'images': [
                        {
                            'class': 'col-sm-6 text-center',
                            'caption': 'Winding arrangement in the slot.',
                            'image': self.project.parts.drawLayoutXY(strokeWidth=0.1, strokeColor='none', margin=(1, 1, 1, 1), createNewGroup=True),
                        },
                        {
                            'class': 'col-sm-6 text-center',
                            'caption': 'Winding arrangement in the slot.',
                            'image': self.project.parts.drawSlotXY(margin=(1, 1, 1, 1)),
                        },
                    ],
                },
            ],
        }

    def __section_Cogging_Test(self):
        """Creates the dictionary for the cogging test results."""
        self.project.test = cogging()
        self.project.test.machine = self.project.machine
        solutions = self.readSolutions(os.path.join(self.project.testsDirectory, type(cogging()).__name__))

        if solutions != {}:
            parameterDict = self.getParameters(solutions)
            dataDict = self.getDataDict(solutions)

            subsections = []
            for temperature in parameterDict:
                for speed in parameterDict[temperature]:
                    subsections.append(
                        {
                            'title': 'Temperature (C) = %s, Speed (rpm) = %s' % (temperature, speed),
                            'text': 'Results of the current temperature variation.',
                            'tables': [],
                            'images': self.__getPlotlyTimeSignalsImages(dataDict=dataDict, class_string='data-sm-6 text-center', temperature=temperature, speed=speed),
                        }
                    )

            return {
                'title': 'Cogging Virtual Test',
                'text': 'This section summerizes the main resutls of the cogging test. The cogging test is defined as...',
                'tables': [],
                'images': [],
                'subsections': subsections,
            }
        else:
            return None

    def __section_Noload_Test(self):
        """Creates the dictionary for the cogging test results."""

        self.project.test = noload()
        self.project.test.machine = self.project.machine
        solutions = self.readSolutions(os.path.join(self.project.testsDirectory, type(noload()).__name__))
        parameterDict = self.getParameters(solutions)
        dataDict = self.getDataDict(solutions)

        if solutions != {}:
            subsections = []
            for temperature in parameterDict:
                for speed in parameterDict[temperature]:
                    subsections.append(
                        {
                            'title': 'Temperature (C) = %s, Speed (rpm) = %s' % (temperature, speed),
                            'text': 'Results of the current temperature and speed variation.',
                            'tables': [],
                            'images': self.__getPlotlyTimeSignalsImages(dataDict=dataDict, class_string='data-sm-6 text-center', temperature=temperature, speed=speed),
                        }
                    )

            return {
                'title': 'No-load Virtual Test',
                'text': 'This section summerizes the main resutls of the no-load test. The no-load test is defined as...',
                'tables': [],
                'images': [],
                'subsections': subsections,
            }
        else:
            return None

    def __section_Block120_Test(self):
        """Creates the dictionary for the cogging test results."""

        self.project.test = block120()
        self.project.test.machine = self.project.machine
        solutions = self.readSolutions(os.path.join(self.project.testsDirectory, type(block120()).__name__))
        parameterDict = self.getParameters(solutions)
        dataDict = self.getDataDict(solutions)

        if solutions != {}:
            subsections = []
            for temperature in parameterDict:
                subsections.append(
                    {
                        'title': 'Temperature (C) = %s' % (temperature),
                        'text': 'Results of the current temperature variation.',
                        'tables': self.__getPerformanceTables(dataDict=dataDict, class_string='data-sm-12 text-center', temperature=temperature),
                        'images': self.__getPlotlyPerformanceImages(dataDict=dataDict, class_string='data-sm-6 text-center', temperature=temperature),
                    }
                )

            return {
                'title': 'Performance (Block 120deg) Virtual Test',
                'text': 'This section summerizes the main resutls of the performance test. The performance test is defined as...',
                'tables': [],
                'images': [
                    {
                        'class': 'col-sm-6 text-center',
                        'caption': 'Control circuit of the performance model.',
                        'image': self.__getbase64Image(imagePath=self.imagesPath + "\\calculationmodel.png"),
                    },
                ],
                'subsections': subsections,
            }
        else:
            return None

    def __getGeometryMaterialTables(self, part, class_string="table-responsive col-sm-4"):
        flattenData = part.reprFlattenJSON()
        tables = []
        for key, item in flattenData.items():
            tables.append(
                {
                    'class': class_string,
                    'caption': key,
                    # 'table':json2html.convert(item, table_attributes="id=\"info-table\" class=\"table table-sm table-hover table-bordered table-condensed\""),
                    'table': json2table.convert(item, build_direction="LEFT_TO_RIGHT", table_attributes={"id": "info-table", "class": "table table-sm table-hover table-bordered table-condensed"}),
                }
            )

        return tables

    def __getbase64Image(self, imagePath):
        if os.path.exists(imagePath):
            return '<img src="data:image/png;base64,{0}" width="500">'.format(base64.b64encode(open(imagePath, 'rb').read()).decode('utf-8').replace('\n', ''))
        else:
            return '<img src="data:image/png;base64,{0}" width="500">'

    def __render_jinja_html(self, template_loc, file_name, **context):
        """ Renders a HTML string using jinja2 template render. """
        return jinja2.Environment(loader=jinja2.FileSystemLoader(template_loc + '/')).get_template(file_name).render(context)

    def __getPlotlyTimeSignalsImages(self, **kwargs):
        """ Plots the solutions based on the plot definitions obtained by the 'getPlotDefinitions()' method form the corresponding test. """
        dataDict = kwargs.pop('dataDict')
        class_string = kwargs.pop('class_string')
        temperature = kwargs.pop('temperature')
        speed = kwargs.pop('speed')

        images = []
        for group in self.project.test.getVariableGroups():
            if group['plottype'] == enums.plotType.singleYaxis:
                xtrace = group['x-trace']
                data = []
                for ytrace in group['y-traces']:
                    data.append(go.Scatter(x=dataDict[xtrace['name']][temperature][speed], y=dataDict[ytrace['name']][temperature][speed], name=ytrace['caption']))

                layout = go.Layout(
                    height=300,
                    width=450,
                    xaxis=dict(title=group['xlabel'], domain=[0, 1]),
                    yaxis=dict(title=group['ylabel'], showline=True),
                )
                fig = go.Figure(data=data, layout=layout)
                images.append(
                    {
                        'class': class_string,
                        'caption': 'Temperature (C) = %s, Speed (rpm) = %s' % (temperature, speed),
                        'image': pyoff.plot(fig, include_plotlyjs=True, output_type='div', config={'showLink': False, 'sendDataToCloud': False, 'modeBarButtonsToRemove': ['sendDataToCloud']}),
                    }
                )

        return images

    def __getPlotlyPerformanceImages(self, **kwargs):
        """ Plots the solutions based on the plot definitions obtained by the 'getPlotDefinitions()' method form the corresponding test. """
        dataDict = kwargs.pop('dataDict')
        class_string = kwargs.pop('class_string')
        temperature = kwargs.pop('temperature')
        layout_dict = dict(
            title='multiple y-axes example',
            width=900,
            xaxis=dict(title='Drive Performance', domain=[0.4, 1], zeroline=False),
        )

        images = []
        for group in self.project.test.getVariableGroups():
            if group['plottype'] == enums.plotType.performance:
                data = []
                xtrace = group['x-trace']

                for i, ytrace in enumerate(group['y-traces'], 1):
                    x_avg, y_avg = [], []

                    for speed in dataDict[ytrace['name']][temperature]:
                        (N1, N2) = self.__getIndexes(signal=dataDict[ytrace['name']][temperature][speed])
                        x_avg.append(avg(dataDict[xtrace['name']][temperature][speed], limits=(N1, N2)))
                        y_avg.append(avg(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2)))

                    data.append(go.Scatter(x=x_avg, y=y_avg, name=ytrace['caption'], yaxis='y%s' % (i)))
                    if i == 1:
                        layout_dict['yaxis%s' % (i)] = dict(title=ytrace['caption'], anchor='free', side='left', position=i * 0.1, showline=True, showspikes=True)
                    else:
                        layout_dict['yaxis%s' % (i)] = dict(title=ytrace['caption'], anchor='free', overlaying='y', side='left', position=i * 0.1, showline=True, showspikes=True)

                fig = go.Figure(data=data, layout=go.Layout(layout_dict))
                images.append(
                    {
                        'class': class_string,
                        'caption': 'Performance caclulation, Temperature (C) = %s' % (temperature),
                        'image': pyoff.plot(fig, include_plotlyjs=True, output_type='div', config={'showLink': False, 'sendDataToCloud': False, 'modeBarButtonsToRemove': ['sendDataToCloud']}),
                    }
                )

        return images

    def __getPerformanceTables(self, **kwargs):
        """Creates performance dict to be rendered as HTML table."""
        dataDict = kwargs.pop('dataDict')
        class_string = kwargs.pop('class_string')
        temperature = kwargs.pop('temperature')

        test = self.project.test.getVariableGroups()[0]
        rows = []
        for speed in dataDict[test['x-trace']['name']][temperature]:
            vars_dict = defaultdict(float)
            for group in self.project.test.getVariableGroups():
                for ytrace in group['y-traces']:
                    if ytrace['show']:
                        (N1, N2) = self.__getIndexes(signal=dataDict[ytrace['name']][temperature][speed])
                        vars_dict[ytrace['caption']] = {
                            'avg': si_format(avg_abs(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2))),
                            'rms': si_format(rms(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2))),
                            'max': si_format(maximum(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2))),
                            'min': si_format(minimum(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2))),
                            'p2p': si_format(p2p(dataDict[ytrace['name']][temperature][speed], limits=(N1, N2))),
                        }

            rows.append(vars_dict)

        return [{
            'class': class_string,
            'caption': 'Power Characteristics',
            'table': json2html.convert(rows, table_attributes="id=\"info-table\" class=\"table table-sm table-hover table-condensed\""),
        }]

    def getDataDict(self, solutions):
        """Calculates the data important for the performance analysis."""
        # Nested dictionaries
        vars_dict = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for solution in solutions:
            temperature = solution['parameters']['temperature']
            speed = solution['parameters']['speed']
            data = solution['data']
            for var in data:
                vars_dict[var][temperature][speed] = data[var]

        return vars_dict

    def getParameters(self, solutions):
        param_dict = defaultdict(list)

        for solution in solutions:
            temperature = solution['parameters']['temperature']
            speed = solution['parameters']['speed']

            param_dict[temperature].append(speed)
        return param_dict

    def readSolutions(self, directory):
        """ Reads the CSV solution file and returns the dictionary in form {'parameters':{2-dict}, 'data': {n-dict}}. """
        solutions = []
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith(".csv"):
                    # Extract the numbers from the file name. Important is that the temperature is given first!
                    numbers = re.findall(r"\d+", filename)
                    parameters = {}
                    parameters['temperature'] = numbers[0]
                    parameters['speed'] = numbers[1]
                    # Get the data and make the solution dictionary
                    data = {}
                    df = pandas.read_csv(os.path.join(directory, filename))
                    for i, colname in enumerate(df.columns):
                        data[colname] = df[colname].tolist()

                    solutions.append({
                        'parameters': parameters,
                        'data': data
                    })

            return solutions
        else:
            print(directory + "does not exist! Empty dictionary will be returned")
            return {}

    def __getIndexes(self, signal=[]):
        """ Calculates indexes for the given integration window (0-1). Returns a tuple of intexes, i.e. (N1, N2) """
        N2 = len(signal)
        N1 = N2 - int(len(signal) / self.project.test.numberofPeriods)
        return (N1, N2)
