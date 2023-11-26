import numpy as np
import util, model
from util import toDeg, toRad, arcCap
from temporal import Date, Time, ydays, dsecs


axisAngle = toRad(23.5)
springEquinox = Date(3, 21)
earthRadius = 6371000 # In meters 

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

def noonTime(args):
    return util.secondsToTime(noonSecs(args[1], args[0])).__str__()

def horizonArc(alt):
    return np.arccos(arcCap(earthRadius/(earthRadius+alt)))

def horizonAngle(alt):
    return -toDeg(horizonArc(alt))

def horizonDistance(alt):
    return earthRadius/1000 * horizonArc(alt)

def thrTimeZone(args):
    lon = args[0]
    low = np.floor((lon-7.5)/15)
    mid = np.floor(lon/15)
    up = np.floor((lon+7.5)/15)
    if low < mid:
        return int(mid)
    if up > mid:
        return int(up)
    return int(mid)

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

def sphereDistance(lats, lons):
    for i in range(2):
        lats[i] = util.toRad(lats[i])
        lons[i] = util.toRad(lons[i])
    rise2 = pow(np.sin(lats[0])-np.sin(lats[1]), 2)
    ra = np.cos(lats[0])
    rb = np.cos(lats[1])
    run2 = pow(ra, 2) + pow(rb, 2) - 2*ra*rb*np.cos(lons[0] - lons[1])
    ang = 2*np.arcsin(util.arcCap(np.sqrt(rise2+run2)/2))

    return earthRadius/1000*ang

