import sunTime as st
import sunPosition as sp
import model, util
from temporal import Date, Time
import numpy as np
import matplotlib.pyplot as plt

plotfile = "static/db/plot.txt"
heightTime = "static/Image/heightTime.png"
directionTime = "static/Image/directionTime.png"
heightDate = "static/Image/heightDate.png"
directionDate = "static/Image/directionDate.png"     

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
        if 2 in self.queries:
            lat = util.toRad(self.args[0])
            noon = model.noonSecs(self.args[2], self.args[1])
            if self.iv == 3:
                sinlat0 = model.sunDirectLatSin(self.args[3])
                locTime = np.array([sec for sec in range(0, 86400, 60)])
                directions = np.zeros(len(locTime))
                if len(self.queries) == 2:
                    heights =  np.zeros(len(locTime))
                    for i in range(len(locTime)):
                        ang, ht = sp.sungeom(sinlat0, lat, [noon, locTime[i]])
                        heights[i] = util.toDeg(ht) 
                        directions[i] = util.toDeg(ang) 
                    plt.title("Sun height over 24 hours "+"on "+self.args[3].show())
                    plt.xlabel("Local time (s)")
                    plt.ylabel("Sun height angle (degree)")
                    plt.plot(locTime, heights)
                    plt.grid()
                    for i in range(0, 1440, 180):
                        plt.annotate(util.secondsToTime(locTime[i]).show(), (locTime[i], heights[i]),
                                     xytext=(locTime[i], heights[i]-5), arrowprops={"headwidth": 1, "width":1})
                    plt.annotate("Horizon", (0,0), (85000,1), arrowprops={"width": 0.5, "headwidth": 0.5})
                    plt.savefig(heightTime)
                    plt.clf()
                else:
                    for i in range(len(locTime)):
                        directions[i] = util.toDeg(sp.sungeom(sinlat0, lat, [noon, locTime[i]])[0]) 
                plt.title("Sun direction over 24 hours "+"on "+self.args[3].show())
                plt.xlabel("Local time (s)")
                plt.ylabel("Sun direction (from north)")
                plt.plot(locTime, directions)
                plt.grid()
                for i in range(0, 1440, 180):
                    plt.annotate(util.secondsToTime(locTime[i]).show(),(locTime[i], directions[i]), 
                                 xytext=(locTime[i], directions[i]-15), arrowprops={"headwidth": 1})
                for (d, t) in [(0, "North"), (45, "NE"), (90, "East"), (135, "SE"), (180, "South"), (225, "SW"), (270, "West"), (315, "NW")]:
                    plt.annotate(t, (0, d), xytext=(85000, d+4), arrowprops={"width": 0.5, "headwidth": 0.5})

                plt.savefig(directionTime)
            if self.iv == 4:
                noonshift = [noon, self.args[3].toSecs()]
                dates = np.array([d for d in range(1, 366, 1)])
                directions = np.zeros(len(dates))
                if len(self.queries) == 2:
                    heights = np.zeros(len(dates))
                    plt.title("Sun height at "+self.args[3].show()+" every day of the year")
                    plt.xlabel("Date (days from January 1)")
                    plt.ylabel("Sun height angle (degree)")
                    for d in dates:
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        ang, ht = sp.sungeom(sinlat0, lat, noonshift)
                        directions[d-1] = util.toDeg(ang) 
                        heights[d-1] = util.toDeg(ht)
                    plt.plot(dates, heights)
                    plt.grid()
                    plt.savefig(heightDate)
                    plt.clf()
                else:
                    for d in range(1, 366, 1):
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        directions[d-1] = util.toDeg(sp.sungeom(sinlat0, lat, noonshift)[0]) 
                plt.title("Sun direction at "+self.args[3].show()+" every day of the year")
                plt.xlabel("Date (days from January 1)")
                plt.ylabel("Sun direction (from north)")
                plt.plot(dates, directions)
                plt.grid()
                plt.savefig(directionDate)
        
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
    
p = Plot([1,2], ["Time zone--GMT", "Sun height angle", "Sun direction angle", "Local time","Date", "Longitude", "Latitude", "Sunrise time", "Sunset time", "Altitude of observation", "","Solar noon"])
p.loadMap([35, 120, 8, Time(15,35,0,0)], 4)
print(p.show())
print(p.drawPlot())
