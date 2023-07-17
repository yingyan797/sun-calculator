import numpy as np
from dateTime import Time, mdays

def toRad(deg):
    return deg*np.pi/180
def toDeg(rad):
    return rad*180/np.pi

def n2norm(vec):
    sum = 0
    for c in vec:
        sum += pow(c,2)
    return np.sqrt(sum)

def unit(vec):
    return vec/n2norm(vec)    

def project(vec, base):
    legnth = np.dot(vec, base)/n2norm(base)
    return legnth * unit(base)

def debase(vec, base):
    return vec-project(vec, base)

def vecAngleCos(v1, v2):
    return np.dot(v1, v2)/(n2norm(v1) * n2norm(v2))

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

