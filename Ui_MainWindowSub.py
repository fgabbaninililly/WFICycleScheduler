from mainwindow import Ui_MainWindow
from Ui_AddCyclePanelSub import Ui_AddCyclePanelSub
from OptimizerFunctions import *

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5 import QtCore, QtWidgets

import time
import pyqtgraph as pg

#Optimizer's packages
from scipy.optimize import minimize
from scipy.optimize import Bounds

class RequestedItem:
    componentName = ""
    cycleName = ""
    startDT = time.time()
    endDT = time.time()
    isOptimized = 0

class Ui_MainWindowSub(Ui_MainWindow):

    TBL_ADDCYCLE_COL_IDX_COMPONENT = 0
    TBL_ADDCYCLE_COL_IDX_CYCLE = 1
    TBL_ADDCYCLE_COL_IDX_STARTDT = 2
    TBL_ADDCYCLE_COL_IDX_ENDDT = 3
    TBL_ADDCYCLE_COL_IDX_ISOPTIMIZED = 4

    def setupUi(self, MainWindow):
        super(Ui_MainWindowSub, self).setupUi(MainWindow)

    def __init__(self):
        super(Ui_MainWindowSub, self).__init__()

    def retranslateUi(self, MainWindow):
        #call method on super class
        super(Ui_MainWindowSub, self).retranslateUi(MainWindow)
        #add any other code here
        self.btnAddCycle.clicked.connect(self.openAddCycleDialog)
        self.dialog=Ui_AddCyclePanelSub()
        self.btnCalculateLevel.clicked.connect(self.updatePlan)
        self.btnCalculateLevel.clicked.connect(self.plotOnGraphOptimized)
        self.legend = self.grphViewTankLevel.addLegend(size=(50, 100), offset=(-10, -100))

    def plotOnGraphOptimized(self):
        self.legend.scene().removeItem(self.legend)
        self.legend = self.grphViewTankLevel.addLegend(size=(50, 100), offset=(-10, -100))
        self.grphViewTankLevel.clear()
        self.set_RunningCC()
        self.set_RuCC()
        self.grphViewTankLevel.setBackground('w')
        self.grphViewTankLevel.setTitle('Tank level predicted on the '+ str(nb15min/4)+' following hours')
        self.grphViewTankLevel.setLabel('left','Tank Level',units='L')
        self.grphViewTankLevel.setLabel('bottom','Time',units='min')
        TL=Compute_tank_level2(self.optimized_Time)
        self.plot = self.grphViewTankLevel.plot(listOfTimeUnitTicks, 2000 * np.ones(len(listOfTimeUnitTicks)),
                                                pen=pg.mkPen('r', width=5), name="Threshold")
        self.plot=self.grphViewTankLevel.plot(listOfTimeUnitTicks, Compute_tank_level2(self.optimized_Time), symbol='o', symbolBrush='r'
                                              , symbolSize=7, pen=pg.mkPen('r', width=5), name="Tank level")
        for i in range(self.nbRunningCycles):
            color=pg.mkColor((255/self.nbRunningCycles*i,100,100))
            self.grphViewTankLevel.plot(listOfTimeUnitTicks, self.RunningCC[i], symbol='o', symbolSize=7, symbolBrush=color, pen=pg.mkPen(color, width=3)
                                        , name=['Running: ' + r['Component'] +' running with '+r['Value'] for i,r in self.RunningCycles.iterrows()][i])
        # Requested Cycles (opti non checked)
        list_Request_index = [Cyclename_to_index(r['Component'], r['Cycle']) for r in self.requests]
        RequestCC = CycleConsumption(Du[list_Request_index], De[list_Request_index],
                                     self.Trequest, CF[list_Request_index], len(self.requests))
        for i in range(len(self.requests)):
            color=pg.mkColor((100, 100, 255 / len(self.requests) * i))
            self.grphViewTankLevel.plot(listOfTimeUnitTicks, RequestCC[i], symbol='o', symbolSize=7, symbolBrush=color, pen=pg.mkPen(color, width=3)
                                        , name=['Request: ' + request['Component'] +' running with ' + request['Cycle'] for request in self.requests][i])

        # Requested Cycles (opti checked)
        list_Request_index = [Cyclename_to_index(r['Component'], r['Cycle']) for r in self.optimizedRequests]
        optiRequestCC = CycleConsumption(Du[list_Request_index], De[list_Request_index],
                                         (np.array(self.optimized_Time) - self.actualTime * np.ones(len(self.optimized_Time))) / 60,
                                         CF[list_Request_index], len(self.optimizedRequests))
        for i in range(len(self.optimizedRequests)):
            color=pg.mkColor((100, 255 / len(self.optimizedRequests) * i, 100))
            self.grphViewTankLevel.plot(listOfTimeUnitTicks, optiRequestCC[i], symbol='o', symbolSize=7, symbolBrush=color,
                                        pen=pg.mkPen(color, width=3)
                                        , name=
                                   ['Request: ' + request['Component'] + ' running with ' + request['Cycle'] for
                                    request in self.optimizedRequests][i])

    def openAddCycleDialog(self):
        addCycleDialog = QtWidgets.QDialog()
        ui = Ui_AddCyclePanelSub()
        ui.setupUi(addCycleDialog)
        addCycleDialog.exec()
        if (ui.accepted_input)&(ui.getComponent()!= ''):
            self.addCycleToTable(ui.getComponent(), ui.getCycle(), ui.getStart(), ui.getEnd())

    def removeCurrentRow(self):
        selectedRow = self.tblAddCycle.currentRow()
        self.tblAddCycle.removeRow(selectedRow)

    """
    def testSetupTable(self):
        for i in range(3):
            self.addRowtblAddCycle("text " + str(i), "text " + str(i),"text " + str(i),"text " + str(i))
    """

    def SetRunningCycles(self):
        self.RunningCycles=get_Running_Cycles()
        self.nbRunningCycles=len(self.RunningCycles)

    def setOptimizedRequests(self):
        self.optimizedRequests=self.getOptimizedRequestsFromTable()

    def setRequests(self):
        self.requests = self.getRequestsFromTable()

    def addCycleToTable(self, Component_name, Cycle_name, start, end):
        rowPos = self.tblAddCycle.rowCount()

        button = QtWidgets.QPushButton(self.tblAddCycle)
        button.setGeometry(QtCore.QRect(60, 10, 75, 23))
        button.setObjectName("button")
        button.setText("Remove ")

        checkbox = QtWidgets.QCheckBox(self.tblAddCycle)
        checkbox.setGeometry(QtCore.QRect(60, 10, 75, 23))
        checkbox.setObjectName("checkbox")

        button.clicked.connect(self.removeCurrentRow)
        #button.clicked.connect(self.update_Plan)

        self.tblAddCycle.insertRow(rowPos)
        itemComponent= QTableWidgetItem(Component_name)
        itemComponent.setFlags(itemComponent.flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, 0, itemComponent)
        itemcycle= QTableWidgetItem(Cycle_name)
        itemcycle.setFlags(itemcycle.flags() & ~QtCore.Qt.ItemIsEditable)
        self.tblAddCycle.setItem(rowPos, 1, itemcycle)
        itemstart=QTableWidgetItem(start)
        #itemstart.itemChanged.connect(self.check_TimeEdit_validity)
        self.tblAddCycle.setItem(rowPos, 2, itemstart)
        itemend=QTableWidgetItem(end)
        #itemend.itemChanged.connect(self.check_TimeEdit_validity)
        self.tblAddCycle.setItem(rowPos, 3, itemend)
        self.tblAddCycle.setCellWidget(rowPos, 4, checkbox)
        self.tblAddCycle.setCellWidget(rowPos, 5, button)

    def addRowToCycleResultsTable(self, Component_name, Cycle_name, start, end, status):
        rowPos = self.tblCycleResults.rowCount()

        self.tblCycleResults.insertRow(rowPos)
        self.tblCycleResults.setItem(rowPos, 0, QTableWidgetItem(Component_name))
        self.tblCycleResults.setItem(rowPos, 1, QTableWidgetItem(Cycle_name))
        self.tblCycleResults.setItem(rowPos, 2, QTableWidgetItem(start))
        self.tblCycleResults.setItem(rowPos, 3, QTableWidgetItem(end))
        self.tblCycleResults.setItem(rowPos, 4, QTableWidgetItem(status))

    def updatePlan(self):
        self.actualTime=time.time()
        self.clearPlan()
        self.set_startTanklevel()
        self.SetRunningCycles()
        self.setRequests()
        self.setOptimizedRequests()
        self.set_RunningCC()
        self.set_RqCC()
        self.set_RuCC()
        self.set_globalVariables_for_opti()
        self.init_optimized_Time()
        for i,runningC in self.RunningCycles.iterrows():
            self.addRowToCycleResultsTable(runningC['Component'], runningC['Value'],
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                                         time.localtime(self.actualTime)),
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                                         time.localtime(self.actualTime + 60 * runningC['TimeLeftminutes'])),
                              'Running')
        self.Trequest = []
        for requestC in self.requests:
            self.addRowToCycleResultsTable(requestC['Component'], requestC['Cycle'],
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(requestC['t1'])),
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(requestC['t1']+
                                            +De[Cyclename_to_index(requestC['Component'], requestC['Cycle'])]*60
                                            +Du[Cyclename_to_index(requestC['Component'],
                                            requestC['Cycle'])]*60))
                                           ,'Request')
            self.Trequest.append((requestC['t1'] - self.actualTime) / 60)

        if len(self.optimizedRequests)>0:
            #OPTIMIZATION- may take some time
            s=time.time()
            self.get_optimized_Time()
            e=time.time()
            print('Optimization completed in '+str(e-s)+' seconds')

        for i,requestC in zip(range(len(self.optimizedRequests)), self.optimizedRequests):
            self.addRowToCycleResultsTable(requestC['Component'], requestC['Cycle'],
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.optimized_Time[i])),
                                           time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime(self.optimized_Time[i]
                                                           + De[Cyclename_to_index(requestC['Component'],
                                                                                   requestC['Cycle'])] * 60
                                                           + Du[Cyclename_to_index(requestC['Component'],
                                                                                   requestC['Cycle'])] * 60))
                                           , 'Request optimised')

    def clearPlan(self):
        while (self.tblCycleResults.rowCount() > 0):
            self.tblCycleResults.removeRow(0)

    def getCycleTableItem(self, i, j):
        return self.tblAddCycle.item(i,j)

# refactor these into a single call; use class RequestedItem to model a requested cycle
    def getRequestsFromTable(self):
        act_time=time.time()
        requestList = []
        rowCnt = self.tblAddCycle.rowCount()
        for i in range(rowCnt):
            requestItem = {}
            if (self.getCycleTableItem(i, 0).text()!= '')&(not(self.tblAddCycle.cellWidget(i, 4).isChecked())):
                requestItem['Component']=self.getCycleTableItem(i, 0).text()
                requestItem['Cycle']=self.getCycleTableItem(i, 1).text()
                requestItem['Flow']=CF[Cyclename_to_index(self.getCycleTableItem(i, 0).text(), self.getCycleTableItem(i, 1).text())]
                requestItem['t1']=float(time.mktime(time.strptime(
                    self.getCycleTableItem(i, 2).text(), "%Y-%m-%d %H:%M:%S")))
                requestItem['t2']=float(time.mktime(time.strptime(
                    self.getCycleTableItem(i, 3).text(), "%Y-%m-%d %H:%M:%S")))
                requestList.append(requestItem)
        return requestList

    def getOptimizedRequestsFromTable(self):
        act_time=time.time()
        REQUESTS=[]
        RowCount=self.tblAddCycle.rowCount()
        for i in range(RowCount):
            Request = {}
            if (self.getCycleTableItem(i, 0).text()!= '')&(self.tblAddCycle.cellWidget(i, 4).isChecked()):
                Request['Component']=self.getCycleTableItem(i, 0).text()
                Request['Cycle']=self.getCycleTableItem(i, 1).text()
                Request['Flow']=CF[Cyclename_to_index(self.getCycleTableItem(i, 0).text(), self.getCycleTableItem(i, 1).text())]
                Request['t1']=float(time.mktime(time.strptime(
                    self.getCycleTableItem(i, 2).text(), "%Y-%m-%d %H:%M:%S")))
                Request['t2']=float(time.mktime(time.strptime(
                    self.getCycleTableItem(i, 3).text(), "%Y-%m-%d %H:%M:%S")))
                REQUESTS.append(Request)
        return REQUESTS

    def init_optimized_Time(self):
        self.optimized_Time=[(request['t1'] - self.actualTime) / 60 for request in self.optimizedRequests]

    # Getting the information to pass into the function to optimize (we can't put self in argument)
    # We define the global variables
    def set_globalVariables_for_opti(self):
        global startTankLevel
        startTankLevel = self.startTankLevel
        global optimizedREQUESTS
        optimizedREQUESTS = self.optimizedRequests
        global RuCC
        RuCC = self.RuCC
        global RqCC
        RqCC = self.RqCC
        global act_time
        act_time=self.actualTime

    def get_optimized_Time(self):
        self.optimized_Time=OPTIMISATION(self.optimizedRequests)

    def set_RunningCC(self):
        ##Running parameters
        nbRunningCycles = len(self.RunningCycles)
        if nbRunningCycles > 0:
            RunningCyclesFlow = [CF[Cyclename_to_index(r['Component'], r['Value'])] for i, r in
                                 self.RunningCycles.iterrows()]
            RunningCyclesDelays = [max(0, (r['TimeLeftminutes'] - r['Duration'])) for i,r in self.RunningCycles.iterrows()]
            RunningCyclesDurations = [min(r['TimeLeftminutes'], r['Duration']) for i,r in self.RunningCycles.iterrows()]
        else:
            RunningCyclesFlow = []
            RunningCyclesDurations = []
            RunningCyclesDelays = []
        self.RunningCC = CycleConsumption(RunningCyclesDurations, RunningCyclesDelays, np.zeros(nbRunningCycles),
                                     RunningCyclesFlow, nbRunningCycles)

    def set_startTanklevel(self):
        self.startTankLevel=get_Tank_level()

    def set_RuCC(self):
        if len(self.RunningCC) > 0:
            self.RuCC = sum([runningCC for runningCC in self.RunningCC])
        else:
            self.RuCC = np.zeros(nb15min + 1)

    def set_RqCC(self):
        ##Request parameters
        nbRequestCycles = len(self.requests)
        if nbRequestCycles > 0:
            RequestCyclesFlow = [CF[Cyclename_to_index(r['Component'], r['Cycle'])] for r in
                                 self.requests]
            RequestCyclesDelays = [De[Cyclename_to_index(r['Component'], r['Cycle'])] for r in
                                   self.requests]
            RequestCyclesDurations = [Du[Cyclename_to_index(r['Component'], r['Cycle'])] for r in
                                      self.requests]
            RequestStartTime= (np.array([r['t1'] for r in self.requests]) - self.actualTime * np.ones(nbRequestCycles)) / 60
        else:
            RequestCyclesFlow = []
            RequestCyclesDurations = []
            RequestCyclesDelays = []
            RequestStartTime=[]
        self.RequestCC = CycleConsumption(RequestCyclesDurations, RequestCyclesDelays, RequestStartTime,
                                          RequestCyclesFlow, nbRequestCycles)
        if len(self.RequestCC) > 0:
            self.RqCC = sum([requestCC for requestCC in self.RequestCC])
        else:
            self.RqCC = np.zeros(nb15min + 1)



######### Optimisation ########
def OPTIMISATION(optirequests):
    N=len(optirequests)
    u=np.random.uniform(0,1,(N,len(optirequests)))
    X0=[[u[i,j]*(optirequests[j]['t2']-optirequests[j]['t1'])+optirequests[j]['t1'] for j in range(len(optirequests))] for i in range(N)]
    optfun=10000
    RequestLB = [request['t1'] for request in optirequests]
    list_Request_index = [Cyclename_to_index(r['Component'], r['Cycle']) for r in optirequests]
    RequestDurations=[Du[i] for i in list_Request_index]
    RequestDelays=[De[i] for i in list_Request_index]
    RequestUB = np.array([request['t2'] for request in optirequests]) - (np.array(RequestDurations) + np.array(RequestDelays))*60
    for x0 in X0:
        bounds=Bounds(lb=RequestLB ,ub=RequestUB ,keep_feasible=False)
        Solution=minimize(min_Compute_tank_level2,x0,bounds=bounds,method='SLSQP')
        if Solution['fun']<optfun:
            RequestStartTime=Solution['x']
            optfun=Solution['fun']

    return RequestStartTime

def min_Compute_tank_level2(T):
    L = Compute_tank_level2(T)
    return -min(L)

def Compute_tank_level2(T):
    L = np.zeros(nb15min + 1)
    L[0] = startTankLevel
    r=RqCC[0]
    list_Request_index = [Cyclename_to_index(r['Component'], r['Cycle']) for r in optimizedREQUESTS]
    optiRequestCC = CycleConsumption(Du[list_Request_index], De[list_Request_index],
                                     (np.array(T) - act_time * np.ones(
                                         len(T))) / 60,
                                     CF[list_Request_index], len(optimizedREQUESTS))
    if len(optiRequestCC) > 0:
        optiRqCC = sum([optirequestCC for optirequestCC in optiRequestCC])
    else:
        optiRqCC = np.zeros(nb15min + 1)
    L[1] = (L[0] + get_MS1_active() * MS1F + get_MS2_active() * MS2F - CU
            - RuCC[0] - RqCC[0] - optiRqCC[0])
    for i in range(2, nb15min + 1):
        L[i] = (L[i - 1] + int(L[i - 1] < TC - MS1F) * MS1F + int(L[i - 1] < TC - MS1F - MS2F) * MS2F - CU
                - RuCC[i - 1] - RqCC[i - 1] - optiRqCC[i-1])
    return L