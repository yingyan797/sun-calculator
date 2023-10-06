import numpy as np
from util import toDeg, toRad, arcCap
from dateTime import Date, Time, ydays, dsecs

axisAngle = toRad(23.5)
springEquinox = Date(3, 21)
earthRadius = 6371000 # In meters 

class Model:
    def sunDirectLatSin(date):
        days = 0
        if isinstance(date, Date):
            days = date.daysToRef(springEquinox)
        else:
            days = date-springEquinox.daysToRef(Date(1,1))
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

