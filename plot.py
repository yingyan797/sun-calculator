import sunTime as st
import sunPosition as sp
import model, util
from temporal import Date, Time, dsecs
import numpy as np
import matplotlib.pyplot as plt

plotFiles = ["static/plots/"+fn for fn in 
             ["heightTime","heightDate","directionTime","directionDate","rsDate","rsAltitude1","","rsAltitude2"]]
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
    lx = min(xs)
    ly = min(ys)
    ux = max(xs)
    uy = max(ys)
    if yl == 1:
        for (d,t) in heightAnno:
            if d <= uy+5 and d >= ly-5:
                plt.axhline(d)
                plt.annotate(t, (ux, d))
    elif yl == 2 and xl == 3:
        for (d, t) in directionAnno1:
            plt.axhline(d)
            plt.annotate(t, (86400, d))
    
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
        for (d,t) in directionAnno2:
            if d >= lx and d <= ux:
                plt.axvline(d)
                plt.annotate(t,(d,-10))
        for (d,t) in dateAnno:
            plt.annotate(t, (xs[d-1], d), (xs[d-1]-(ux-lx)/20,d+3), arrowprops={"headwidth": 1, "width":0.5})
        for (d,t) in vertAnno:
            plt.axhline(d)
            plt.annotate(t,(ux,d))

def riseSetPlot(xs, tr, ts, xl,t):
    fig, ax1 = plt.subplots()
    ax1.set_title(t)
    ax1.set_xlabel(xl)
    ax1.set_ylabel("Sunrise time (s)")
    ax2 = ax1.twinx()
    ax2.set_ylabel("Sunset time (s)")
    ax1.plot(xs, tr)
    ax2.plot(xs, ts)
    ax1.set_yticklabels([])
    ax2.set_yticklabels([])
    ly = min(tr)
    uy = max(tr)
    ly2 = min(ts)
    uy2 = max(ts)
    unit = (uy-ly)/20
    timeStep = 1800
    if xl == labels[4]:
        ax1.set_yticklabels([])
        ax2.set_yticklabels([])
        ax1.annotate("Sunrise",(51,tr[50]))
        ax2.annotate("Sunset",(51,ts[50]))
        for (d,t) in dateAnno:
            ax1.axvline(d)
            ax1.annotate(t,(d,ly-unit))
        for (d,t) in vertAnno:
            ax1.annotate(t,(d,tr[d-1]),(d-5,tr[d-1]+3*unit),arrowprops={"headwidth": 1, "width":0.5})
            ax2.annotate(t,(d,ts[d-1]),(d+2,ts[d-1]+2*unit),arrowprops={"headwidth": 1, "width":0.5})
    elif xl == "Altitude (km)":
        timeStep = 600
        ax1.annotate("Sunrise",(xs[10],tr[10]))
        ax2.annotate("Sunset",(xs[10],ts[10]))
    for t in range(-7200,150000,timeStep):
        if t >= ly - timeStep/3 and t <= uy+timeStep/3:
            ax1.annotate(util.secondsToTime(t).show(), (-0.5,t))
            ax1.axhline(t,0,0.6)
    for t in range(-7200,150000,timeStep):
        if t >= ly2 - timeStep/3 and t <= uy2+timeStep/3:
            ax2.annotate(util.secondsToTime(t).show(), (xs[-10],t))
            ax2.axhline(t,0.4,1)
    

class Plot:
    def __init__(self, queries, fields, ab):
        self.queries = queries
        self.miss = None
        self.over = None
        self.fields = fields
    
    def loadMap(self, args, iv):
        self.args = args
        self.iv = iv

    def draw(self, calc):
        lat = util.toRad(self.args[0])
        noon = model.noonSecs(self.args[2], self.args[1])
        dates = np.array([d for d in range(1, 366, 1)])
        locTime = np.array([sec for sec in range(0, 86400, 60)])
        plots = []
        if 2 in self.queries:
            if self.iv == 3:
                sinlat0 = model.sunDirectLatSin(self.args[3])
                
                directions = np.zeros(len(locTime))
                if len(self.queries) == 2:
                    heights =  np.zeros(len(locTime))
                    for i in range(len(locTime)):
                        ang, ht = sp.sungeom(sinlat0, lat, [noon, locTime[i]])
                        heights[i] = util.toDeg(ht) 
                        directions[i] = util.direcctionHalf(ang) 
                    drawPlot(locTime, heights, "Sun height over 24 hours "+"on "+self.args[3].show(),3,1)
                    pn = plotFiles[0]+str(calc.plotNum[0])+".png"
                    plt.savefig(pn)
                    plt.clf()
                    plots.append(pn)
                    calc.plotNum[0] += 1
                else:
                    for i in range(len(locTime)):
                        directions[i] = util.direcctionHalf(sp.sungeom(sinlat0, lat, [noon, locTime[i]])[0]) 
                drawPlot(locTime, directions, "Sun direction over 24 hours "+"on "+self.args[3].show(),3,2)
                pn = plotFiles[2]+str(calc.plotNum[2])+".png"
                plt.savefig(pn)
                plt.clf()
                plots.append(pn)
                calc.plotNum[2] += 1
            if self.iv == 4:
                noonshift = [noon, self.args[3].toSecs()]
                directions = np.zeros(len(dates))
                if len(self.queries) == 2:
                    heights = np.zeros(len(dates))
                    for d in dates:
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        ang, ht = sp.sungeom(sinlat0, lat, noonshift)
                        directions[d-1] = util.toDeg(ang) 
                        heights[d-1] = util.toDeg(ht)
                    drawPlot(dates,heights,"Sun height at "+self.args[3].show()+" every day of the year",4,1)
                    pn = plotFiles[1]+str(calc.plotNum[1])+".png"
                    plt.savefig(pn)
                    plt.clf()
                    plots.append(pn)
                    calc.plotNum[1] += 1
                else:
                    for d in range(1, 366, 1):
                        sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                        directions[d-1] = util.toDeg(sp.sungeom(sinlat0, lat, noonshift)[0]) 
                drawPlot(directions,dates,"Sun direction at "+self.args[3].show()+" every day of the year",2,4)
                pn = plotFiles[3]+str(calc.plotNum[3])+".png"
                plt.savefig(pn)
                plt.clf()
                plots.append(pn)
                calc.plotNum[3] += 1
        elif self.queries == [1]:
            if self.iv == 3:
                sinlat0 = model.sunDirectLatSin(self.args[3])
                heights =  np.zeros(len(locTime))
                for i in range(len(locTime)):
                    heights[i] = util.toDeg(sp.sunht(sinlat0, lat, [noon, locTime[i]])[0]) 
                drawPlot(locTime, heights, "Sun height over 24 hours "+"on "+self.args[3].show(),3,1)
                pn = plotFiles[0]+str(calc.plotNum[0])+".png"
                plt.savefig(pn)
                plt.clf()
                plots.append(pn)
                calc.plotNum[0] += 1
            elif self.iv == 4:
                noonshift = [noon, self.args[3].toSecs()]
                
                heights = np.zeros(len(dates))
                for d in dates:
                    sinlat0 = model.sunDirectLatSin(util.daysToDate(d)) 
                    heights[d-1] = util.toDeg(sp.sunht(sinlat0, lat, noonshift)[0])
                drawPlot(dates,heights,"Sun height at "+self.args[3].show()+" every day of the year",4,1)
                pn = plotFiles[1]+str(calc.plotNum[1])+".png"
                plt.savefig(pn)
                plt.clf()
                plots.append(pn)
                calc.plotNum[1] += 1
        elif 7 in self.queries or 8 in self.queries:
            if self.iv == 4:
                match len(self.args):
                    case 3:
                        rises = np.zeros(len(dates))
                        sets = np.zeros(len(rises))
                        for d in dates:
                            hdl = st.dayLength(util.daysToDate(d), lat)/2
                            rises[d-1] = noon-hdl
                            sets[d-1] = noon + hdl
                        riseSetPlot(dates,rises,sets,labels[4],"Sunrise and sunset times every day of the year")
                        pn = plotFiles[4]+str(calc.plotNum[4])+".png"
                        plt.savefig(pn)
                        plt.clf()
                        plots.append(pn)
                        calc.plotNum[4] += 1
                    case 4:
                        ang = model.horizonAngle(self.args[3])
            elif self.iv == 9:
                alts = [[a/10 for a in range(0,150)], [a for a in range(0,200,2)]]
                rises = [np.zeros(len(alts[0])),np.zeros(len(alts[1]))]
                sets = [np.zeros(len(alts[0])),np.zeros(len(alts[1]))]
                sinlat0 = model.sunDirectLatSin(self.args[3])
                for j in [0,1]:
                    a = alts[j]
                    for i in range(len(a)):
                        ang = util.toRad(model.horizonAngle(a[i]*1000))
                        tr = model.approachTime(sinlat0,lat,noon,sp.sunht,noon-dsecs/2, noon, ang)
                        ts = 2*noon-tr
                        rises[j][i] = tr
                        sets[j][i] = ts
                    riseSetPlot(a,rises[j],sets[j],"Altitude (km)","Sunrise and sunset times for different altitudes on "+self.args[3].show())
                    num = 5+j
                    pn = plotFiles[num]+str(calc.plotNum[num])+".png"
                    plt.savefig(pn)
                    plt.clf()
                    plots.append(pn)
                    calc.plotNum[num] += 1
        return plots

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
    
# p = Plot([7,8], ["Time zone--GMT", "Sun height angle", "Sun direction angle", "Local time","Date", "Longitude", "Latitude", "Sunrise time", "Sunset time", "Altitude of observation", "","Solar noon"])
# # p.loadMap([51, -0.1, 1, Date(7,4)], 3)
# # p.loadMap([35, 112, 8, Date(7,4)], 9)
# p.loadMap([35, 112, 8], 4)
# print(p.show())
# print(p.draw())
# print(plotFiles)
