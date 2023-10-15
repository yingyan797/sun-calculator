import numpy as np
import model
import util
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

def sunht(sinlat0, lat, noonShift):
    
    sun = np.array([0, util.latSinToCos(sinlat0), sinlat0])
    loc = sunVectorSet(lat, noonShift)[0]
    return np.pi/2-np.arccos(util.vecAngleCos(sun, loc)),None
    
def sungeom(sinlat0, lat, noonShift):
    loc, east, north = sunVectorSet(lat, noonShift)
    sun = np.array([0, util.latSinToCos(sinlat0), sinlat0])
    ht = np.pi/2-np.arccos(util.vecAngleCos(sun, loc))
    ort = util.debase(sun, loc)
    ang = np.arccos(util.vecAngleCos(ort, north))
    if (np.dot(ort, east) < 0):
        ang = 2*np.pi-ang
    return ang, ht

def sunHeight(args):
    # lat, lon, gmt, date, time
    noon = model.noonSecs(args[2], args[1])
    sinlat0 = model.sunDirectLatSin(args[3])
    ht, ang = sunht(sinlat0, util.toRad(args[0]), [noon, args[4].toSecs()])
    return util.toDeg(ht)

def sunPosition(args):
    # lat, lon, gmt, date, time
    noon = model.noonSecs(args[2], args[1])
    sinlat0 = model.sunDirectLatSin(args[3])
    ang, ht = sungeom(sinlat0, util.toRad(args[0]), [noon, args[4].toSecs()])
    return util.toDeg(ht), util.toDeg(ang)

def approachTime(sinlat0, lat, noon, calc, low, high, std):
    tl = low
    th = high
    t = tl
    while True:
      diff = calc(sinlat0, lat, [noon, t])[0] - std
      if diff < 0:
          tl = t
          if (th-t <= 1):
              if abs(diff) > abs(calc(sinlat0, lat, [noon, th])[0] - std):
                  t = th
              break
          t = int((th+t)/2)   
      else:
          th = t
          if (t-tl <= 1):
              if abs(diff) > abs(calc(sinlat0, lat, [noon, tl])[0] - std):
                  t = tl
              break
          t = int((t+tl)/2)
    return t

def approachDate(lat, noon, summer, time, calc, std):
    ref = Date(2,28).daysToRef(Date(1,1))
    secs = time.toSecs()
    preDiff = calc(model.sunDirectLatSin(0), lat, [noon, secs])[0] - std
    minDays = []
    for d in range(1,365):
        days = d
        if d > ref:
            days += 0.25
        if len(summer) > 0:
            if d in range(summer[0], summer[1]):
                noon += 3600
        res = calc(model.sunDirectLatSin(days), lat, [noon, secs])[0]
        diff = res - std
        if diff * preDiff < 0:
            if abs(diff) > abs(preDiff):
                minDays.append(util.daysToDate(days - 1))
            else:
                minDays.append(util.daysToDate(days))
            print(res)
        preDiff = diff
    
    return minDays


def approachLat(lat0, noon, time, calc, std):
    latl = -np.pi/2
    lath = np.pi/2
    lat = latl
    preDiff = calc(np.arcsin(lat0), )
    while lat <= lath:
        break
    return lat

def sunHeightTimeLim(args):
    # lat, lon, gmt, date, ht
    ht = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    sinlat0 = model.sunDirectLatSin(args[3])
    if sunht(sinlat0, lat, [0])[0] < ht or sunht(sinlat0, lat, [-np.pi])[0] > ht:
      print("Sun height not reachable")
      return util.secondsToTime(0)
    t1 = approachTime(sinlat0, lat, noon, sunht, noon-dsecs/2, noon, ht)
    t2 = 2*noon-t1
    if t1 != t2:
        return util.secondsToTime(t1).show(), util.secondsToTime(t2).show()  
    return util.secondsToTime(t1).show()

def sunDirectionTimeLim(args):
    # lat, lon, gmt, date, ort
    ort = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    t = approachTime(model.sunDirectLatSin(args[3]), lat, noon, sungeom, noon-dsecs/2, noon+dsecs/2, ort)
    return util.secondsToTime(t).show()

def sunDateLim(args):
    # lat, lon, gmt, time, ang, hod
    ang = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    calc = sunht
    if not args[5]:
        calc = sungeom
    ds = approachDate(lat, noon, [], args[3], calc, ang)
    return [d.show() for d in ds]   


def sunGeomLocLim(gmt, date, ht, ort, time):
    lat0 = np.arcsin(model.sunDirectLatSin(date))

# t1, t2 = sunHeightTimeLim(30, 120, 8, Date(6,15), 50)
# print(t1.show(), t2.show())
# print(sunPosition(30, 120, 8, Date(6,15), t1))
# print(sungeom(0, 0, [0]))
