import numpy as np
from util import toDeg, toRad, vecAngleCos, debase, secondsToTime
from model import sunDirectLatSin, noonSecs
from dateTime import Time, dsecs

def triangular(lat, dlon):
    return [np.cos(lat),np.cos(dlon+np.pi/2),np.sin(lat),np.sin(dlon+np.pi/2)]

def sunRelative(lat, dlon):
    vs = triangular(lat, dlon)
    return np.array([vs[0]*vs[1], vs[0]*vs[3], vs[2]])

def sunVectorSet(lat, noonShift):
    dlon = 0
    if len(noonShift) == 1:
        dlon = noonShift[0]
    else:
        dlon = (noonShift[1] - noonShift[0])/dsecs*2*np.pi
    vs = triangular(lat, dlon)
    loc = np.array([vs[0]*vs[1], vs[0]*vs[3], vs[2]])
    east = np.array([-vs[3], vs[1], 0])
    north = np.array([-vs[2]*vs[1], -vs[2]*vs[3], vs[0]])
    return loc, east, north

def sunHeight(lat0, lat, noonShift):
    
    sun = np.array([0, np.cos(lat0), np.sin(lat0)])
    loc = sunVectorSet(lat, noonShift)[0]
    return np.pi/2-np.arccos(vecAngleCos(sun, loc)),0
    
def sunGeometric(lat0, lat, noonShift):
    loc, east, north = sunVectorSet(lat, noonShift)
    sun = np.array([0, np.cos(lat0), np.sin(lat0)])
    ht = np.pi/2-np.arccos(vecAngleCos(sun, loc))
    ort = debase(sun, loc)
    ang = np.arccos(vecAngleCos(ort, north))
    if (np.dot(ort, east) < 0):
        ang = 2*np.pi-ang
    return ang, ht

def sunTimePosition(lat, lon, gmt, date, time):
    noon = noonSecs(gmt, lon)
    lat0 = np.arcsin(sunDirectLatSin(date))
    ang, ht = sunGeometric(lat0, lat, [noon, time.toSecs()])
    return "Sun height: "+str(toDeg(ht))+"; Sun direction: "+str(toDeg(ang))

def approachTime(lat0, lat, noon, calc, low, high, std):
    tl = low
    th = high
    t = tl
    while True:
      diff = calc(lat0, lat, [noon, t])[0] - std
      if diff < 0:
          tl = t
          if (th-t <= 1):
              if abs(diff) > abs(calc(lat0, lat, [noon, th])[0] - std):
                  t = th
              break
          t = int((th+t)/2)   
      else:
          th = t
          if (t-tl <= 1):
              if abs(diff) > abs(calc(lat0, lat, [noon, tl])[0] - std):
                  t = tl
              break
          t = int((t+tl)/2)
    return t

def approachLoc():
    
    return lon, lat

def sunHeightTimeLim(lat, lon, gmt, date, ht):
    ht = toRad(ht)
    lat = toRad(lat)
    noon = noonSecs(gmt, lon)
    lat0 = np.arcsin(sunDirectLatSin(date))
    if sunHeight(lat0, lat, [0])[0] < ht or sunHeight(lat0, lat, [-np.pi])[0] > ht:
      print("Sun height not reachable")
      return secondsToTime(0)
    t = approachTime(lat0, lat, noon, sunHeight, noon-dsecs/2, noon, ht)
    return secondsToTime(t), secondsToTime(2*noon-t)      

def sunDirectionTimeLim(lat, lon, gmt, date, ort):
    ort = toRad(ort)
    lat = toRad(lat)
    noon = noonSecs(gmt, lon)
    lat0 = np.arcsin(sunDirectLatSin(date))
    t = approachTime(lat0, lat, noon, sunGeometric, noon-dsecs/2, noon+dsecs/2, ort)
    return secondsToTime(t)   

def sunGeomLocLim(gmt, date, ht, ort, time):
    lat0 = np.arcsin(sunDirectLatSin(date))
    


