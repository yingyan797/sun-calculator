import numpy as np
from util import toDeg, toRad, vecAngleCos, debase, secondsToTime
from model import sunDirectLatSin, noonSecs
from dateTime import Time, dsecs

def localVecs(lat0, lat, lon):
    clt = np.cos(lat)
    cln = np.cos(lon+np.pi/2)
    slt = np.sin(lat)
    sln = np.sin(lon+np.pi/2)
    loc = np.array([clt*cln, clt*sln, slt])
    east = np.array([-sln, cln, 0])
    north = np.array([-slt*cln, -slt*sln, clt])
    return loc, east, north
    
def sunHeight(lat0, loc, e, n):
    sun = np.array([0, np.cos(lat0), np.sin(lat0)])
    return np.pi/2-np.arccos(vecAngleCos(sun, loc)), 0
    
def sunGeometric(lat0, loc, east, north):
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
    loc, east, north = localVecs(lat0, toRad(lat), (time.toSecs() - noon)/dsecs*2*np.pi)
    ang, ht = sunGeometric(lat0, loc, east, north)
    return "Sun height: "+str(toDeg(ht))+"; Sun direction: "+str(toDeg(ang))

def approach(lat0, lat, noon, calc, low, high, std):
    tl = low
    th = high
    t = tl
    while True:
      loc, east, north = localVecs(lat0, lat, (t-noon)/dsecs*2*np.pi)
      diff = calc(lat0, loc, east, north)[0] - std
      if diff < 0:
          tl = t
          if (th-t <= 1):
              loc1, e1, n1 = localVecs(lat0, lat, (th-noon)/dsecs*2*np.pi)
              if abs(diff) > abs(calc(lat0, loc1, e1, n1)[0] - std):
                  t = th
              break
          t = int((th+t)/2)   
      else:
          th = t
          if (t-tl <= 1):
              loc1, e1, n1 = localVecs(lat0, lat, (tl-noon)/dsecs*2*np.pi)
              if abs(diff) > abs(calc(lat0, loc1, e1, n1)[0] - std):
                  t = tl
              break
          t = int((t+tl)/2)
    return t

def sunHeightTimeLim(lat, lon, gmt, date, ht):
    ht = toRad(ht)
    lat = toRad(lat)
    noon = noonSecs(gmt, lon)
    lat0 = np.arcsin(sunDirectLatSin(date))
    locn, _, _ = localVecs(lat0, toRad(lat), 0)
    locm, _, _ = localVecs(lat0, toRad(lat), -np.pi)
    if sunHeight(lat0, locn, 0, 0)[0] < ht or sunHeight(lat0, locm, 0, 0)[0] > ht:
      print("Sun height not reachable")
      return secondsToTime(0)
    t = approach(lat0, lat, noon, sunHeight, noon-dsecs/2, noon, ht)
    return secondsToTime(t), secondsToTime(2*noon-t)      


def sunDirectionTimeLim(lat, lon, gmt, date, ort):
    ort = toRad(ort)
    lat = toRad(lat)
    noon = noonSecs(gmt, lon)
    lat0 = np.arcsin(sunDirectLatSin(date))
    t = approach(lat0, lat, noon, sunGeometric, noon-dsecs/2, noon+dsecs/2, ort)
    return secondsToTime(t)

        
    
