from temporal import Date, Time
import util, model
import sunTime as st
import sunPosition as sp
from plot import Plot

fields = ["Time zone GMT", "Sun height angle", "Sun direction angle", "Local time", 
          "Date", "Longitude", "Latitude", "Sunrise time", "Sunset time", "Altitude of observation", "","Solar noon"]

qs = ["what is the (theoretical) time zone?", "what is the height angle of the sun (relative to horizon)?", 
                "what is the direction of the sun (angle clockwise from North)?", "what time of the day is it when", 
                "which date is it when", "what is the longitude of a location where", "what is the latitude of a location where", 
                "what time does sunrise occur?", "what time does sunset occur?", "what altitude of observation (in meters) is it where",
                "", "what time is the solar noon?"]
sunriseset = [(st.sunTimeAltitude, [6,5,0,4,9]), (st.sunTimes, [6,5,0,4])]

answerMap = {
    1: [(sp.sunHeight, [6,5,0,4,3])], 2: [(sp.sunPosition, [6,5,0,4,3])], 
    3: [(sp.sunHeightTimeLim, [6,5,0,4,1]), (sp.sunDirectionTimeLim, [6,5,0,4,2])],
    4: [(sp.sunDateLim, [6,5,0,3,1]), (sp.sunDateLim, [6,5,0,3,2])],
    7: sunriseset, 8: sunriseset, 0: [(model.thrTimeZone, [5])], 11: [(model.noonTime, [5, 0])]
}

plotMaps = [[([6,5,0,4], 3), ([6,5,0,3], 4)], [([6,5,0,9], 4), ([6,5,0], 4), ([6,5,0,4],9)]]


class Abstract:
    def __init__(self, taskDesc, num):
        self.taskDesc = taskDesc
        self.num = num
        self.interpret = ""
        self.negate = False

    def clear(self):
        self.queries = []
        self.angles = []
        self.details = [None for i in range(12)]
        self.interpret = ""
        self.conditions = {}
        self.response = []
        self.place = None
        self.ivs = []
        self.plotNums = []
        self.plotInfo = []

    def addDate(self, month, day):
        d = Date(int(month), int(day))
        if d.check():
            self.details[4] = d
    
    def addTime(self, h, m, s):
        sec = 0
        day = 0
        if s:
            sec = s
        if h == 24:
            day = 1
        self.details[3] = Time(int(h),int(m),int(sec),day)

    def addAltitude(self, alt, unit):
        self.details[9] = alt
        if not unit:
            unit = "m"
        self.details[10] = unit   

    def addLon(self, lon, ew):
        self.details[5] = util.toLonVal(lon, ew)

    def addLat(self, lat, ns):
        self.details[6] = util.toLatVal(lat, ns)

    def queryReduce(self):
        qi = 0
        while qi < len(self.queries):
            q = self.queries[qi]
            if q == 1 and len(self.angles) > 0:
                self.queries.pop(qi)
                self.details[1] = self.angles.pop(0)
                if self.negate:
                    self.details *= (-1)
            elif q == 2 and len(self.angles) > 0:
                self.queries.pop(qi)
                self.details[2] = self.angles.pop(0)
            elif q == 5 and self.details[6] == None:
                self.queries.pop(qi)
            elif q in [4,3,9,0] and self.details[q]:
                self.queries.pop(qi)
            else:
                qi += 1

    def formQuestion(self):
        self.interpret = ""  
        if self.queries == []:
            self.interpret += "**Sorry, unable to detect what values to calculate or plot. "
        else:    
            if self.place:
                self.interpret = "at "+self.place+", "
            for qi in self.queries:
                self.interpret += qs[qi] + " "
            self.interpret = self.interpret[0].upper() + self.interpret[1:]

            if self.details[1]:
                self.interpret += " the sun is at "+str(self.details[1])+" degree above horizon?"
            if self.details[2]:
                self.interpret += " the sun's direction is "+str(self.details[2])+" degree clockwise from North?"
        if self.ivs:
            self.interpret += "Plotting over "+fields[self.ivs[0]]
        for iv in self.ivs[1:]:
            self.interpret +=  ", "+fields[iv]
        self.interpret += " --Given conditions:"
        lat, lon = self.details[6], self.details[5]
        if lat != None and lon != None:
            self.conditions["Location"] = util.showLat(lat)+" "+util.showLon(lon)
        else:
            if lat != None:
                self.conditions[fields[6]] = util.showLat(lat)
            elif lon != None:
                self.conditions[fields[5]] = util.showLon(lon)
        
        for i in [4, 3]:
            if self.details[i]:
                self.conditions[fields[i]] = self.details[i].__str__()
        if self.details[0] is not None:
            gmt = self.details[0]
            c = ""
            if gmt > 0:
                c = '+'+str(gmt)
            else:
                c = str(gmt)
            self.conditions[fields[0]] = c
        if self.details[9]:
            self.conditions[fields[9]] = str(self.details[9])+self.details[10]

    def formPlot(self):
        def checkConds(pmap):
            missing = []
            for (ms, iv) in pmap:
                missCase = []
                for m in ms:
                    if self.details[m] is None:
                        missCase.append(m)
                if missCase != []:
                    missing.append(missCase)
                else:
                    return (ms, iv), None
            return None, missing

        plots = [Plot([], fields, self.conditions) for i in range(2)]
        ps = [1,2,7,8]
        pflag = [False, False]
        for q in self.queries:
            if q in ps:
                pmap = None
                i = 0
                if q in [7,8]:
                    i = 1
                plots[i].queries.append(q)
                if not pflag[i]:
                    pflag[i] = True
                    pmap, miss = checkConds(plotMaps[i])
                    if miss is None and self.details[pmap[1]] is None: 
                        plots[i].loadMap([self.details[j] for j in pmap[0]], pmap[1])
                    elif miss is None:
                        plots[i].over = pmap[1]
                    else:
                        plots[i].miss = miss
        self.plotInfo = []
        self.plotNums = []
        for plot in plots:
            valid, info = plot.validInfo()
            if valid == 0:
                self.plotNums += plot.draw()
            elif valid == 2:
                self.plotInfo.append(info)

    def formResponse(self):
        self.response = []
        if not self.conditions:
            self.response.append("**Missing conditions")
            return False
        if self.details[10] == "km":
            self.details[10] = "m"
            self.details[9] *= 1000
        def checkAnswer(maps):
            missing = []
            for m in maps:
                mg = []
                for cond in m[1]:
                    if self.details[cond] is None:
                        mg.append(cond)
                if mg != []:
                    missing.append(mg)
                else:
                    args = [self.details[cond] for cond in m[1]]
                    if m[0] == sp.sunDateLim:
                        hod = False
                        if m[1][-1] == 1:
                            hod = True
                        args.append(hod)
                    return m[0](args), None
            return None,missing
        
        res, res78, missing, qtemp, temp78 = [], [], [], [], []
        q1 = False
        miss78 = None
        for q in self.queries:
            if q == 1:
                q1 = True
            elif q == 2:
                r,m = checkAnswer(answerMap[2])
                if q1:
                    qtemp.append(1)
                    missing.append(m)
                    if r:
                        res.append(r[0])
                    else:
                        res += [None, None]
                qtemp.append(2)
                missing.append(m)
                if r:
                    res.append(r[1])
                q1 = False
            elif q in [7,8]:
                if len(temp78) < 1:
                    r,miss78 = checkAnswer(answerMap[7])
                    if r:
                        res78 += [r[0], r[1]]
                    else:
                        res78 += [None, None]
                temp78.append(q)
            
            elif q in answerMap:
                maps = answerMap[q]
                qtemp.append(q)
                r, m = checkAnswer(maps)
                res.append(r)
                missing.append(m)

        if q1:
            qtemp.append(1)
            r,m = checkAnswer(answerMap[1])
            res.append(r) 
            missing.append(m)
        qtemp += temp78
        for i in temp78:
            res.append(res78[i-7])
            missing.append(miss78)
        
        valid = False
        for i in range(len(qtemp)):
            info = ""
            if res[i] is not None:
                info = fields[qtemp[i]]+": "+str(res[i])
                valid = True
            if missing[i] is not None:
                info = "Calculating "+fields[qtemp[i]]+": **Missing the following information: \n  <Case 1>"
                c = 1
                for m in missing[i][0]:
                    info += ", "+fields[m]
                for ms in missing[i][1:]:
                    c += 1
                    info += "\n  <Case "+str(c)+'>'
                    for m in ms:
                        info += ", "+fields[m]
            self.response.append(info)
            return valid
        # for qt in qtemp:
        #     self.response.append(fields[qt]+res[qt])

    def show(self):
        print(self.formQuestion())