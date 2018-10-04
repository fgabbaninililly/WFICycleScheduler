import numpy as np
import pandas as pd

#### GLOBAL VARIABLES #############

#Getting time status
nb15min=24*4 #we arbitrarely plot on 10 hours
listOfTimeUnitTicks= np.arange(nb15min + 1) * 15

##Data from excel

#Constants
Constants = pd.read_excel('Variables.xlsx',sheet_name ='Constants',names =['Name','Water_Flow'],header=None)
MS1F=Constants['Water_Flow'].iloc[0]
MS2F=Constants['Water_Flow'].iloc[1]
TC =Constants['Water_Flow'].iloc[2]
CU =Constants['Water_Flow'].iloc[5]

#Tags
Tags=pd.read_excel('Tags.xlsx')
Cycle_Tags=Tags.drop([0,1,2,3])
Cycle_Tags.index = range(len(Cycle_Tags))

#Cycles
Cycles = pd.read_excel('Variables.xlsx',sheet_name ='Cycles')
Du=Cycles['Duration (m)']
#Du=Du.drop([14,16,18])
Du.index = range(len(Du))
nb_Cycles=len(Du)
De=Cycles['delay from start cycle (m)']
#De=De.drop([14,16,18])
De.index = range(len(De))
Components=Cycles['Component']
#Components=Components.drop([14,16,18])
Components=np.array(Components)
Cyclenames=Cycles['Cycle']
#Cyclenames=Cyclenames.drop([14,16,18])
Cyclenames=np.array(Cyclenames)
Subphasesnames=np.array(Cycles['SubPhase'],dtype=str)
#=np.array(Subphasesnames.drop([14,16,18]))
CF=Cycles['WFI Flow OSI_PI o rossi (l/15min)']
#CF=CF.drop([14,16,18])
CF=np.array(CF)