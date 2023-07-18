import numpy as np
from util import toDeg, toRad, vecAngleCos, debase, secondsToTime
from sunModel import sunDirectLatSin, noonTime, dsecs

def sunGeometric(lat0, lat, lon):
    clt = np.cos(toRad(lat))
    cln = np.cos(toRad(90+lon))
    slt = np.sin(toRad(lat))
    sln = np.sin(toRad(90+lon))

    sun = np.array([0, np.cos(toRad(lat0)), np.sin(toRad(lat0))])
    loc = np.array([clt*cln, clt*sln, slt])
    east = np.array([-sln, cln, 0])
    north = np.array([-slt*cln, -slt*sln, clt])

    ht = 90-toDeg(np.arccos(vecAngleCos(sun, loc)))
    ort = debase(sun, loc)
    angCos = vecAngleCos(ort, north)
    if angCos > 1-1/100000:
        return ht, 0
    if angCos < -1+1/100000:
        return ht, 180
    ang = toDeg(np.arccos(angCos)) 
    if (np.dot(ort, east) < 0):
        ang = 360-ang
    return ht, ang

def sunTimePosition(lat, lon, gmt, date, time):
    noon = noonTime(gmt, lon)
    lat0 = toDeg(np.arcsin(sunDirectLatSin(date)))
    ht, ang = sunGeometric(lat0, lat, (time.toSecs() - noon.toSecs())/dsecs*360)
    return "Sun height: "+str(ht)+"; Sun direction: "+str(ang)
