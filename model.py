import numpy as np
import pandas as pd
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

def daytimeBalance(date, lat):
    pss = sunDirectLatSin(date)
    sbs = np.tan(toRad(lat)) * pss / np.sqrt(1-pow(pss,2))
    if sbs > 1:
        return 90
    if sbs < -1:
        return -90
    return toDeg(np.arcsin(sbs))

def dayLength(date, lat):
    return (daytimeBalance(date, lat) * 2 + 180) / 360 * dsecs

def sunOrientation(time, midnight, lat, date):
    perp = sunDirectLatSin(date)
    # to be continued

# Main formula to calculate sunrise&sunset times
def sunTimes(lat, lon, gmt, date):
    hdl = secondsToTime(dayLength(date, lat)/2)
    noon = Time(12,0,0,0)
    lonShift = secondsToTime(abs(15*gmt-lon)/15*3600)

    if 15*gmt > lon:
        noon = noon.succ(lonShift)
    else:
        noon = noon.pred(lonShift)
    sunrise = noon.pred(hdl)
    sunset = noon.succ(hdl)
    return sunrise, sunset

# Display calculation result
def calcSun(lat, lon, gmt, date):
    sr, ss = sunTimes(lat, lon, gmt, date)
    ns = ""
    ew = ""
    if lat > 0:
        ns = "N"
    if lat < 0:
        ns = "S"
    if lon > 0:
        ew = "E"
    if lon < 0:
        ew = "W"
    print("Location: "+str(abs(lat))+ns+", "+str(abs(lon))+ew+"\n"
          +"Date: "+date.show()+"\n"
          +"Sunrise: "+sr.show()+"\n"
          +"Sunset:  "+ss.show())
