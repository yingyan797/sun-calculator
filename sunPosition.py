import numpy as np
from util import Util
from model import sunDirectLatSin, noonSecs
from dateTime import Time,Date, dsecs

def triangular(lat, dlon):
    return [np.cos(lat),np.cos(dlon+np.pi/2),np.sin(lat),np.sin(dlon+np.pi/2)]

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

def sunHeight(sinlat0, lat, noonShift):
    
    sun = np.array([0, np.cos(lat0), sinlat0])
    loc = sunVectorSet(lat, noonShift)[0]
    return np.pi/2-np.arccos(vecAngleCos(sun, loc)),0
    
def sunGeometric(sinlat0, lat, noonShift):
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

def approachTime(sinlat0, lat, noon, calc, low, high, std):
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

def approachDate(lat, noon, summer, time, calc, std):
    ref = Date(2,28).daysToRef(Date(1,1))
    secs = time.toSecs()
    preDiff = calc(np.arcsin(sunDirectLatSin(0)), lat, [noon, secs])[0] - std
    minDays = []
    for d in range(1,365):
        days = d
        if d > ref:
            days += 0.25
        if len(summer) > 0:
            if d in range(summer[0], summer[1]):
                noon += 3600
        lat0 = np.arcsin(sunDirectLatSin(days))
        res = calc(lat0, lat, [noon, secs])[0]
        diff = res - std
        if diff * preDiff < 0:
            if abs(diff) > abs(preDiff):
                minDays.append(daysToDate(days - 1))
            else:
                minDays.append(daysToDate(days))
            print(res)
        preDiff = diff
    
    return minDays


def approachLat(lat0, noon, time, calc, std):
    latl = -np.pi/2
    lath = np.pi/2
    lat = latl
    preDiff = calc(np.arcsin(lat0), )
    while lat <= lath:

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

def sunDateLim(lat, lon, gmt, time, hod, ang):
    ang = toRad(ang)
    lat = toRad(lat)
    noon = noonSecs(gmt, lon)
    calc = sunHeight
    if not hod:
        calc = sunGeometric
    ds = approachDate(lat, noon, [], time, calc, ang)
    return [d.show() for d in ds]   


def sunGeomLocLim(gmt, date, ht, ort, time):
    lat0 = np.arcsin(sunDirectLatSin(date))

