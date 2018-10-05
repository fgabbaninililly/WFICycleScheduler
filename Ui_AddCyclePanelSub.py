from addcyclepanel import Ui_Dialog

from PyQt5 import QtCore,QtWidgets
from CycleScheduler import *
from DataModel import *

class Ui_AddCyclePanelSub(Ui_Dialog):
    context = Context()

    def __init__(self):
        super(Ui_AddCyclePanelSub, self).__init__()
        self.requestedPhase = RequestedPhase()

    def setContext(self, context):
        #The context is a copy from  context in main window. If modified, it wouldn't modify context in main window.
        self.context.initFromContext(context)

    def getContext(self):
        return self.context

    def setupUi(self, Dialog):
        super(Ui_AddCyclePanelSub, self).setupUi(Dialog)
        self.buttonBox.clicked.connect(self.updateRequestedCyclePhase)

        self.cmbComponentName.addItems(list(np.unique(self.context.configurationParameters.getComponents())))

        self.cmbComponentName.currentTextChanged.connect(self.updateCycles)
        self.cmbCycleName.currentTextChanged.connect(self.updateSubphases)
        self.cmbSubPhase.currentTextChanged.connect(self.updateDelayAndDuration)
        self.cmbSubPhase.currentTextChanged.connect(self.updateEndTime)

        self.updateCycles()
        self.updateSubphases()
        self.updateEndTime()

        self.dtEditStart.dateTimeChanged.connect(self.updateEndTime)
        self.updateMaximumTime()

        self.dtEditStart.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dtEditEnd.setDateTime(QtCore.QDateTime.currentDateTime())

        self.accepted_input = False
        self.buttonBox.accepted.connect(self.setResult)

    def updateRequestedCyclePhase(self):

        self.requestedPhase.startDT = self.dtEditStart.dateTime().toTime_t()
        self.requestedPhase.endDT = self.dtEditEnd.dateTime().toTime_t()
        self.requestedPhase.id = self.context.getNextId()
        self.context.requestedCyclePhases.append(self.requestedPhase)
        return

    def updateCycles(self):
        self.cmbCycleName.currentTextChanged.disconnect(self.updateSubphases)

        self.cmbCycleName.clear()

        componentNames = np.array(self.context.configurationParameters.getComponents())
        currentComponentName = self.cmbComponentName.currentText()
        filteredCycleNames = self.context.configurationParameters.getCycles()[np.where(currentComponentName == componentNames)[0]]

        for cycleName in list(set(filteredCycleNames)):
            self.cmbCycleName.addItem(str(cycleName))

        self.updateSubphases()
        self.cmbCycleName.currentTextChanged.connect(self.updateSubphases)

    def updateSubphases(self):
        self.cmbSubPhase.currentTextChanged.disconnect(self.updateDelayAndDuration)
        self.cmbSubPhase.currentTextChanged.disconnect(self.updateEndTime)

        self.cmbSubPhase.clear()

        componentNames = self.context.configurationParameters.getComponents()
        currentComponentName = self.cmbComponentName.currentText()
        cycleNames = self.context.configurationParameters.getCycles()
        currentCycleName = self.cmbCycleName.currentText()
        filteredSubphaseNames = self.context.configurationParameters.getSubPhases()[np.where( (currentCycleName == cycleNames) & (currentComponentName == componentNames))[0]]

        for phaseName in list(set(filteredSubphaseNames)):
            self.cmbSubPhase.addItem(phaseName)

        self.updateDelayAndDuration()
        self.updateEndTime()

        self.cmbSubPhase.currentTextChanged.connect(self.updateDelayAndDuration)
        self.cmbSubPhase.currentTextChanged.connect(self.updateEndTime)

    def updateEndTime(self):
        newDateTime = self.dtEditStart.dateTime().addSecs((self.requestedPhase.delay + self.requestedPhase.duration)*60)
        self.dtEditEnd.setMinimumDateTime(newDateTime)
        self.dtEditEnd.setDateTime(newDateTime)

    def updateMaximumTime(self):
        maxDateTime = QtCore.QDateTime.currentDateTime().addSecs(Constants.NUMBER_OF_15MIN_TICKS*15*60)
        self.dtEditStart.setMaximumDateTime(maxDateTime.addSecs(-(self.requestedPhase.delay + self.requestedPhase.duration)*60))
        self.dtEditEnd.setMaximumDateTime(maxDateTime)

    def updateDelayAndDuration(self):
        #retrieve cycle phase from component, cycle and phase names
        cyclePhase = self.context.getCyclePhaseFromNames(self.cmbComponentName.currentText(),self.cmbCycleName.currentText(),self.cmbSubPhase.currentText())
        self.requestedPhase.initFromPhase(cyclePhase)

        if not (self.cmbComponentName.currentText() == Constants.COMPONENT_NAME_RRU):
            return

        msg = QtWidgets.QInputDialog()
        msg.setWindowTitle(Constants.COMPONENT_NAME_RRU)
        msg.setLabelText(Constants.MSG_ENTER_DURATION_RRU)

        if msg.exec_() == QtWidgets.QDialog.Accepted:
            self.requestedPhase.duration = int(msg.textValue())
            self.requestedPhase.delay = 0
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText(Constants.MSG_DURATION_RRU)
            msg.setInformativeText(Constants.MSG_CANNOT_OPTIMIZE_CYCLE)
            msg.setWindowTitle(Constants.COMPONENT_NAME_RRU)
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
        else:
            self.updateDelayAndDuration()

    def setResult(self):
        self.accepted_input=True

    def retranslateUi(self, MainWindow):
        # call method on super class
        super(Ui_AddCyclePanelSub, self).retranslateUi(MainWindow)
        # add any other code here