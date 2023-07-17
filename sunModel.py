import numpy as np
from util import toDeg, toRad, dateToDays, secondsToTime
from dateTime import Date, Time

axisAngle = toRad(23.5)
springEquinox = Date(3, 21) 
ydays = 365.25  # The number of days per year on average
dsecs = 86400   # The number of seconds per day

def sunDirectLatSin(date):
    days = dateToDays(date, springEquinox)
    phase = 2*np.pi*days/ydays
    return np.sin(phase) * np.sin(axisAngle)

def noonTime(gmt, lon):
    rtNoon = Time(12,0,0,0)
    lonShift = secondsToTime(abs(15*gmt-lon)/15*3600)
    if 15*gmt > lon:
        return rtNoon.succ(lonShift)
    return rtNoon.pred(lonShift)
