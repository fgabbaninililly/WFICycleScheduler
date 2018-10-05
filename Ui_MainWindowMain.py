from PyQt5 import QtWidgets

from Ui_AddCyclePanelSub import Ui_AddCyclePanelSub
from Ui_MainWindowSub import Ui_MainWindowSub

from CycleScheduler import *

#Move this into unit testing project when convenient
def testParameterIntitalization():
    context = Context()
    context.setConfigurationParameters(ConfigurationParameters.createFromExcel(".\config\Variables.xlsx", ".\config\Tags.xlsx"))

    #test if row from Variables.xlsx!Cycles is correctly read
    #Component	Cycle	    SubPhase	    Duration (m)	WFI Flow OSI_PI o rossi (l/15min)	delay from start cycle (m)
    #CP_800711	GLASS BEAD	washing mode II	100	            200	                                0

    print("Test on Variables.xlsx!Cycles starting...")
    components = context.configurationParameters.getComponents()
    componentsList = components.tolist()
    if "CP_800711" not in componentsList:
        raise Exception('Element not in list')

    cycles = context.configurationParameters.getCycles()
    cyclesList = cycles.tolist()
    if "GLASS BEAD" not in cyclesList:
        raise Exception('Element not in list')

    subphases = context.configurationParameters.getSubPhases()
    subphasesList = subphases.tolist()
    if "washing mode II" not in subphasesList:
        raise Exception('Element not in list')

    durations = context.configurationParameters.getDurations()
    durationsList = durations.tolist()
    if 100 not in durationsList:
        raise Exception('Element not in list')

    wfiConsumptions = context.configurationParameters.getWFIConsumptions()
    wfiConsumptionsList = wfiConsumptions.tolist()
    if 200 not in wfiConsumptionsList:
        raise Exception('Element not in list')

    delays = context.configurationParameters.getDelays()
    delaysList = delays.tolist()
    if 0 not in delaysList:
        raise Exception('Element not in list')

    print("Test on Variables.xlsx!Cycles passed!")

    #test if Variables.xlsx!Constants is correctly read
    #MS1_Flow	275;    MS2_Flow	275;     Tank_Capacity	7200;    Limit_MS1_activation	6925;    Limit_MS1_activation	6375;    Constant_usage	25

    print("Test on Variables.xlsx!Constants starting...")
    tmp = context.configurationParameters.getMS1Flow().tolist()[0]
    if 275 != tmp:
        raise Exception('Missing or wrong value')

    tmp = context.configurationParameters.getMS2Flow().tolist()[0]
    if 275 != tmp:
        raise Exception('Missing or wrong value')

    tmp = context.configurationParameters.getTankCapacity().tolist()[0]
    if 7200 != tmp:
        raise Exception('Missing or wrong value')

    tmp = context.configurationParameters.getBaselineUsage().tolist()[0]
    if 25 != tmp:
        raise Exception('Missing or wrong value')

    print("Test on Variables.xlsx!Constants passed!")

    print("Test on Tags.xlsx!Sheet 1 starting...")
    #Component	Tag List
    #CP_800711	Batch_CP_800711_PMX_Internal.RECIPE_NAME.P31.BAT

    tmp = context.configurationParameters.getTagComponents().tolist()
    if "CP_800711" not in tmp:
        raise Exception('Element not in list')

    tmp = context.configurationParameters.getTags().tolist()
    if "Batch_CP_800711_PMX_Internal.RECIPE_NAME.P31.BAT" not in tmp:
        raise Exception('Element not in list')

    print("Test on Tags.xlsx!Sheet 1 passed!")

#Test dialog for adding cycle subphases and times
if __name__ == "__main__":
    import sys

    configurationParameters = ConfigurationParameters.createFromExcel(".\config\Variables.xlsx", ".\config\Tags.xlsx")
	
    context = Context()
    context.setConfigurationParameters(configurationParameters)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindowSub()
    ui.setupUi(MainWindow)
    ui.setContext(context)

    MainWindow.show()
    sys.exit(app.exec_())

"""
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    testParameterIntitalization()

    MainWindow = QtWidgets.QMainWindow()
    #ui = Ui_MainWindowSub()
    #ui.setupUi(MainWindow)

    ui = Ui_AddCyclePanelSub()
    ui.setupUi(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())

"""
