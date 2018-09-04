from addcyclepanel import Ui_Dialog

from PyQt5 import QtCore
import time

from OptimizerFunctions import *
from Context import *

class Ui_AddCyclePanelSub(Ui_Dialog):
    def __init__(self):
        super(Ui_AddCyclePanelSub, self).__init__()

    def setupUi(self, Dialog):
        super(Ui_AddCyclePanelSub, self).setupUi(Dialog)
        self.delay=0
        self.duration=0
        self.cmbComponentName.addItems(list(np.flip(np.unique(Components))))

        self.cmbComponentName.currentTextChanged.connect(self.CycleOfComponents)
        self.cmbCycleName.currentTextChanged.connect(self.updateDelayAndDuration)
        self.cmbCycleName.currentTextChanged.connect(self.updateEndTime)

        self.CycleOfComponents()

        self.dtEditStart.dateTimeChanged.connect(self.updateEndTime)
        self.updateMaximumTime()

        self.dtEditStart.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dtEditEnd.setDateTime(QtCore.QDateTime.currentDateTime())

        self.accepted_input= False
        self.buttonBox.accepted.connect(self.setResult)

    def updateEndTime(self):
        newDateTime = self.dtEditStart.dateTime().addSecs((self.delay + self.duration)*60)
        self.dtEditEnd.setMinimumDateTime(newDateTime)
        self.dtEditEnd.setDateTime(newDateTime)

    def updateMaximumTime(self):
        maxDateTime = QtCore.QDateTime.currentDateTime().addSecs(nb15min*15*60)
        self.dtEditStart.setMaximumDateTime(maxDateTime.addSecs(-(self.delay + self.duration)*60))
        self.dtEditEnd.setMaximumDateTime(maxDateTime)

    def updateDelayAndDuration(self):
        index=Cyclename_to_index(self.cmbComponentName.currentText(),self.cmbCycleName.currentText())
        self.delay=De[index]
        self.duration = Du[index]

    def CycleOfComponents(self):
        self.cmbCycleName.currentTextChanged.disconnect(self.updateDelayAndDuration)
        self.cmbCycleName.currentTextChanged.disconnect(self.updateEndTime)

        self.cmbCycleName.clear()
        for cycle_name in Cyclenames[np.where(self.cmbComponentName.currentText() == Components)[0]]:
            self.cmbCycleName.addItem(str(cycle_name))

        self.updateDelayAndDuration()
        self.updateEndTime()

        self.cmbCycleName.currentTextChanged.connect(self.updateDelayAndDuration)
        self.cmbCycleName.currentTextChanged.connect(self.updateEndTime)

    def setResult(self):
        self.accepted_input=True

    def retranslateUi(self, MainWindow):
        # call method on super class
        super(Ui_AddCyclePanelSub, self).retranslateUi(MainWindow)
        # add any other code here

    def getComponent(self):
        return self.cmbComponentName.currentText()

    def getCycle(self):
        return self.cmbCycleName.currentText()

    def getStart(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.dtEditStart.dateTime().toTime_t()))
    def getEnd(self):
        return time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.dtEditEnd.dateTime().toTime_t()))


