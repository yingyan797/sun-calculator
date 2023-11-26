from util import validLat, validLon, seps, showLat, showLon, parseRecord

placeFile = "static/db/places.csv"
plotFile = "static/db/plots.csv"
calcFile = "static/db/calculations.txt"
plotLim = 20
calcLim = 20

def readPlaces(parse):
    f = open(placeFile, "r")
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

def changeRecord(place, ln, info):
    f = open(placeFile, "r")
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
    f = open(placeFile, "w")
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
    return readPlaces(False)

def updatePlace(place, ln, coordi, gmti):
    lat, lon, gmt = parseRecord([coordi, gmti])
    info = place+','+str(lat)+','+str(lon)+','+str(gmt)
    if info != ",,,":
        changeRecord(place, ln, info+'\n')
        
def deletePlace(place):
    f = open(placeFile, "r")
    lines = f.readlines()
    for i in range(len(lines)):
        if lines[i].split(",")[0].lower() == place.lower():
            lines.pop(i)
            break
    f = open(placeFile, "w")
    f.writelines(lines)
    f.close()

def checkPlotNum():
    f = open(plotFile, "r")
    lines = f.readlines()
    f.close()
    if len(lines) == 0:
        return "1"
    if len(lines) >= plotLim:
        lines.pop(0)
        f = open(plotFile, "w")
        f.writelines(lines)
        f.close()
    
    num = (int(lines[-1].split(",")[0])+1) % plotLim
    if num == 0:
        num = plotLim
    return str(num)

def registerPlot(plotNum, plotType, plotDesc):
    f = open(plotFile, "a")
    line = plotNum+","+plotType+","+plotDesc
    f.write(line+"\n")
    f.close()

def readPlots():
    plots = []
    f = open(plotFile, "r")
    i = 1
    while True:
        line = f.readline()
        if line:
            info = line.split(",")
            plots = [{"Num": str(i),
                "plotName": "static/plots/"+info[0]+".png",
                "plotType": info[1],
                "plotInfo": info[2:]
                }] + plots
        else:
            break
    f.close()
    return plots

def registerCalc(interpret, conditions, res):
    f = open(calcFile, "r")
    lines = f.readlines()
    f.close()
    if len(lines) >= 3*calcLim:
        f = open(calcFile, "w")
        lines = lines[3:]
        f.writelines(lines)
        f.close()
    f = open(calcFile, "a")
    f.write(interpret+"\n")
    for k,v in conditions.items():
        f.write(k+": "+v+", ")
    f.write("\n"+res+"\n")
    f.close()

def readCalcs():
    calcs = []
    f = open(calcFile, "r")
    i = 1
    while True:
        question = f.readline()
        if question:
            calcs = [{"Num": str(i),
                "Question": question,
                "Conditions": f.readline(),
                "Result": f.readline()}] + calcs
            i += 1
        else:
            break
    f.close()
    return calcs

# print(registerPlace("soigih", "120", "35", "East", "North", "8"))
# print(registerPlace("london", "0.1", "51", "West", "North", "1"))
# print(updatePlace("iafk", 1, "51n `20w", "-2"))
# print(deletePlace("iafk"))
