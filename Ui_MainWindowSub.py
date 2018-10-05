from mainwindow import Ui_MainWindow
from Ui_AddCyclePanelSub import Ui_AddCyclePanelSub
from CycleScheduler import *
from PyQt5.QtWidgets import QTableWidgetItem,QMessageBox,QDialog,QPushButton,QCheckBox,QFileDialog
from pyqtgraph import BarGraphItem
from pyqtgraph import mkPen,mkColor
from PyQt5 import QtCore

class Ui_MainWindowSub(Ui_MainWindow):
    TBL_ADDCYCLE_COL_IDX_ID = 0
    TBL_ADDCYCLE_COL_IDX_COMPONENT = 1
    TBL_ADDCYCLE_COL_IDX_CYCLE = 2
    TBL_ADDCYCLE_COL_IDX_CYCLEPHASE = 3
    TBL_ADDCYCLE_COL_IDX_STARTDT = 4
    TBL_ADDCYCLE_COL_IDX_ENDDT = 5
    TBL_ADDCYCLE_COL_IDX_ISOPTIMIZED = 6
    TBL_ADDCYCLE_COL_IDX_REMOVE = 7

    context = Context()

    def setupUi(self, MainWindow):
        super(Ui_MainWindowSub, self).setupUi(MainWindow)

    def __init__(self):
        super(Ui_MainWindowSub, self).__init__()

    def setContext(self, context):
        self.context = context

    def getContext(self):
        return self.context

    def retranslateUi(self, MainWindow):
        # call method on super class
        super(Ui_MainWindowSub, self).retranslateUi(MainWindow)
        # add any other code here
        self.btnAddCycle.clicked.connect(self.openAddCycleDialog)
        self.dialog = Ui_AddCyclePanelSub()
        self.tblAddCycle.itemChanged.connect(self.tableChanged)
        self.tblAddCycle.horizontalHeader().hideSection(Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ID)

        self.btnCalculateLevel.clicked.connect(self.updatePlan)
        self.btnCalculateLevel.clicked.connect(self.plotOnGraphOptimized)
        self.legend = self.grphViewTankLevel.addLegend(size=(50, 100), offset=(-10, -100))
        self.btnExport.clicked.connect(self.exportPlanToCsv)

    def openAddCycleDialog(self):
        addCycleDialog = QDialog()
        ui = Ui_AddCyclePanelSub()
        ui.setContext(self.context)
        ui.setupUi(addCycleDialog)

        addCycleDialog.exec()
        if ui.accepted_input:
            self.context.initFromContext(ui.getContext())
            self.updateTableFromContext()

    def updateTableFromContext(self):
        self.tblAddCycle.itemChanged.disconnect(self.tableChanged)
        self.tblAddCycle.setRowCount(0)

        for requestedCycle in self.context.requestedCyclePhases:
            self.addRequestedCycleToTable(requestedCycle)

        self.tblAddCycle.itemChanged.connect(self.tableChanged)

    def addRequestedCycleToTable(self, requestedCycle):
        rowPos = self.tblAddCycle.rowCount()
        self.tblAddCycle.insertRow(rowPos)

        button = QPushButton(self.tblAddCycle)
        button.setGeometry(QtCore.QRect(60, 10, 75, 23))
        button.setObjectName("button")
        button.setText("Remove ")
        button.clicked.connect(self.removeCurrentRow)

        checkbox = QCheckBox(self.tblAddCycle)
        checkbox.setGeometry(QtCore.QRect(60, 10, 75, 23))
        checkbox.setObjectName("checkbox")
        if requestedCycle.isOptimized==1:
            checkbox.setChecked(True)
        checkbox.clicked.connect(self.optimizationChanged)

        itemId = QTableWidgetItem(str(requestedCycle.id))
        itemId.setFlags(itemId.flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ID, itemId)

        itemComponent = QTableWidgetItem(requestedCycle.componentName)
        itemComponent.setFlags(itemComponent.flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_COMPONENT, itemComponent)

        itemCycle = QTableWidgetItem(requestedCycle.cycleName)
        itemCycle.setFlags(itemCycle .flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_CYCLE, itemCycle)

        itemPhase = QTableWidgetItem(requestedCycle.name)
        itemPhase.setFlags(itemPhase.flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_CYCLEPHASE, itemPhase)

        itemStart = QTableWidgetItem(requestedCycle.getStartDateStr())
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_STARTDT, itemStart)

        itemEnd = QTableWidgetItem(requestedCycle.getEndDateStr())
        self.tblAddCycle.setItem(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ENDDT, itemEnd)

        self.tblAddCycle.setCellWidget(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ISOPTIMIZED, checkbox)
        self.tblAddCycle.setCellWidget(rowPos, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_REMOVE, button)

    def removeCurrentRow(self):
        selectedRow = self.tblAddCycle.currentRow()
        id = int(self.tblAddCycle.item(selectedRow, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ID).text())
        self.context.removeRequestedCyclePhaseId(id)
        self.updateTableFromContext()

    def optimizationChanged(self, item):
        selectedRow = self.tblAddCycle.currentRow()
        id = int(self.tblAddCycle.item(selectedRow, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ID).text())
        requestedCyclePhase = self.context.getCyclePhaseFromId(id)
        requestedCyclePhase.isOptimized = int(item)

    def tableChanged(self, item):
        row = item.row()
        column = item.column()
        id = int(self.tblAddCycle.item(row, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ID).text())
        requestedCyclePhase = self.context.getCyclePhaseFromId(id)

        if (column == Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_STARTDT):
            requestedCyclePhase.resetStartDateFromString(self.tblAddCycle.item(row, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_STARTDT).text())

        if (column == Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ENDDT):
            requestedCyclePhase.resetEndDateFromString(
                self.tblAddCycle.item(row, Ui_MainWindowSub.TBL_ADDCYCLE_COL_IDX_ENDDT).text())

    def updatePlan(self):
        #Set of the actual time on which optimisation is scaled. The start of the update is the reference start time.
        self.actualTime = time.time()
        #Initialistion of the table of results
        self.tblCycleResults.setRowCount(0)

        #Instancing a OSIPI reader and reading the following PI values: running cycle list, MS1 and MS2 filling machine activity, the tank level.
        piReader = OSIPIReader()
        piReader.setContext(self.context)
        self.runningCyclesList = piReader.getRunningCycles(self.actualTime)
        MS1Active=piReader.getMS1Active()
        MS2Active=piReader.getMS2Active()
        tankLevel=piReader.getTankLevel()

        #Instancing a cyclecheduler and scheduling the request cycles list
        cyclescheduler=CycleScheduler()
        self.scheduledCycleList,self.TankLevelOptimized=cyclescheduler.scheduleCycleRequests(self.runningCyclesList,tankLevel,MS1Active,MS2Active,self.actualTime,self.context)
        self.optimizedCyclesList=[scheduledCycle for scheduledCycle in self.scheduledCycleList if (scheduledCycle.isOptimized==1)]
        self.nonoptimizedCyclesList=[scheduledCycle for scheduledCycle in self.scheduledCycleList if (scheduledCycle.isOptimized==0)]

        #Writing results on the table of results
        self.__writeontblCycleResults(self.runningCyclesList, 'Running')
        self.__writeontblCycleResults(self.optimizedCyclesList, 'Optimized')
        self.__writeontblCycleResults(self.nonoptimizedCyclesList, 'Non Optimized')

    def __writeontblCycleResults(self,scheduledCycleList,Status):
        '''Function that writes on tblCycleResults the information from the scheduled cycles 
        
        :param scheduledCycleList: List of Scheduled Cycles instances.
        :param Status: String which indicates status of scheduled cycle list ('Running','Non Optimized','Optimized').
        '''
        for scheduledPhase in scheduledCycleList:
            self.__addRowToCycleResultsTable(scheduledPhase.componentName, scheduledPhase.cycleName, scheduledPhase.name,
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                                         time.localtime(scheduledPhase.scheduledStartDT)),
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                                         time.localtime(scheduledPhase.scheduledEndDT)),
                                           Status)

    def __addRowToCycleResultsTable(self, Component_name, Cycle_name, Subphase_name, start, end, status):
        rowPos = self.tblCycleResults.rowCount()

        self.tblCycleResults.insertRow(rowPos)
        self.tblCycleResults.setItem(rowPos, 0, QTableWidgetItem(Component_name))
        self.tblCycleResults.setItem(rowPos, 1, QTableWidgetItem(Cycle_name))
        self.tblCycleResults.setItem(rowPos, 2, QTableWidgetItem(Subphase_name))
        self.tblCycleResults.setItem(rowPos, 3, QTableWidgetItem(start))
        self.tblCycleResults.setItem(rowPos, 4, QTableWidgetItem(end))
        self.tblCycleResults.setItem(rowPos, 5, QTableWidgetItem(status))

    def plotOnGraphOptimized(self):

        #Plot Tank Level Curve on grphViewTankLevel
        self.legend.scene().removeItem(self.legend)
        self.legend = self.grphViewTankLevel.addLegend(size=(50, 100), offset=(-10, -100))
        self.grphViewTankLevel.clear()
        self.grphViewTankLevel.setBackground('w')
        self.grphViewTankLevel.setTitle('Tank level predicted on the ' + str(Constants.NUMBER_OF_15MIN_TICKS / 4) + ' following hours')
        self.grphViewTankLevel.setLabel('left', 'Tank Level', units='L')
        self.grphViewTankLevel.setLabel('bottom', 'Time', units='min')

        X = [15.0*i for i in range(Constants.NUMBER_OF_15MIN_TICKS+1)]
        listOfTimeUnitTicks=[(x,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.actualTime+x*60))) for x in X[::16]]

        typeWidget=type(self.grphViewTankLevel)
        self.plot = self.grphViewTankLevel.plot( X,2000 * np.ones(len(X)),
                                                pen=mkPen('r', width=5), name="Threshold")

        self.plot = self.grphViewTankLevel.plot(X,self.TankLevelOptimized,
                                                symbol='o', symbolBrush='r'
                                                , symbolSize=7, pen=mkPen('r', width=5), name="Tank level")

        ax = self.grphViewTankLevel.getAxis('bottom')
        ax.setTicks([listOfTimeUnitTicks])

        #Plot Schedule barplots on grphViewSchedule
        listOfComponentsTicks=[]
        self.grphViewSchedule.clear()
        self.grphViewSchedule.setBackground('w')
        for i in range(len(self.runningCyclesList)):
            bgplot=self.getBarPlotItem(self.runningCyclesList[i],'b')
            self.grphViewSchedule.getPlotItem().addItem(bgplot)
            listOfComponentsTicks.append(self.getItemTick(self.runningCyclesList[i]))
        for i in range(len(self.optimizedCyclesList)):
            bgplot = self.getBarPlotItem( self.optimizedCyclesList[i],'g')
            self.grphViewSchedule.getPlotItem().addItem(bgplot)
            listOfComponentsTicks.append(self.getItemTick(self.optimizedCyclesList[i]))
        for i in range(len(self.nonoptimizedCyclesList)):
            bgplot = self.getBarPlotItem(self.nonoptimizedCyclesList[i],'r')
            self.grphViewSchedule.getPlotItem().addItem(bgplot)
            listOfComponentsTicks.append(self.getItemTick(self.nonoptimizedCyclesList[i]))

        ax = self.grphViewSchedule.getAxis('left')
        ax.setTicks([listOfComponentsTicks])
        ax = self.grphViewSchedule.getAxis('bottom')
        ax.setTicks([listOfTimeUnitTicks])


    def getBarPlotItem(self,scheduledPhase,color):
        barplot=BarGraphItem(x=[-self.context.cyclenameToIndex(scheduledPhase.componentName, scheduledPhase.cycleName, scheduledPhase.name)],
                     height=[(scheduledPhase.scheduledEndDT - scheduledPhase.scheduledStartDT)/60],
                     y0=(scheduledPhase.scheduledStartDT-self.actualTime)/60, width=0.6, brush=color)
        barplot.rotate(-90)
        return barplot

    def getItemTick(self,scheduledPhase):
         return (self.context.cyclenameToIndex(scheduledPhase.componentName, scheduledPhase.cycleName, scheduledPhase.name),
                      scheduledPhase.componentName + '\n' + scheduledPhase.cycleName + '\n' + scheduledPhase.name)

    def exportPlanToCsv(self):
        rowCnt = self.tblCycleResults.rowCount()
        if rowCnt > 0:
            Table = []
            for i in range(rowCnt):
                colCnt = self.tblCycleResults.columnCount()
                Row = []
                for j in range(colCnt):
                    element = self.tblCycleResults.item(i, j).text()
                    Row.append(element)
                Table.append(Row)
            # Save results
            #folderdialog=QFileDialog()
            #folderPath =str(QFileDialog.getExistingDirectory(folderdialog, CyclePhaseWriter.DIRSELECT_TITLE))
            fileName = CyclePhaseWriter.getfileName(self.actualTime)
            filePath=self.saveFileDialog(fileName)

            if not filePath or filePath=='':
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(CyclePhaseWriter.MSG_EXPORT_CANCEL)
                msg.setInformativeText(CyclePhaseWriter.MSG_EXPORT_INFO_CANCEL)
                msg.setWindowTitle(CyclePhaseWriter.MSG_EXPORT_TITLE)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                CyclePhaseWriter.writeOnExcel(filePath,Table)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(CyclePhaseWriter.MSG_EXPORT_TEXT)
                msg.setInformativeText(CyclePhaseWriter.MSG_EXPORT_INFO + filePath)
                msg.setWindowTitle(CyclePhaseWriter.MSG_EXPORT_TITLE)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(CyclePhaseWriter.MSG_EXPORT_WARNING_TEXT)
            msg.setInformativeText(CyclePhaseWriter.MSG_EXPORT_WARNING_INFO)
            msg.setWindowTitle(CyclePhaseWriter.MSG_EXPORT_WARNING_TITLE)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


    def saveFileDialog(self,fileName):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        try:
            filePath, _ = QFileDialog.getSaveFileName(self.centralWidget, CyclePhaseWriter.DIRSELECT_TITLE, fileName, options=options)
        except Exception as e:
            print(e)

        return filePath