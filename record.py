from calculator import Calculator
from util import dbfile, readTable


def changeRecord(place, ln, info):
    f = open(dbfile, "r")
    lines = f.readlines()
    inRecord = False
    if ln is None:
        for i in range(len(lines)):
            if lines[i].split(",")[0].lower() == place.lower():
                lines[i] = info
                inRecord = True
                break
    else:
        lines[ln] = info
        inRecord = True
    f.close()
    if not inRecord:
        lines.append(info)
    f = open(dbfile, "w")
    f.writelines(lines)
    f.close()

def registerPlace(place, lon, lat, ew, ns, gmt):
    info = place+",,,"
    if lon:
        if ew == "West" and lon[0] != '-':
            lon = '-'+lon
    if lat:
        if ns == "South" and lat[0] != '-':
            lat = '-'+lat
    if lon and lat:
        info = place + ',' +lat+','+lon+','
    if gmt:
        info += gmt
    if info != place+",,,":
        changeRecord(place, None, info+'\n')
    return readTable(dbfile, False)

def updatePlace(place, ln, coordi, gmti):
    sc = Calculator()
    sc.taskDesc = coordi
    sc.readProgress = 0
    sc.notMatchToken = ""
    lat, lon = sc.parseLocation()
    sc.taskDesc = gmti
    sc.readProgress = 0
    sc.notMatchToken = ""
    gmt = sc.parseGMT()
    info = place+",,,"
    if (lat, lon) != (None, None):
        info = place+','+str(lat)+','+str(lon)+','
    if gmt != None:
        info += str(gmt)
    if info != ",,,":
        changeRecord(place, ln, info+'\n')
        
def deletePlace(place):
    f = open(dbfile, "r")
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].split(",")[0].lower() == place.lower():
            lines.pop(i)
            break
    f = open(dbfile, "w")
    f.writelines(lines)
    f.close()

# print(registerPlace("soigih", "120", "35", "East", "North", "8"))
# print(registerPlace("london", "0.1", "51", "West", "North", "1"))
# print(updatePlace("iafk", 1, "51n `20w", "-2"))
# print(deletePlace("iafk"))
