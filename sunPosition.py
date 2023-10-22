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
    print("h, a", ht, ang)
    ang = util.toDeg(ang)
    return util.toDeg(ht), str(ang) +", "+ util.directionClass(ang, 10)

def sunHeightTimeLim(args):
    # lat, lon, gmt, date, ht
    ht = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    sinlat0 = model.sunDirectLatSin(args[3])
    if sunht(sinlat0, lat, [0])[0] < ht or sunht(sinlat0, lat, [-np.pi])[0] > ht:
      return "**Sun height angle not reachable in the given context"
    t1 = model.approachTime(sinlat0, lat, noon, sunht, noon-dsecs/2, noon, ht)
    t2 = 2*noon-t1
    if t1 != t2:
        return util.secondsToTime(t1).show(), util.secondsToTime(t2).show()  
    return util.secondsToTime(t1).show()

def sunDirectionTimeLim(args):
    # lat, lon, gmt, date, ort
    ort = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    t = model.approachTime(model.sunDirectLatSin(args[3]), lat, noon, sungeom, noon-dsecs/2, noon+dsecs/2, ort)
    return util.secondsToTime(t).show()

def sunDateLim(args):
    # lat, lon, gmt, time, ang, hod
    ang = util.toRad(args[4])
    lat = util.toRad(args[0])
    noon = model.noonSecs(args[2], args[1])
    calc = sunht
    if not args[5]:
        calc = sungeom
    ds = model.approachDate(lat, noon, [], args[3], calc, ang)
    return [d.show() for d in ds]   


def sunLatLim(args):
    # lon, gmt, date, time, ang, hod
    sinlat0 = model.sunDirectLatSin(args[2])

# t1, t2 = sunHeightTimeLim(30, 120, 8, Date(6,15), 50)
# print(t1.show(), t2.show())
# print(sunPosition(30, 120, 8, Date(6,15), t1))
# print(sungeom(0, 0, [0]))
