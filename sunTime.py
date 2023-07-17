import numpy as np
from sunModel import sunDirectLatSin, noonTime, dsecs
from util import toRad, toDeg, secondsToTime

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

# Main formula to calculate sunrise&sunset times
def sunTimes(lat, lon, gmt, date):
    hdl = secondsToTime(dayLength(date, lat)/2)
    noon = noonTime(gmt, lon)
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
