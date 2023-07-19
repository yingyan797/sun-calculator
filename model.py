import numpy as np
from util import toDeg, toRad, dateToDays, arcCap
from dateTime import Date, Time, ydays, dsecs

axisAngle = toRad(23.5)
springEquinox = Date(3, 21)
earthRadius = 6371000 # In meters 

def sunDirectLatSin(date):
    days = dateToDays(date, springEquinox)
    phase = 2*np.pi*days/ydays
    return arcCap(np.sin(phase) * np.sin(axisAngle))

def noonSecs(gmt, lon):
    return dsecs/2 + (15*gmt-lon)/15*3600

def horizonArc(alt):
    return np.arccos(arcCap(earthRadius/(earthRadius+alt)))

def horizonAngle(alt):
    return -toDeg(horizonArc(alt))

def horizonDistance(alt):
    return earthRadius/1000 * horizonArc(alt)
