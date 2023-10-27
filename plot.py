import sunTime as st
import sunPosition as sp
import model, util
from temporal import Date, Time
import numpy as np
import matplotlib.pyplot as plt

heightTime = "static/Image/heightTime.png"
directionTime = "static/Image/directionTime.png"
heightDate = "static/Image/heightDate.png"
directionDate = "static/Image/directionDate.png"     
labels = ["","Sun height angle (degree)","Sun direction (from north)","Local time (s)","Date (days from January 1)"]
heightAnno = [(0, "Sunrise/set"), (-6, "Civil twl."), (-12, "Naut. twl."), (-18, "Astr. twl.")]
directionAnno1 = [(0, "North"), (45, "NE/NW"), (90, "East/West"), (135, "SE/SW"), (180, "South")]
directionAnno2 = [(0, "North"), (90, "East"), (180, "South"), (270, "West")]
dateAnno = [(1,"Jan"),(32,"Feb"),(60,"March"),(91,"April"),(121,"May"),(152,"June"),(182,"July"),(213,"Aug"),
                (244,"Sep"),(274,"Oct"),(305,"Nov"),(335,"Dec")]
vertAnno = [(80,"Spring Eq."),(173,"Summer So."),(266,"Autumn Eq."),(356,"Winter So.")]


def drawPlot(xs, ys, t, xl, yl):
    plt.title(t)
    plt.xlabel(labels[xl])
    plt.ylabel(labels[yl])
    plt.plot(xs,ys)
    plt.grid()
    gfile = ""

    lx = min(xs)
    ly = min(ys)
    ux = max(xs)
    uy = max(ys)
    if yl == 1:
        gfile = heightDate
        if xl == 3:
            gfile = heightTime
        for (d,t) in heightAnno:
            if d <= uy+5 and d >= ly-5:
                plt.axhline(d)
                plt.annotate(t, (ux, d))
    elif yl == 2 and xl == 3:
        gfile = directionTime
        for (d, t) in directionAnno1:
            plt.axhline(d)
            plt.annotate(t, (86400, d))
    elif yl in [7,8]:
        if xl == 4:
            return
        elif xl == 9:
            return

    if xl == 3:
        for i in range(0, 1440, 180):
            plt.annotate(util.secondsToTime(xs[i]).show(), (xs[i], ys[i]),xytext=(xs[i], ys[i]-(uy-ly)/10), arrowprops={"headwidth": 1, "width":1})
    elif xl == 4:
        for (d,t) in dateAnno:
            plt.annotate(t, (d, ys[d-1]),xytext=(d, ys[d-1]-(uy-ly)/20), arrowprops={"headwidth": 1, "width":0.5})
        for (d,t) in vertAnno:
            plt.axvline(d)
            plt.annotate(t,(d,ly-(uy-ly)/20))
    elif yl == 4:
        gfile = directionDate
        for (d,t) in directionAnno2:
            if d >= lx and d <= ux:
                plt.axvline(d)
                plt.annotate(t,(d,-10))
        for (d,t) in dateAnno:
            plt.annotate(t, (xs[d-1], d), (xs[d-1]-(ux-lx)/20,d+3), arrowprops={"headwidth": 1, "width":0.5})
        for (d,t) in vertAnno:
            plt.axhline(d)
            plt.annotate(t,(ux,d))

    plt.savefig(gfile)
    plt.clf()

class Plot:
    def __init__(self, queries, fields):
        self.queries = queries
        self.miss = None
        self.over = None
        self.fields = fields
    
    def loadMap(self, args, iv):
        self.args = args
        self.iv = iv

    def draw(self):
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
                        directions[i] = util.direcctionHalf(ang) 
                    drawPlot(locTime, heights, "Sun height over 24 hours "+"on "+self.args[3].show(),3,1)
                else:
                    for i in range(len(locTime)):
                        directions[i] = util.direcctionHalf(sp.sungeom(sinlat0, lat, [noon, locTime[i]])[0]) 
                drawPlot(locTime, directions, "Sun direction over 24 hours "+"on "+self.args[3].show(),3,2)
            if self.iv == 4:
                noonshift = [noon, self.args[3].toSecs()]
                dates = np.array([d for d in range(1, 366, 1)])
                directions = np.zeros(len(dates))
                if len(self.queries) == 2:
                    heights = np.zeros(len(dates))
                    for d in dates:
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        ang, ht = sp.sungeom(sinlat0, lat, noonshift)
                        directions[d-1] = util.toDeg(ang) 
                        heights[d-1] = util.toDeg(ht)
                    drawPlot(dates,heights,"Sun height at "+self.args[3].show()+" every day of the year",4,1)
                else:
                    for d in range(1, 366, 1):
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        directions[d-1] = util.toDeg(sp.sungeom(sinlat0, lat, noonshift)[0]) 
                drawPlot(directions,dates,"Sun direction at "+self.args[3].show()+" every day of the year",2,4)
        
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
# p.loadMap([51, -0.1, 1, Date(7,4)], 3)
p.loadMap([51, -0.1, 1, Time(12,35,0,0)], 4)
print(p.show())
print(p.draw())
