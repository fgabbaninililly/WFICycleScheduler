import time
import datetime
"""
class Component:
    name = ""
    cycleList = list()

class Cycle:
    name = ""
    phaseList = list()

"""
class Phase:
    """
       Models a cycle phase that consumes WFI.

       Attributes:
           componentName: name of component that triggers the cycle
           cycleName: cycle name
           name: cycle phase name
           duration: cycle phase duration (minutes)
           delay: time delay when for WFI consumption, from cycle phase start (minutes)
           wfiConsumption: WFI used by cycle (liters/15 minutes)
    """

    componentName = ""
    cycleName = ""
    name = ""
    duration = 0
    delay = 0
    wfiConsumption = 0
    id = 0

class RequestedPhase(Phase):
    """
        Enriches CyclePhase with information related to requested scheduling and optimization.
    
        Attributes:
            startDT: cycle phase start date and time. If a cycle phase is optimally scheduled (isOptimized = 1), scheduled cycle phase  start (scheduledStartDT)
                will be chosen by an optimization algorithm to be not earlier than startDT. 
                If a cycle phase is NOT optimized, scheduled cycle phase start (scheduledStartDT) will coincide with startDT.
            endDT: cycle phase end date and time. Provides an upper bound for cycle phase end. In case of optimization, cycle phase start is 
                chosen so that scheduledStartDT + duration <= endDT
            isOptimized: denotes if cycle phase start is optimally scheduled by calls to CycleScheduler.scheduleCycleRequests or not 
    """

    startDT = time.time()
    endDT = time.time()
    isOptimized = 0

    def initFromPhase(self, cyclePhase):
        self.componentName = cyclePhase.componentName
        self.cycleName = cyclePhase.cycleName
        self.name = cyclePhase.name
        self.duration = cyclePhase.duration
        self.delay = cyclePhase.delay
        self.wfiConsumption = cyclePhase.wfiConsumption

    def toString(self):
        mystr = "Component name: " + self.componentName + "\n"
        mystr = mystr  + "Cycle name: " + self.cycleName + "\n"
        mystr = mystr  + "Phase name: " + self.name + "\n"
        mystr = mystr  + "Duration: " + str(self.duration) + "\n"
        mystr = mystr  + "Delay: " + str(self.delay) + "\n"
        mystr = mystr  + "WFI consumption: " + str(self.wfiConsumption) + "\n"
        mystr = mystr  + "Start: " + str(datetime.datetime.fromtimestamp(self.startDT)) + "\n"
        mystr = mystr  + "End: " + str(datetime.datetime.fromtimestamp(self.endDT))
        return mystr

    def isEqual(self, anotherRequestedPhase):
        return self.id == anotherRequestedPhase.id

    def getStartDateStr(self):
        return str(datetime.datetime.fromtimestamp(self.startDT))

    def getEndDateStr(self):
        return str(datetime.datetime.fromtimestamp(self.endDT))

    def resetStartDateFromString(self, dateAsString):
        self.startDT = int(time.mktime(time.strptime(dateAsString, "%Y-%m-%d %H:%M:%S")))

    def resetEndDateFromString(self, dateAsString):
        self.endDT = int(time.mktime(time.strptime(dateAsString, "%Y-%m-%d %H:%M:%S")))

class ScheduledPhase(RequestedPhase):
    """
        Enriches RequestedCyclePhase with information related to final scheduling.

        Attributes:
            scheduledStartDT: scheduled cycle phase start date and time (see comments to startDT) 
    """
    scheduledStartDT = time.time()
    scheduledEndDT = time.time()

    def initFromRunningPhase(self, runningPhase,actualTime,timefromnowminutes):
        #runningPhase is a Phase instance
        self.initFromPhase(runningPhase)
        self.startDT = actualTime
        self.endDT = self.startDT + (self.delay + self.duration + timefromnowminutes) * 60
        self.scheduledStartDT = actualTime
        self.scheduledEndDT = self.startDT + (self.delay + self.duration + timefromnowminutes) * 60

    def initFromRequestedPhase(self, requestedPhase):
        self.initFromPhase(requestedPhase)
        self.startDT = requestedPhase.startDT
        self.endDT = requestedPhase.endDT
        self.scheduledStartDT = self.startDT
        self.scheduledEndDT = self.endDT
        self.isOptimized = requestedPhase.isOptimized






