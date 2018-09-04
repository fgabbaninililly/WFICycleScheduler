#####  PACKAGES IMPORT ######

from PIDataReadFunctions import readFromOSIPI
from Context import *
pd.options.mode.chained_assignment = None

#### IMPLEMENTED FUNCTIONS ############

TANK_LEVEL_TAG_NAME = "WT_351_711_02.P31.PV"

def get_Tank_level():
    Tank_level = readFromOSIPI(TANK_LEVEL_TAG_NAME, float)
    tank_level = Tank_level['Value']
    return float(tank_level)


def get_Running_Cycles():
    Cycles_still_running = pd.DataFrame([],
                                        columns=['Component', 'LocalTime', 'TimefromNow', 'TimefromNowMinutes', 'Value',
                                                 'TimeLeftminutes'])
    # Recording the last listed cycles which could be running

    ## Special Cases : Washers:
    if int(readFromOSIPI(Cycle_Tags['Tag List'][1], int)['Value']) == 1:
        tag_info = readFromOSIPI(Cycle_Tags['Tag List'][0], str)
        Component_name = Cycle_Tags['Component'][0]
        Cycle_name = tag_info['Value'][0]
        duration = Du[Cyclename_to_index(Component_name, Cycle_name)]
        delay = De[Cyclename_to_index(Component_name, Cycle_name)]
        tag_info['Component'] = Component_name
        tag_info['Duration'] = duration
        tag_info['TimeLeftminutes'] = delay + duration + tag_info['TimefromNowMinutes']
        Cycles_still_running = Cycles_still_running.append(tag_info, sort=True)
    if int(readFromOSIPI(Cycle_Tags['Tag List'][3], int)['Value']) == 1:
        tag_info = readFromOSIPI(Cycle_Tags['Tag List'][2], str)
        Component_name = Cycle_Tags['Component'][2]
        Cycle_name = tag_info['Value'][0]
        duration = Du[Cyclename_to_index(Component_name, Cycle_name)]
        delay = De[Cyclename_to_index(Component_name, Cycle_name)]
        tag_info['TimeLeftminutes'] = delay + duration + tag_info['TimefromNowMinutes']
        tag_info['Component'] = Component_name
        tag_info['Duration'] = duration
        Cycles_still_running = Cycles_still_running.append(tag_info, sort=True)

    ##Other cycle cases
    for i in range(4, len(Cycle_Tags['Tag List'])):
        tag_info = readFromOSIPI(Cycle_Tags['Tag List'][i])
        Component_name = Cycle_Tags['Component'][i]
        Cycle_name = tag_info['Value'][0]
        if Cycle_consumes_Water(Component_name, Cycle_name):
            duration = Du[Cyclename_to_index(Component_name, Cycle_name)]
            delay = De[Cyclename_to_index(Component_name, Cycle_name)]
            # getting information from tag
            if duration + tag_info['TimefromNowMinutes'][0] > 0:
                tag_info['TimeLeftminutes'] = delay + duration + tag_info['TimefromNowMinutes']
                tag_info['Component'] = Component_name
                tag_info['Duration'] = duration
                Cycles_still_running = Cycles_still_running.append(tag_info, sort=True)

    return Cycles_still_running


def Cycle_consumes_Water(Component_name, Cycle_name):
    return (Component_name in Components) & (Cycle_name in Cyclenames)


def Cyclename_to_index(Component_name, Cycle_name):
    return list(set(np.where(Components == Component_name)[0]) & set(np.where(Cyclenames == Cycle_name)[0]))[0]


def get_MS1_active():
    return readFromOSIPI(Tags['Tag List'][1], float)['Value'][0] >= 102


def get_MS2_active():
    return readFromOSIPI(Tags['Tag List'][2], float)['Value'][0] >= 102

def CycleConsumption(D, De, ST, CF, nbC):
    return [Cp * cf for cf, Cp in zip(CF, Cycle_planning(D, De, ST, nbC))]


def Cycle_planning(D, De, ST, nbC):
    CD15min = [d / 15 for d in D]
    CDe15min = [de / 15 for de in De]
    CS15min = [st * 1.0 / 15.0 for st in ST]
    Cycle = np.zeros((nbC, nb15min + 1))
    for Cyclestart_15min, Cycle_duration_15min, Cycle_delay_15min, j in zip(CS15min, CD15min, CDe15min, range(nbC)):
        Cycle[j, int(Cyclestart_15min + Cycle_delay_15min)] = 1 - (Cyclestart_15min + Cycle_delay_15min - int(
            Cyclestart_15min + Cycle_delay_15min))
        for i in range(int(Cyclestart_15min + Cycle_delay_15min) + 1, int(
                round(Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min))):
            Cycle[j, i] = 1
        Cycle[j, int(round(Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min))] = (Cyclestart_15min
                                                                                             + Cycle_delay_15min + Cycle_duration_15min) - int(
            Cyclestart_15min + Cycle_delay_15min + Cycle_duration_15min)
    return Cycle


def sample_Requests_to_optimize():
    Component_name = 'Washer_981721'
    Cycle_name = 'LAVAGGIO ACIDO FREDDO CORTO TUBI FORMULATION'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 0
    upper_bound = 200
    R1 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS = [R1]
    Component_name = 'CP_800711'
    Cycle_name = 'LAVAGGIO_VUOTO_GB'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 0
    upper_bound = 300
    R2 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R2)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 0
    upper_bound = 600
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 0
    upper_bound = 300
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 100
    upper_bound = 300
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 100
    upper_bound = 600
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 200
    upper_bound = 400
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 50
    upper_bound = 250
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    Component_name = 'SFL_740'
    Cycle_name = 'CIP_SFL_1LINE'
    Cycle_Flow = CF[Cyclename_to_index(Component_name, Cycle_name)]
    lower_bound = 300
    upper_bound = 450
    R3 = {'Component': Component_name,
          'Cycle': Cycle_name
        , 'Flow': Cycle_Flow, 't1': lower_bound, 't2': upper_bound}
    REQUESTS.append(R3)
    return REQUESTS





