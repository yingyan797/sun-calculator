from dateTime import Date, Time
import sunTime as st
import sunPosition as sp
import util, model

months = {
    "january": "1","jan": "1","february": "2","feb": "2","march": "3","mar": "3","april": "4","apr": "4","may": "5",
    "june": "6","jun": "6","july": "7","jul": "7","august": "8","aug": "8","september": "9","sept": "9","sep": "9",
    "october": "10","oct": "10","november": "11","nov": "11","december": "12","dec": "12"
}

querySet = {
    "height": 1, "ht": 1, "high": 1, "direction": 2, "dir": 2, "orientation": 2, "time": 3, "date": 4, "day": 4,
    "longitude": 5, "lon": 5, "latitude": 6, "lat": 6, "sunrise": 7, "sunset": 8, "above": 1, "below": 1, 
    "altitude": 9, "elavation": 9, "zone": 0, "noon": 11
}

fields = ["Time zone--GMT", "Sun height angle", "Sun direction angle", "Local time", 
          "Date", "Longitude", "Latitude", "Sunrise time", "Sunset time", "Altitude of observation", "","Solar noon"]

degs = ["degree", "deg", "d"]
ms = ["m", "meter", "meters", "metre", "metres"]
kms = ["km", "kilometer", "kilometers", "kilometre", "kilometres"]

sunriseset = [(st.sunTimeAltitude, [6,5,0,4,9]), (st.sunTimes, [6,5,0,4])]
risesetplot = [([6,5,0,9], 4), ([6,5,0], 4), ([6,5,0,4],9)]

answerMap = {
    1: [(sp.sunHeight, [6,5,0,4,3])], 2: [(sp.sunPosition, [6,5,0,4,3])], 
    3: [(sp.sunHeightTimeLim, [6,5,0,4,1]), (sp.sunDirectionTimeLim, [6,5,0,4,2])],
    4: [(sp.sunDateLim, [6,5,0,3,1]), (sp.sunDateLim, [6,5,0,3,2])],
    7: sunriseset, 8: sunriseset, 0: [(model.thrTimeZone, [5])], 11: [(model.noonTime, [5, 0])]
}

plotMap = {
    1: [([6,5,0,4], 3), ([6,5,0,3], 4)], 2: [([6,5,0,4], 3), ([6,5,0,3], 4)], 7: risesetplot, 8: risesetplot
}

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
        self.conditions = []
        self.response = []
        self.plot = None
        self.place = None
        self.ivs = []

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
            self.interpret += "**Sorry, unable to detect what value(s) to calculate. "
        else:    
            if self.place:
                self.interpret = "at "+self.place+", "
            qs = ["what is the (theoretical) time zone?", "what is the height angle of the sun (relative to horizon)?", 
                "what is the direction of the sun (angle clockwise from North)?", "what time of the day is it when", 
                "which date is it when", "what is the longitude of a location where", "what is the latitude of a location where", 
                "what time does sunrise occur?", "what time does sunset occur?", "what altitude of observation (in meters) is it where",
                "", "what time is the solar noon?"]
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
            self.conditions.append("Location: "+util.showLat(lat)+", "+util.showLon(lon))
        else:
            if lat != None:
                self.conditions.append(fields[6]+": "+util.showLat(lat))
            elif lon != None:
                self.conditions.append(fields[5]+": "+util.showLon(lon))
        
        for i in [4, 3]:
            if self.details[i]:
                self.conditions.append(fields[i]+": "+self.details[i].show())
        if self.details[0] is not None:
            gmt = self.details[0]
            c = "Time zone: GMT "
            if gmt > 0:
                c += '+'+str(gmt)
            else:
                c += str(gmt)
            self.conditions.append(c)
        if self.details[9]:
            self.conditions.append(fields[9]+": "+str(self.details[9])+self.details[10])

    def formPlot(self):
        self.plot = []
        for q in self.queries:
            if q in plotMap:
                for (ms, iv) in plotMap[q]:
                    complete = True
                    for m in ms:
                        if self.details[m] is None:
                            complete = False
                            break
                    if complete:
                        select = (ms, iv)
                        self.plot.append(select)


    def formResponse(self):
        self.response = []
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
        
        for i in range(len(qtemp)):
            info = ""
            if res[i] is not None:
                info = fields[qtemp[i]]+": "+str(res[i])
            if missing[i] is not None:
                info = fields[qtemp[i]]+": **Missing the following information: \n  <Case 1>"
                c = 1
                for m in missing[i][0]:
                    info += ", "+fields[m]
                for ms in missing[i][1:]:
                    c += 1
                    info += "\n  <Case "+str(c)+'>'
                    for m in ms:
                        info += ", "+fields[m]
            self.response.append(info+'\n')
        # for qt in qtemp:
        #     self.response.append(fields[qt]+res[qt])

    def show(self):
        print(self.formQuestion())

class Calculator:
    def __init__(self, seps=util.seps):
        self.seps = seps
        self.taskDesc = ""
        self.abstracts = []
    
    def parseTask(self, tasks):
        ci = 0
        self.abstracts = []
        while True:
            if ci < len(tasks):
                c = tasks[ci]
                
                if c not in "\n\r":
                    self.taskDesc += c
                    ci += 1
                    continue

                while ci < len(tasks):
                    if tasks[ci] in "\n\r":
                        ci += 1
                    else:
                        break
            self.abstracts.append(self.parseDesc(len(self.abstracts)+1))
            self.taskDesc = "" 
            
            if ci >= len(tasks):
                break
        return self.abstracts
        
    def parseDesc(self, abi):
        self.readProgress = 0
        self.notMatchToken = ""
        ab = Abstract(self.taskDesc, abi)
        ab.clear()
        self.taskDesc += " e"
        while self.readProgress < len(self.taskDesc):
            if self.parsePlace(ab):
                continue
            date = self.parseDate()
            if date:
                if date.check():
                    ab.details[4] = date
                continue
            time = self.parseTime()
            if time:
                ab.details[3] = time
                continue

            num, unit = self.parseAngleAltitude()
            if num and num != '':
                if unit != "deg":
                    ab.details[9] = num
                    ab.details[10] = unit
                else:
                    ab.angles.append(num)
                continue

            lat, lon = self.parseLocation()
            if (lon, lat) != (None, None):
                if util.validLon(lon):
                    ab.details[5] = lon
                if util.validLat(lat):
                    ab.details[6] = lat
                continue
            gmt = self.parseGMT()
            if gmt is not None and gmt >= -12 and gmt <= 12:
                ab.details[0] = gmt
                continue
            
            query = self.parseQuery()
            if query:
                if query.isdigit() and int(query) not in ab.ivs:
                    ab.ivs.append(int(query))
                else:
                    i = querySet[query]
                    if i not in ab.queries:
                        if query == "below":
                            ab.negate = True
                        ab.queries.append(i)
                continue

            self.notMatchToken = ""

        ab.queryReduce()
        ab.formQuestion()
        return ab

    def parsePlace(self, ab):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()
        for row in self.table:
            if t == row[1].lower():
                ab.place = row[1]
                lat = row[2]
                if lat:
                    ab.details[6] = float(lat)
                lon = row[3]
                if lon:
                    ab.details[5] = float(lon)
                gmt = row[4]
                if gmt:
                    ab.details[0] = int(gmt)
                self.notMatchToken = ""
                return True
        self.notMatchToken = t
        return False    
    
    def parseDate(self):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()
        
        def toDayStr(tok):
            day = ""
            for c in tok:
                if c.isdigit():
                    day += c
                else:
                    break
            if day != "" and int(day) in range(1,32):
                return day
            return ""
        
        fromMonth = ""
        fromDay = ""
        
        if t in months:
            # July 4th
            fromMonth = months[t]
            t = self.readToken()
            if t == "the":
                t = self.readToken()
                fromDay = toDayStr(t)
            else:
                fromDay = toDayStr(t)
            
        elif t.isnumeric():  
            if int(t) in range(1,13) and self.precSymbol() in "_/\\":
                # 7/4 07-04
                fromMonth = t
                prg = self.readProgress
                t = self.readToken()
                fromDay = toDayStr(t)
                if fromDay == "":
                    t = fromMonth
                    fromMonth = ""
                    self.readProgress = prg
            elif len(t) == 4:
                # 0704
                if int(t[:2]) in range(1,13):
                    fromMonth = t[:2]
                    if int(t[2:]) in range(1,32):
                        fromDay = t[2:]
        
        if fromDay == "":
            # 4th of July
            fromDay = toDayStr(t)
            t0 = t
            prg = self.readProgress
            if fromDay != "":
                t = self.readToken()
                if t == "of":
                    t = self.readToken()
                    if t in months:
                        fromMonth = months[t]
                    
                elif t in months:
                    fromMonth = months[t]
                else:
                    t = t0
                    self.readProgress = prg

        if fromMonth != "" and fromDay != "":
            self.notMatchToken = ""
            return Date(int(fromMonth), int(fromDay))
        self.notMatchToken = t
        # print(t,1)
        return None
 
    def parseTime(self):
        fromHour = ""
        fromMinute = ""
        fromSecond = "0"
        day = 0
        noon = ""
        seps = ":_/\\"
        ams = ["pm", 'p.m.', "p.m", "am."]
        pms = ["am", "a.m.", "a.m", "am."]

        t = self.notMatchToken
        if t == "":
            t = self.readToken()

        if t.isnumeric():
            if len(t) in [4,6]:
                if int(t[:2]) <= 24:
                    fromHour = t[:2]
                    if t[:2] == "24":
                        day = 1
                    if int(t[2:4]) < 60:
                        fromMinute = t[2:4]
                        if len(t) == 6 and int(t[4:]) < 60:
                            fromSecond = t[4:]
                        prg = self.readProgress
                        t0 = t
                        t = self.readToken()
                        if t in ms+kms+degs:
                            self.notMatchToken = t0
                            self.readProgress = prg
                            return None
                        self.readProgress = prg
                        t = t0
            
            elif len(t) <= 2 and self.precSymbol() in seps :
                prg = self.readProgress
                if int(t) <= 24:
                    fromHour = t
                    t = self.readToken()
                    if t.isnumeric() and int(t) < 60:
                        fromMinute = t
                        if self.precSymbol() in seps:
                            t = self.readToken()
                            if t.isnumeric() and int(t) < 60:
                                fromSecond = t

                    else:
                        t = fromHour
                        self.readProgress = prg

        if fromHour != "" and fromMinute != "":
            if fromSecond != "":
               t = self.readToken() 
            fac = 0
            if t in ams:
                self.notMatchToken = ""
                if int(fromHour) in range(1, 12):
                    fac = 1
            elif t in pms:
                self.notMatchToken = ""
                if int(fromHour) == 12:
                    fac = -1
            else:
                self.notMatchToken = t

            return Time(int(fromHour)+fac*12, int(fromMinute), int(fromSecond), day)
        
        self.notMatchToken = t
        return None
    
    def parseLocation(self):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()

        loc1 = ("", '')
        loc2 = ("", '')
        
        def toCoord(tok):
            loc, i = util.findFloat(tok)
            d = ''
            if loc != "":
                if i < len(tok) and tok[i] in "news":
                    d = tok[i]
            else:
                return ("", '')

            prg = self.readProgress
            if d == '':
                t = self.readToken()
                if t in ["degree", "deg", "deg.", "d.", "d"]:
                    t = self.readToken()
                if t in ["north", "n"]:
                    d = 'n'
                elif t in ["south", "s"]:
                    d = 's'
                elif t in ["east", "e"]:
                    d = 'e'
                elif t in ["west", "w"]:
                    d = 'w'
                else:
                    self.readProgress = prg
                    return (loc,'')

            if loc[0] != '-' and d != '':
                if d == 's':
                    d = 'n'
                    loc = '-' + loc
                elif d == 'w':
                    d = 'e'  
                    loc = '-' + loc
            return (loc, d)                                    
        
        
        loc1 = toCoord(t)
        if loc1 != ("", ''):

            t = self.readToken()
            loc2 = toCoord(t)

            if loc1[1] != '':  
                if loc2 == ("", ''):
                    self.notMatchToken = t
                    match loc1[1]:
                        case 'e'|'w':
                            return (None, float(loc1[0]))
                        case 'n'|'s':
                            return (float(loc1[0]), None)
            # else:
            #     t = t0
            #     self.readProgress = prg

        if loc2 == ("", ''):
            self.notMatchToken = t
            return (None, None)
        
        self.notMatchToken = ""
        if loc1[1] == 'e':
            return (float(loc2[0]), float(loc1[0]))
        return (float(loc1[0]), float(loc2[0]))

    def parseGMT(self):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()
        
        gmt = 0
        if t in ["gmt", "utc"]:
            t = self.readToken()
            sym = t[0]
            if sym == '-':
                t = t[1:]
            if t.isnumeric():
                gmt = int(t)
                if sym == '-':
                    gmt = -gmt
                self.notMatchToken = ""
                return gmt
            
        self.notMatchToken = t
        return None
    
    def parseQuery(self):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()
        
        if t in ["above", "below"]:
            query = t
            t = self.readToken()
            if t in ["horizon", "ground"]:
                self.notMatchToken = ""
                return query
        
        elif t in querySet:
            if t in ["sunrise", "sunset", "noon"]:
                query = t
                t = self.readToken()
                if t != "time":
                    self.notMatchToken = t
                else:
                    self.notMatchToken = ""
                return query

            elif t == "time":
                t = self.readToken()
                if t != "zone":
                    self.notMatchToken = t
                    return "time"
                self.notMatchToken = ""
                return "zone"

            self.notMatchToken = ""
            return t
            
        elif t in ["versus", "vs", "over", "about", "regarding", "each", "every"]:
            t = self.readToken()
            if t in querySet:
                iv = querySet[t] 
                if iv in [3,4,9,6]:
                    self.notMatchToken = ""
                    return str(iv)

        self.notMatchToken = t
        return None
            
    def mapUnit(tok):
        if tok in degs:
            return "deg"
        elif tok in ms:
            return "m"
        elif tok in kms:
            return "km"
        return None

    def parseAngleAltitude(self):
        t = self.notMatchToken
        if t == "":
            t = self.readToken()

        ang, i = util.findFloat(t)
        cont = ""
        while i < len(t):
            c = t[i]
            if c in ".-":
                break
            cont += t[i]
            i += 1

        if ang != "":
            unit = Calculator.mapUnit(cont)
            if unit:
                self.notMatchToken = ""
                return float(ang), unit

        t0 = t
        prg = self.readProgress
        t = self.readToken()
        if ang != "":
            unit = Calculator.mapUnit(t)
            if unit:
                self.notMatchToken = ""
                return float(ang), unit
        t = t0
        self.readProgress = prg

        self.notMatchToken = t
        return None, None
        
    def readToken(self):
        haveToken = False
        token = ""
        while self.readProgress < len(self.taskDesc):
            c = self.taskDesc[self.readProgress]
            if not haveToken:
                if c in self.seps:
                    haveToken = True
                else:
                    if c.isalpha():
                        token += c.lower()
                    else:
                        token += c
            elif c not in self.seps:
                return token
            self.readProgress += 1
        return token
    
    def precSymbol(self):
        return self.taskDesc[self.readProgress-1]
       

# c = Calculator("~`!@#$%^&*()_+={[]|\\:;<,>?/'\"\n }")
# c.parseTask("which date london 51n 0.1w sun height is 30 degree at 15:00 gmt +1")
# for ab in c.abstracts:
#     print(ab.interpret)
#     print(ab.conditions)

# print(util.findFloat("30.5.5ks ndf"))
# print(util.findFloat("0.-2e2.5e25"))
# print("-3".isnumeric())
# ab = Abstract("", 1)
# ab.clear()
# ab.details[6] = 35
# ab.details[5] = 120
# ab.details[0] = 8
# ab.details[3] = Time(12,0,0,0)
# ab.details[4] = Date(6,22)
# ab.queries = [3]
# ab.formResponse()
# print(ab.response)

'''
calculate the sunset hour of london 51N 0.1E gmt+1 on june 25
what is the sunrise hour at chicago gmt-5 51N 0w on july 4th?
calculate the sunset hour of london on june 25
what time of dhabi on june 25 is the sun height 75 degree?
what time of dhabi 24_N 95_E gmt 4 on june 25 is the sun 75 degree above horizon and direction at 315 deg?
what date is dubai 24_N 95_E at the time of 17:25 when sun direction is 285 deg?
'''



