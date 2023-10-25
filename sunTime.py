import numpy as np
from model import sunDirectLatSin, noonSecs, horizonAngle
from temporal import dsecs
from util import toRad, toDeg, secondsToTime
from sunPosition import sunHeightTimeLim

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
def sunTimes(args):
    # lat, lon, gmt, date
    hdl = dayLength(args[3], args[0])/2
    noon = noonSecs(args[2], args[1])
    return secondsToTime(noon-hdl).show(), secondsToTime(noon+hdl).show()

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

def sunTimeAltitude(args):
    # lat, lon, gmt, date, alt
    return sunHeightTimeLim([args[0], args[1], args[2], args[3], horizonAngle(args[4])])


