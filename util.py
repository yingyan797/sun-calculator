import numpy as np
from dateTime import Time, Date, mdays, dsecs

def arcCap(ac):
    if ac > 1:
        return 1
    if ac < -1:
        return -1
    return ac

def latSinToCos(asin):
    if asin >= 1 or asin <= -1:
        return 0
    return np.sqrt(1-pow(asin, 2))

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
    return arcCap(np.dot(v1, v2)/(n2norm(v1) * n2norm(v2)))     

def daysToDate(days):
    month = 1
    day = 0
    for md in mdays:
        if days > md:
            month += 1
            days -= md
        else:
            day = np.ceil(days)
            break
    return Date(month, int(day))

def secondsToTime(secs):
    d = 0
    if (secs >= 0):
        d = int(secs/dsecs)
    else:
        d = int((1+secs)/dsecs)-1
    secs -= dsecs*d
    h = int(secs/3600)
    secs -= 3600*h
    m = int(secs/60)
    secs -= 60*m
    return Time(h, m ,secs, d)

def showLon(lon):
    if lon > 0:
        return str(lon)+'E'
    if lon < 0:
        return str(-lon)+'W'
    return str(lon)

def showLat(lat):
    if lat > 0:
        return str(lat)+'N'
    if lat < 0:
        return str(-lat)+'S'
    return str(lat)

def toLonVal(num, ew):
    if num > 0 and ew == "West":
        return 0-num
    return num

def toLatVal(num, ns):
    if num > 0 and ns == "South":
        return 0-num
    return num

def validLat(lat):
    return lat in range(-90, 91)

def validLon(lon):
    return lon in range(-180, 181)

