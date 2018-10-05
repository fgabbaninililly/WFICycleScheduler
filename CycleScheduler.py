import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds

from DataModel import *
from PIDataReadFunctions import *
from copy import deepcopy

class TagsReader:
    SHEET_NAME = 'Sheet1'
    COLNAME_COMPONENT = 'Component'
    COLNAME_TAG = 'Tag List'

    @staticmethod
    def loadFromExcel(filePath):
        tags = pd.read_excel(filePath, sheet_name=TagsReader.SHEET_NAME)
        return tags

class CyclePhaseReader:
    SHEET_NAME = 'Cycles'
    COLNAME_COMPONENT = 'Component'
    COLNAME_CYCLE = 'Cycle'
    COLNAME_PHASE = 'SubPhase'
    COLNAME_DURATION = 'Duration (m)'
    COLNAME_CONSUMPTION = 'WFI Flow OSI_PI o rossi (l/15min)'
    COLNAME_DELAY = 'delay from start cycle (m)'

    @staticmethod
    def loadFromExcel(filePath):
        cyclePhaseParams = pd.read_excel(filePath, sheet_name=CyclePhaseReader.SHEET_NAME)
        return cyclePhaseParams


class ConstantsReader:
    SHEET_NAME = 'Constants'
    COLNAME_NAME = 'CName'
    COLNAME_VALUE = 'CValue'

    ROWNAME_MS1VALUE = 'MS1_Flow'
    ROWNAME_MS2VALUE = 'MS2_Flow'
    ROWNAME_TANKCAPACITY = 'Tank_Capacity'
    ROWNAME_BASELINE_USAGE = 'Constant_usage'

    @staticmethod
    def loadFromExcel(filePath):
        modelConstants = pd.read_excel(filePath, sheet_name=ConstantsReader.SHEET_NAME, names =[ConstantsReader.COLNAME_NAME, ConstantsReader.COLNAME_VALUE], header=None)
        return modelConstants

class CyclePhaseWriter:
    SHEET_NAME = 'WFIScheduleSheet'
    ENGINE_NAME='xlsxwriter'
    COLNAME_COMPONENT = 'Component'
    COLNAME_CYCLE = 'Cycle'
    COLNAME_SUBPHASE = 'SubPhase'
    COLNAME_START = 'Start'
    COLNAME_END = 'End'
    COLNAME_STATUS = 'Status'

    MSG_EXPORT_TEXT = "The plan has been exported"
    MSG_EXPORT_INFO = "To excel file : "
    MSG_EXPORT_TITLE="Export results"

    MSG_EXPORT_WARNING_TEXT = "The plan is not initialised"
    MSG_EXPORT_WARNING_INFO = "No excel file is exported \nTo initialize plan click on \n'Calculate tank level'"
    MSG_EXPORT_WARNING_TITLE = "Export results"

    MSG_EXPORT_CANCEL= "The export has been cancelled"
    MSG_EXPORT_INFO_CANCEL= "No folder selected"

    DIRSELECT_TITLE="Select Directory"

    @staticmethod
    def writeOnExcel(filePath,Table):
        # Save results
        writer = pd.ExcelWriter(filePath,engine=CyclePhaseWriter.ENGINE_NAME)
        pd.DataFrame(Table, columns=[CyclePhaseWriter.COLNAME_COMPONENT, CyclePhaseWriter.COLNAME_CYCLE, CyclePhaseWriter.COLNAME_SUBPHASE, CyclePhaseWriter.COLNAME_START, CyclePhaseWriter.COLNAME_END, CyclePhaseWriter.COLNAME_STATUS]).to_excel(
            writer, sheet_name=CyclePhaseWriter.SHEET_NAME)
        writer.save()

    @staticmethod
    def getfileName(actualTime):
        return "/ScheduleWFI_" + time.strftime('%Y-%m-%d_%Hh%Mm%Ss',time.localtime(actualTime)) + '.xlsx'

#######################################################################################################################

class ConfigurationParameters:
    """
    Parameters is used to store
    - cycle phase parameters (from Variablex.xlsx, sheet "Cycles")
    - constants (from Variablex.xlsx, sheet "Constants")
    - tags (from Tags.xlsx)

    Attributes:
        cyclePhaseParameters: parameters describing cycle phases (component, cycle, phase, duration, consumption of WFI, delay)
        constants: constants describing the process (tank re-fill rate, thresholds for tank activation)
        tags: tag names (used for reading cycle phases already running)
    """

    cyclePhaseParams = None
    constants = None
    tags = None

    @staticmethod
    def createFromExcel(parameterFile, tagFile):
        configurationParameters = ConfigurationParameters()
        configurationParameters.setCyclePhaseParams(CyclePhaseReader.loadFromExcel(parameterFile))
        configurationParameters.setConstants(ConstantsReader.loadFromExcel(parameterFile))
        configurationParameters.setTags(TagsReader.loadFromExcel(tagFile))
        return configurationParameters

    def setCyclePhaseParams(self, cyclePhaseParams):
        self.cyclePhaseParams = cyclePhaseParams

    def setConstants(self, constants):
        self.constants = constants

    def setTags(self, tags):
        self.tags = tags

    def getComponents(self):
        return np.array(list(self.cyclePhaseParams[CyclePhaseReader.COLNAME_COMPONENT]))

    def getCycles(self):
        return np.array(list(self.cyclePhaseParams[CyclePhaseReader.COLNAME_CYCLE]))

    def getSubPhases(self):
        return np.array(list(self.cyclePhaseParams[CyclePhaseReader.COLNAME_PHASE]))

    def getDurations(self):
        return self.cyclePhaseParams[CyclePhaseReader.COLNAME_DURATION]

    def getDelays(self):
        return self.cyclePhaseParams[CyclePhaseReader.COLNAME_DELAY]

    def getWFIConsumptions(self):
        return self.cyclePhaseParams[CyclePhaseReader.COLNAME_CONSUMPTION]

# get constants

    def getMS1Flow(self):
        return float(self.constants.loc[self.constants[ConstantsReader.COLNAME_NAME] == ConstantsReader.ROWNAME_MS1VALUE][ConstantsReader.COLNAME_VALUE])

    def getMS2Flow(self):
        return float(self.constants.loc[self.constants[ConstantsReader.COLNAME_NAME] == ConstantsReader.ROWNAME_MS2VALUE][ConstantsReader.COLNAME_VALUE])

    def getTankCapacity(self):
        return float(self.constants.loc[self.constants[ConstantsReader.COLNAME_NAME] == ConstantsReader.ROWNAME_TANKCAPACITY][ConstantsReader.COLNAME_VALUE])

    def getBaselineUsage(self):
        return float(self.constants.loc[self.constants[ConstantsReader.COLNAME_NAME] == ConstantsReader.ROWNAME_BASELINE_USAGE][ConstantsReader.COLNAME_VALUE])

# get tags
    def getTagComponents(self):
        return self.tags[TagsReader.COLNAME_COMPONENT]

    def getTags(self):
        return self.tags[TagsReader.COLNAME_TAG]

#######################################################################################################################

class Constants:
    COMPONENT_NAME_RRU = 'RRU'

    MSG_ENTER_DURATION_RRU = 'Enter Duration of cycle RRU CARTRIDGES, in minutes'
    MSG_DURATION_RRU = 'RRU duration is specified by Start and End bounds'
    MSG_CANNOT_OPTIMIZE_CYCLE = 'This cycle will not optimized'

    NUMBER_OF_15MIN_TICKS = 24*4


class Context:
    """
    Includes all the information needed to retrieve cycle phases that are already running and generate a schedule for a 
    given set of cycle phases.
    Process related parameters are available through the Parameters class.
    
    Attributes:
        configurationParameters: instance of a ConfigurationParameter class containing parameters and constants stored on Excel configuration files 
    """

    configurationParameters = ConfigurationParameters()
    requestedCyclePhases = []
    id = 0

    def initFromContext(self,context):
        self.configurationParameters=deepcopy(context.configurationParameters)
        self.requestedCyclePhases=deepcopy(context.requestedCyclePhases)
        self.id=deepcopy(context.id)

    def setConfigurationParameters(self, configParameters):
        self.configurationParameters = configParameters

    def cyclenameToIndex(self, componentName, cycleName, subphaseName):
        return list(set(np.where(self.configurationParameters.getComponents() == componentName)[0]) &
                    set(np.where(self.configurationParameters.getCycles() == cycleName)[0]) &
                    set(np.where(self.configurationParameters.getSubPhases() == subphaseName)[0]))[0]

    def getNextId(self):
        self.id = self.id + 1
        return self.id

    def addRequestedCyclePhase(self, requestedCyclePhase):
        self.requestedCyclePhases.append(requestedCyclePhase)

    def removeRequestedCyclePhase(self, requestedCyclePhase):
        for reqPhases in self.requestedCyclePhases:
            if (reqPhases.isEqual(requestedCyclePhase)):
                self.requestedCyclePhases.remove(reqPhases)
                return

    def removeRequestedCyclePhaseId(self, id):
        for reqPhase in self.requestedCyclePhases:
            if (reqPhase.id == id):
                self.requestedCyclePhases.remove(reqPhase)
                return

    def getCyclePhaseFromNames(self, componentName, cycleName, subphaseName):
        index = self.cyclenameToIndex(componentName, cycleName, subphaseName)
        cyclePhase = Phase()
        cyclePhase.componentName = self.configurationParameters.getComponents()[index]
        cyclePhase.cycleName = self.configurationParameters.getCycles()[index]
        cyclePhase.name = self.configurationParameters.getSubPhases()[index]
        cyclePhase.duration = self.configurationParameters.getDurations()[index]
        cyclePhase.delay = self.configurationParameters.getDelays()[index]
        cyclePhase.wfiConsumption = self.configurationParameters.getWFIConsumptions()[index]
        return cyclePhase

    def getCyclePhaseFromId(self, id):
        for reqPhase in self.requestedCyclePhases:
            if (reqPhase.id == id):
                return reqPhase

    def cycleConsumesWater(self, componentName, cycleName):
        return (componentName in self.configurationParameters.getComponents()) & (cycleName in self.configurationParameters.getCycles())


class CycleScheduler :

    def scheduleCycleRequests(self,runningCyclesList,tankLevel,MS1Active,MS2Active,actualTime,context):
        """
        Schedules cycles contained in the cycle list in time. 
        Cycles that are not optimized (isOptimized = 0) are scheduled to start exactly at the time specified by startDT.
        Cycles that are optimized (isOptimized = 1) are scheduled to start at time scheduledStartDT. 
        This time is chosen so that:
        - scheduledStartDT + [cycle duration] <= endDT
        - the minimum level of water in the WFI tank is maximized
        
        Maximization of the minimum level of water in the tank is performed by an optimization algorithm invoked in [...]
        
        :param runningCyclesList: list of cycles phases are running according to OSIPI information
        :param tankLevel: Current Scalar value fo the water level (in L) of the tank
        :param MS1Active,MS2Active: ctivity of filling machines 1 and 2 at the start of optimisation
        :param actualTime: start of the update of the Plan
        :param context: context containing the requested cycles and the configuration parameters
        :return: scheduledCycleList: list of cycles phases scheduled in time. List contains instances of ScheduledCyclePhase class. 
            Includes cycles that were running at the time when this method was launched
        """
        requestedCycleList=context.requestedCyclePhases
        self.__setGlobals(runningCyclesList,tankLevel,MS1Active,MS2Active,actualTime,context)
        RequestOptimizedScheduledStartTime,TankLevelOptimized=self.__optimize()

        #From the Optimized Time Scheduled and the Request Cycle List, we build Optimized Request Cycle List.
        idxOpt = 0
        scheduledCycleList = list()
        for requestedCycle in requestedCycleList:
            scheduledCycle= ScheduledPhase()
            scheduledCycle.initFromRequestedPhase(requestedCycle)
            scheduledCycleList.append(scheduledCycle)
            if (scheduledCycle.isOptimized == 0):
                scheduledCycle.scheduledStartDT = scheduledCycle.startDT
                scheduledCycle.scheduledEndDT = scheduledCycle.scheduledStartDT+(scheduledCycle.delay+scheduledCycle.duration)*60
            else:
                scheduledCycle.scheduledStartDT = RequestOptimizedScheduledStartTime[idxOpt]
                scheduledCycle.scheduledEndDT = scheduledCycle.scheduledStartDT+(scheduledCycle.delay+scheduledCycle.duration)*60
                idxOpt = idxOpt + 1

        return scheduledCycleList,TankLevelOptimized


    def __setGlobals(self, runningCyclesList,tankLevel,MS1Active,MS2Active,actualTime,context):
        #To global the actual time defined by the start of the update of the Plan
        global GLB_ActualTime
        GLB_ActualTime = actualTime

        #To global information from OSIPI: tank level, activity of filling machines MS1 and MS2
        global GLB_StartTankLevel
        GLB_StartTankLevel = tankLevel
        global GLB_MS1Active
        GLB_MS1Active=MS1Active
        global GLB_MS2Active
        GLB_MS2Active=MS2Active

        #To global the set of constant values in WFI Simulation
        global GLB_TankCapacity
        GLB_TankCapacity=context.configurationParameters.getTankCapacity()
        global GLB_MS1Flow
        GLB_MS1Flow=context.configurationParameters.getMS1Flow()
        global GLB_MS2Flow
        GLB_MS2Flow=context.configurationParameters.getMS2Flow()
        global GLB_BaselineUsage
        GLB_BaselineUsage=context.configurationParameters.getBaselineUsage()
        global GBL_NUMBER_OF_15MIN_TICKS
        GBL_NUMBER_OF_15MIN_TICKS=Constants.NUMBER_OF_15MIN_TICKS

        # This preprocessing is necessary to optimize the simulation of WFI level using scipy libraries
        #Building list to distinguish Request to Optimize from Request not to Optimize
        requestedCycleList = context.requestedCyclePhases
        REQUESTSToOptimize = []
        for reqPhase in requestedCycleList:
            if (reqPhase.isOptimized == 1):
                REQUESTSToOptimize.append(reqPhase)
        REQUESTSNotToOptimize = []
        for reqPhase in requestedCycleList:
            if (reqPhase.isOptimized == 0):
                REQUESTSNotToOptimize.append(reqPhase)
        #Computing the total consumption of running and requests cycles not to optimize
        if len(runningCyclesList + REQUESTSNotToOptimize)>0:
            ConsumptionForNonOptCycles = CycleScheduler.CycleConsumption(runningCyclesList + REQUESTSNotToOptimize,
                                                                         [runningCycle.startDT for runningCycle in runningCyclesList]+
                                                                         [RequestotToOptimize.startDT for RequestotToOptimize in
                                                                          REQUESTSNotToOptimize])
            totalConsumptionForNonOptCycles = sum([consumptionfornonoptcycle for consumptionfornonoptcycle in ConsumptionForNonOptCycles])
        else:
            totalConsumptionForNonOptCycles=np.zeros( GBL_NUMBER_OF_15MIN_TICKS + 1)
        #To global the requests to optimize and the total consumption of running and requests cycles not to optimize
        global GLB_REQUESTSToOptimize
        GLB_REQUESTSToOptimize = REQUESTSToOptimize
        global GLB_TotalConsumptionForNonOptCycles #array of total consumption values, sampled every 15min (inlcudes, both running and requested cycles with no optimization)
        GLB_TotalConsumptionForNonOptCycles = totalConsumptionForNonOptCycles

    def __optimize(self):
        RequestStartTime=[]
        N = len(GLB_REQUESTSToOptimize)**2
        u = np.random.uniform(0, 1, (N, len(GLB_REQUESTSToOptimize)))
        X0 = [[u[i, j] * (GLB_REQUESTSToOptimize[j].endDT - GLB_REQUESTSToOptimize[j].startDT) + GLB_REQUESTSToOptimize[j].startDT for j in
               range(len(GLB_REQUESTSToOptimize))] for i in range(N)]
        optfun = 10000
        RequestLB = [optimizedrequest.startDT for optimizedrequest in GLB_REQUESTSToOptimize]
        RequestDurations = [optimizedrequest.duration for optimizedrequest in GLB_REQUESTSToOptimize]
        RequestDelays = [optimizedrequest.delay for optimizedrequest in GLB_REQUESTSToOptimize]
        RequestUB = np.array([optimizedrequest.endDT for optimizedrequest in GLB_REQUESTSToOptimize]) - (np.array(RequestDurations) + np.array(
            RequestDelays)) * 60
        for x0 in X0:
            bounds = Bounds(lb=RequestLB, ub=RequestUB)
            Solution = minimize(CycleScheduler.minComputeTankLevel, np.array(x0), bounds=bounds, method='SLSQP')
            if CycleScheduler.minComputeTankLevel(Solution['x']) < optfun:
                RequestStartTime = Solution['x']
                optfun=CycleScheduler.minComputeTankLevel(Solution['x'])

        TankLevelOptimized=CycleScheduler.computeTankLevel(RequestStartTime)

        return RequestStartTime,TankLevelOptimized

    ########################### WFI Simulation Functions ############################################################
    @staticmethod
    def minComputeTankLevel(T):
        L = CycleScheduler.computeTankLevel(T)
        return -min(L)

    @staticmethod
    def computeTankLevel(T):
        L = np.zeros(GBL_NUMBER_OF_15MIN_TICKS + 1)
        L[0] = GLB_StartTankLevel
        optiRequestCC = CycleScheduler.CycleConsumption(GLB_REQUESTSToOptimize,
                                         np.array(T))
        if len(optiRequestCC) > 0:
            optiRqCC = sum([optirequestCC for optirequestCC in optiRequestCC])
        else:
            optiRqCC = np.zeros(GBL_NUMBER_OF_15MIN_TICKS + 1)
        L[1] = (L[0] + GLB_MS1Active * GLB_MS1Flow + GLB_MS2Active * GLB_MS2Flow - GLB_BaselineUsage
                - GLB_TotalConsumptionForNonOptCycles[0] - optiRqCC[0])
        for i in range(2, GBL_NUMBER_OF_15MIN_TICKS + 1):
            L[i] = (L[i - 1] + int(L[i - 1] < GLB_TankCapacity - GLB_MS1Flow) * GLB_MS1Flow +
                    int(L[i - 1] < GLB_TankCapacity - GLB_MS1Flow - GLB_MS2Flow) * GLB_MS2Flow - GLB_BaselineUsage
                    - GLB_TotalConsumptionForNonOptCycles[i - 1] - optiRqCC[i - 1])
        return L

    @staticmethod
    def CycleConsumption(CyclePhases, ST):
        CF = [cyclephase.wfiConsumption for cyclephase in CyclePhases]
        return [Cp * cf for cf, Cp in zip(CF, CycleScheduler.CyclePlanning(CyclePhases, ST))]

    @staticmethod
    def CyclePlanning(CyclePhases, ST):
        CD15min = [cyclephase.duration / 15 for cyclephase in CyclePhases]
        CDe15min = [cyclephase.delay / 15 for cyclephase in CyclePhases]
        CS15min = [(st-GLB_ActualTime) /60.0 / 15.0 for st in ST]
        Cycle = np.zeros((len(CyclePhases), GBL_NUMBER_OF_15MIN_TICKS + 1))
        for Cyclestart_15min, Cycle_duration_15min, Cycle_delay_15min, j in zip(CS15min, CD15min, CDe15min,
                                                                                range(len(CyclePhases))):
            Cycle[j, int(Cyclestart_15min + Cycle_delay_15min)] = 1 - (Cyclestart_15min + Cycle_delay_15min - int(
                Cyclestart_15min + Cycle_delay_15min))
            for i in range(int(Cyclestart_15min + Cycle_delay_15min) + 1, int(
                    round(Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min))):
                Cycle[j, i] = 1
            Cycle[j, int(round(Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min))] = (Cyclestart_15min
                                                                                                 + Cycle_delay_15min + Cycle_duration_15min) - int(
                Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min)
        return Cycle



