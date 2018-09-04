import sys
import clr
import time
import pandas as pd

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