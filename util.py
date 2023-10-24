import numpy as np
from dateTime import Time, Date, mdays, dsecs
seps = "~`!@#$%^&*()_+={[]|\\:;<,>?/'\"\n\r }"
dbfile = "static/db/places.csv"

def readTable(fn, parse):
    f = open(fn, "r")
    lines = f.readlines()
    f.close()
    rows = [l[:-1].split(",") for l in lines]
    for pn in range(len(rows)):
        if parse:
            cct = ""
            for c in rows[pn][0]:
                if c not in seps:
                    cct += c
                else:
                    cct += '-'
            rows[pn][0] = cct
        else:
            lat = rows[pn][1]
            lon = rows[pn].pop(2)
            rows[pn][1] = ""
            if lat != "":
                rows[pn][1] += showLat(float(lat)) + ", "
            if lon != "":
                rows[pn][1] += showLon(float(lon)) 
        rows[pn] = [pn+1]+rows[pn]
                
    return rows

def arcCap(ac):
    if ac > 1:
        return 1
    if ac < -1:
        return -1
    return ac

def latSinToCos(asin):
    if asin >= 1 or asin <= -1:
        return 0
    return np.sqrt(1-pow(asin, 2))

def toRad(deg):
    return deg*np.pi/180
def toDeg(rad):
    return rad*180/np.pi

def n2norm(vec):
    sum = 0
    for c in vec:
        sum += pow(c,2)
    return np.sqrt(sum)

def unit(vec):
    return vec/n2norm(vec)    

def project(vec, base):
    legnth = np.dot(vec, base)/n2norm(base)
    return legnth * unit(base)

def debase(vec, base):
    return vec-project(vec, base)

def vecAngleCos(v1, v2):
    return arcCap(np.dot(v1, v2)/(n2norm(v1) * n2norm(v2)))     

def daysToDate(days):
    month = 1
    day = 0
    for md in mdays:
        if days > md:
            month += 1
            days -= md
        else:
            day = np.ceil(days)
            break
    return Date(month, int(day))

def secondsToTime(secs):
    d = 0
    if (secs >= 0):
        d = int(secs/dsecs)
    else:
        d = int((1+secs)/dsecs)-1
    secs -= dsecs*d
    h = int(secs/3600)
    secs -= 3600*h
    m = int(secs/60)
    secs -= 60*m
    return Time(h, m ,secs, d)

def showLon(lon):
    if lon >= 0:
        return str(lon)+'E'
    else:
        return str(-lon)+'W'

def showLat(lat):
    if lat >= 0:
        return str(lat)+'N'
    else:
        return str(-lat)+'S'

def toLonVal(num, ew):
    if num > 0 and ew == "West":
        return 0-num
    return num

def toLatVal(num, ns):
    if num > 0 and ns == "South":
        return 0-num
    return num

def validLat(lat):
    return lat is not None and lat >= -90 and lat <= 90

def validLon(lon):
    return lon is not None and lon >= -180 and lon <= 180

def findFloat(tok):
    dot = False
    neg = False
    digit = False
    num = ""
    i = 0
    while i < len(tok):
        c = tok[i]
        if not dot and not neg and c == '-':
            neg = True
            num += c
            i += 1
        elif not dot and c == '.':
            dot = True
            num += c
            i += 1
        elif c.isdigit():
            if not digit:
                digit = True
            num += c
            i += 1
        else:
            break
    if digit:
        return num, i
    return "", i

def directionClass(ang, rg):
    if ang < rg or ang > 360-rg:
        return "North"
    if ang >= rg and ang <= 90-rg:
        return "Northeast"
    if ang > 90-rg and ang < 90+rg:
        return "East"
    if ang >= 90+rg and ang <= 180-rg:
        return "Southeast"
    if ang > 180-rg and ang < 180+rg:
        return "South"
    if ang >= 180+rg and ang <= 270-rg:
        return "Southwest"
    if ang > 270-rg and ang < 270+rg:
        return "West"
    if ang >= 270+rg and ang <= 360-rg:
        return "Northwest"
