import numpy as np
from dateTime import Time, mdays

def toRad(deg):
    return deg*np.pi/180
def toDeg(rad):
    return rad*180/np.pi

def dateToDays(date, ref):
    (cmp, spanMonths, dayDiff) = date.diff(ref)
    days = 0
    for m in spanMonths:
        days += mdays[m-1]
    days += dayDiff
    if cmp < 0:
        return (-1)*days
    return days

def secondsToTime(secs):
    h = int(secs/3600)
    secs -= 3600*h
    m = int(secs/60)
    secs -= 60*m
    return Time(h, m ,secs, 0)

