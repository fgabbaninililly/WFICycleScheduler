import sys
import clr
import pandas as pd
import numpy as np
from DataModel import *

sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0')
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *
from OSIsoft.AF.UnitsOfMeasure import *

piServers = PIServers()
piservername= "XF2OSIPI01"
piServer = piServers[piservername]

class PITag :
    TAGFIELD_LOCALTIME = 'LocalTime'
    TAGFIELD_TIMEFROMNOW = 'TimefromNow'
    TAGFIELD_TIMEFROMNOWMIN = 'TimefromNowMinutes'
    TAGFIELD_TIMELEFTMIN = 'TimeLeftminutes'
    TAGFIELD_COMPONENT = 'Component'
    TAGFIELD_DURATION = 'Duration'
    TAGFIELD_VALUE= 'Value'

    def __init__(self, tValue, localTime, timeFromNow, timeFromNowMin):
        self.tagDF = pd.DataFrame({
            PITag.TAGFIELD_LOCALTIME: localTime,
            PITag.TAGFIELD_TIMEFROMNOW: timeFromNow,
            PITag.TAGFIELD_TIMEFROMNOWMIN: timeFromNowMin,
            #PITag.TAGFIELD_TIMELEFTMIN: time.time(),
            #PITag.TAGFIELD_COMPONENT: "",
            #PITag.TAGFIELD_DURATION: 0,
            PITag.TAGFIELD_VALUE: tValue}, index=[0])

    def getValue(self):
        return self.tagDF[PITag.TAGFIELD_VALUE][0]

    def getTimeFromNowMinutes(self):
        return self.tagDF[PITag.TAGFIELD_TIMEFROMNOWMIN][0]

class OSIPIReader :
    TAGNAME_TANK_LEVEL = "WT_351_711_02.P31.PV"
    TAGNAME_MS1_TEMPERATURE = "TT_350_711_14.P31.PV"
    TAGNAME_MS2_TEMPERATURE = "TT_350_721_14.P31.PV"

    def setContext(self, context):
        self.context = context

    def getTankLevel(self):
        Tank_level = self.readTag(OSIPIReader.TAGNAME_TANK_LEVEL, float).getValue()
        return Tank_level

    @staticmethod
    def readTag(tagname, dtype=str):
        pt = PIPoint.FindPIPoint(piServer, tagname)
        current_value = pt.CurrentValue()
        localTime = str(current_value.Timestamp.LocalTime)
        utcSeconds = float(current_value.Timestamp.UtcSeconds)
        actualTime = time.time()
        timeFromNow = -(actualTime - utcSeconds)
        timeFromNowMinutes = -(actualTime - utcSeconds) / 60
        tagValue = dtype(str(current_value.Value))
        piTag = PITag(tagValue, localTime, timeFromNow, timeFromNowMinutes)
        return piTag

    def getRunningCycles(self,actualTime):
        runningCycles = list()

        runningWasherCycles = self.__getRunningWasherCycles(actualTime)
        runningCycles = runningCycles + runningWasherCycles

        tagNames = self.context.configurationParameters.getTags()
        tagComponentNames = self.context.configurationParameters.getTagComponents()
        subPhases = self.context.configurationParameters.getSubPhases()
        components = self.context.configurationParameters.getComponents()
        cycles = self.context.configurationParameters.getCycles()

        for i in range(len(tagNames)):
            #Information of the running Cycle from OSIPI tag
            tagName = OSIPIReader.readTag(tagNames[i])
            cycleName = tagName.getValue()
            componentName = tagComponentNames[i]
            if not(self.context.cycleConsumesWater(componentName, cycleName)):
                continue
            subPhaseName = subPhases[np.where((componentName == components) & (cycles == cycleName))[0][0]]
            phase = self.context.getCyclePhaseFromNames(componentName, cycleName, subPhaseName)

            #Intancing a scheduled phse as running cycles are already scheduled
            scheduledPhase = ScheduledPhase()
            scheduledPhase.initFromRunningPhase(phase,actualTime,tagName.getTimeFromNowMinutes())

            runningCycles.append(scheduledPhase)

        return runningCycles

    def __getRunningWasherCycles(self,actualTime):
        runningCycles = list()

        W721_PNAME = "Batch_WASH_981721.RecipeProductName.P31.BAT"
        W721_ACTIVE = "Batch_WASH_981721.BatchActive.P31.BAT"
        W721_COMPONENT = "Washer_981721"
        W731_ACTIVE = "Batch_WASH_981731.BatchActive.P31.BAT"
        W731_PNAME = "Batch_WASH_981731.RecipeProductName.P31.BAT"
        W731_COMPONENT = "Washer_981731"

        subPhases = np.array(self.context.configurationParameters.getSubPhases())
        components = self.context.configurationParameters.getComponents()
        cycles = self.context.configurationParameters.getCycles()

        tagActive = OSIPIReader.readTag(W721_ACTIVE)
        tagName = OSIPIReader.readTag(W721_PNAME)
        cycleName = tagName.getValue()
        componentName = W721_COMPONENT
        if (int(tagActive.getValue()) == 1)&(self.context.cycleConsumesWater(componentName, cycleName)):
            subPhaseName = subPhases[np.where((componentName == components) & (cycles == cycleName))[0][0]]
            phase = self.context.getCyclePhaseFromNames(componentName, cycleName, subPhaseName)
            scheduledPhase = ScheduledPhase()
            scheduledPhase.initFromRunningPhase(phase,actualTime,tagName.getTimeFromNowMinutes())
            runningCycles.append(scheduledPhase)

        tagActive = OSIPIReader.readTag(W731_ACTIVE)
        tagName = OSIPIReader.readTag(W731_PNAME)
        cycleName = tagName.getValue()
        componentName = W731_COMPONENT
        if (int(tagActive.getValue()) == 1)&(self.context.cycleConsumesWater(componentName, cycleName)):
            subPhaseName = subPhases[np.where((componentName == components) & (cycles == cycleName))[0][0]]
            phase = self.context.getCyclePhaseFromNames(componentName, cycleName, subPhaseName)
            scheduledPhase = ScheduledPhase()
            scheduledPhase.initFromRunningPhase(phase,actualTime,tagName.getTimeFromNowMinutes())
            runningCycles.append(scheduledPhase)
        return runningCycles

    def getMS1Active(self):
        MS1_TEMPERATURE = float(self.readTag(OSIPIReader.TAGNAME_MS1_TEMPERATURE).getValue())
        return MS1_TEMPERATURE >= 102

    def getMS2Active(self):
        MS2_TEMPERATURE = float(self.readTag(OSIPIReader.TAGNAME_MS1_TEMPERATURE).getValue())
        return MS2_TEMPERATURE >= 102

    def readFromOSIPI(tagname, dtype=str):
        pt = PIPoint.FindPIPoint(piServer, tagname)
        current_value = pt.CurrentValue()
        LocalTime = str(current_value.Timestamp.LocalTime)
        UtcSeconds = float(current_value.Timestamp.UtcSeconds)
        actualtime = time.time()
        TimefromNow = -(actualtime - UtcSeconds)
        TimefromNowMinutes = -(actualtime - UtcSeconds) / 60
        Value = dtype(str(current_value.Value))
        df = pd.DataFrame({'LocalTime': LocalTime,
                           'TimefromNow': TimefromNow,
                           'TimefromNowMinutes': TimefromNowMinutes,
                           'Value': Value}, index=[0])
        return df

