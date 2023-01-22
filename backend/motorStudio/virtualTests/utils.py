def exportSolutionCSV(oDesign, oDesktop, variableDefinitions, simTime, timeStep, path):
    # Result is multiplied with 1s to avoid auto units
    oModule = oDesign.GetModule("ReportSetup")
    oDesktop.AddMessage(
        "", "", 1, "Exporting the solution. This may take a while!")

    reportNames = oModule.GetAllReportNames()

    for variable in variableDefinitions:
        name, unit, key, time, factor = variable["name"], variable["unit"], "%s (%s)" % (
            variable["name"], variable["unit"]), 0, variable["integration factor"]
        reportName = "%s [%s]" % (name, unit)

        if reportName not in reportNames:
            if variable["type"] == "Fields":
                oModule.CreateReport(reportName, "Fields", "Rectangular Plot", "Setup1 : Transient", [
                                     "Domain:=", "Sweep"], ["Time:=", ["All"]], ["X Component:=", "Time", "Y Component:=", [name]], [])
            else:
                oModule.CreateReport(reportName, "Transient", "Rectangular Plot", "Setup1 : Transient", ["Domain:=", "Sweep"], [
                                     "Time:=", ["All"]], ["X Component:=", "Time", "Y Component:=", ["%s * 1s" % name]], [])

        # if name == "Tooth_Flux_Density" or name == "Yoke_Flux_Density" or name == "Eddy_Current_Losses_Housing" or name == "Eddy_Current_Losses_Separationcan" or name == "Eddy_Current_Losses_Magnet":
        #     if reportName not in reportNames:
        #         oModule.CreateReport(reportName, "Fields", "Rectangular Plot", "Setup1 : Transient", ["Domain:=", "Sweep"], ["Time:=", ["All"]], ["X Component:=", "Time", "Y Component:=", [name]], [])
        # else:
        #     if reportName not in reportNames:
        #         oModule.CreateReport(reportName, "Transient", "Rectangular Plot", "Setup1 : Transient", ["Domain:=", "Sweep"], ["Time:=", ["All"]], ["X Component:=", "Time", "Y Component:=", ["%s * 1s" % name]], [])

        oModule.ExportUniformPointsToFile(
            reportName, path + "/%s [%s].csv" % (name, unit), "0s", "%ss" % simTime, "%ss" % timeStep)
        # oModule.DeleteReports([reportName])
