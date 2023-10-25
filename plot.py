import sunTime as st
import sunPosition as sp
import model, util
from temporal import Date, Time

plotfile = "static/db/plot.txt"

class Plot:
    def __init__(self, queries, fields):
        self.queries = queries
        self.miss = None
        self.over = None
        self.fields = fields
    
    def loadMap(self, args, iv):
        self.args = args
        self.iv = iv

    def drawPlot(self):
        f = open(plotfile, "w")
        if 2 in self.queries:
            lat = util.toRad(self.args[0])
            noon = model.noonSecs(self.args[2], self.args[1])
            if self.iv == 3:
                sinlat0 = model.sunDirectLatSin(self.args[3])
                if len(self.queries) == 2:
                    for sec in range(0, 86400, 900):
                        ang, ht = sp.sungeom(sinlat0, lat, [noon, sec])
                        f.write(util.secondsToTime(sec).show()+", "+str(util.toDeg(ang))+", "+str(util.toDeg(ht))+'\n')
                else:
                    for sec in range(0, 86400, 900):
                        f.write(util.secondsToTime(sec).show()+", "+str(util.toDeg(sp.sungeom(sinlat0, lat, [noon, sec])[0]))+'\n')
            if self.iv == 4:
                noonshift = [noon, self.args[3].toSecs()]
                if len(self.queries) == 2:
                    for d in range(1, 365, 1):
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        ang, ht = sp.sungeom(sinlat0, lat, noonshift)
                        f.write(str(d)+", "+str(util.toDeg(ang))+", "+str(util.toDeg(ht))+'\n')
                else:
                    for d in range(1, 365, 1):
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        f.write(str(d)+", "+str(util.toDeg(sp.sungeom(sinlat0, lat, noonshift)[0]))+'\n')


        f.close()

        
    def show(self):
        print("plot")
        res = "Plotting for: "
        for a in self.queries:
            res += self.fields[a]
        if self.miss:
            res += str(self.miss)
        elif self.over:
            res += " oversufficient: "+self.fields[self.over]
        else:
            res += " -versus- "+self.fields[self.iv] 
        return res
    
p = Plot([2], ["Time zone--GMT", "Sun height angle", "Sun direction angle", "Local time","Date", "Longitude", "Latitude", "Sunrise time", "Sunset time", "Altitude of observation", "","Solar noon"]
)
p.loadMap([35, 120, 8, Time(15,46,9,0)], 4)
print(p.show())
print(p.drawPlot())
