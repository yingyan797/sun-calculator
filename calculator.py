from dateTime import Date, Time
import sunTime as st
import sunPosition as sp
import util

months = {
    "january": "1","jan": "1","february": "2","feb": "2","march": "3","mar": "3","april": "4","apr": "4","may": "5",
    "june": "6","jun": "6","july": "7","jul": "7","august": "8","aug": "8","september": "9","sept": "9","sep": "9",
    "october": "10","oct": "10","november": "11","nov": "11","december": "12","dec": "12"
}

querySet = {
    "height": 1, "ht": 1, "high": 1, "direction": 2, "dir": 2, "orientation": 2, "time": 3, "date": 4, "day": 4,
    "longitude": 5, "lon": 5, "latitude": 6, "lat": 6, "sunrise": 7, "sunset": 8, "above": 1, "below": 0,
    "altitude": 9, "elavation": 9
}

sunriseset = [(st.sunTimes, [6,5,0,4]), (st.sunTimeAltitude, [6,5,0,4,9])]

answerMap = {
    1: [(sp.sunHeight, [6,5,0,4,3])], 2: [(sp.sunPosition, [6,5,0,4,3])], 
    3: [(sp.sunHeightTimeLim, [6,5,0,4,1]), (sp.sunDirectionTimeLim, [6,5,0,4,2])],
    4: [(sp.sunDateLim, [6,5,0,3,1]), (sp.sunDateLim, [6,5,0,3,2])],
    7: sunriseset, 8: sunriseset
}

class Abstract:
    def __init__(self, taskDesc, num):
        self.taskDesc = taskDesc
        self.num = num
        self.interpret = ""
        self.conditions = []
        self.given = []
        self.response = None

    def clear(self):
        self.queries = []
        self.angles = []
        self.details = [None for i in range(11)]
        self.interpret = ""
        self.conditions = []
        self.response = None

    def addDate(self, month, day):
        self.details[4] = Date(int(month), int(day))
    
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
            if q <= 1 and len(self.angles) > 0:
                self.queries.pop(qi)
                self.details[1] = self.angles.pop(0)
                if q == 0:
                    self.details[1] *= -1
            elif q == 2 and len(self.angles) > 0:
                self.queries.pop(qi)
                self.details[2] = self.angles.pop(0)
            elif q == 5 and self.details[6] == None:
                self.queries.pop(qi)
            elif q == 4 and self.details[4]:
                self.queries.pop(qi)
            elif q == 3 and self.details[3]:
                self.queries.pop(qi)
            elif q == 9 and self.details[9]:
                self.queries.pop(qi)
            else:
                qi += 1

    def formQuestion(self):
        self.interpret = ""
        if self.queries == []:
            self.interpret += "Sorry, I can't unserstand your question."
            return
        qs = ["What is the height angle of the sun (below horizon)?", "What is the height angle of the sun (above horizon)?", 
              "What is the direction of the sun (angle clockwise from North)?", "What time of the day is it when", 
              "Which date is it when", "What is the longitude of a location where", "What is the latitude of a location where", 
              "When does sunrise occur?", "When does sunset occur?", "What altitude of observation (in meters) is it where"]
        self.interpret += qs[self.queries[0]]
        for qi in self.queries[1:]:
            self.interpret += "  "+qs[qi]

        if self.details[1]:
            self.interpret += " the sun is at "+str(self.details[1])+" degree above horizon?"
        if self.details[2]:
            self.interpret += " the sun's direction is "+str(self.details[2])+" degree clockwise from North?"
        
        lat, lon = self.details[6], self.details[5]
        if lat != None and lon != None:
            self.conditions.append("At geographical coordinate: "+util.showLat(lat)+", "+util.showLon(lon))
        else:
            if lat != None:
                self.conditions.append("At Latitude: "+util.showLat(lat))
            elif lon != None:
                self.conditions.append("At Longitude: "+util.showLon(lon))

        if self.details[4]:
            self.conditions.append("On date: "+self.details[4].show())
        if self.details[3]:
            self.conditions.append("At local time: "+self.details[3].show())
        if self.details[0]:
            gmt = self.details[0]
            c = "Time zone: GMT"
            if gmt > 0:
                c += '+'+str(gmt)
            else:
                c += str(gmt)
            self.conditions.append(c)
        if self.details[9]:
            self.conditions.append("Observing at altitude: "+str(self.details[9])+self.details[10])
    
    def formResponse(self):
        self.response = None
        def checkAnswer(maps):
            missing = []
            for m in maps:
                mg = []
                for cond in m[1]:
                    if not self.details[cond]:
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
        
        res = []
        res78 = []
        missing = []
        qtemp = []
        q1 = False
        temp78 = []
        miss78 = None
        for q in self.queries:
            if q == 1:
                q1 = True
            elif q == 2:
                r,m = checkAnswer(answerMap[2])
                if r:
                    if q1:
                        qtemp.append(1)
                        res += [r[0], r[1]]
                    else:
                        res.append(r[1]) 
                else:
                    missing.append(m)
                    if q1:
                        missing.append(m)
                qtemp.append(2)
                q1 = False
            elif q in [7,8]:
                if len(temp78) < 1:
                    r,miss78 = checkAnswer(answerMap[7])
                    if r:
                        res78 += [r[0], r[1]]
                temp78.append(q)
            
            elif q in answerMap:
                maps = answerMap[q]
                qtemp.append(q)
                r, m = checkAnswer(maps)
                if r:
                    res.append(r)
                else:
                    missing.append(m)

        if q1:
            qtemp.append(1)
            r,m = checkAnswer(answerMap[1])
            if r:
                res.append(r) 
            else:
                missing.append(m)
        qtemp += temp78
        for i in temp78:
            res.append(res78[i-7])
            if not miss78 is None:
                missing.append(miss78)
        
        self.response = len(qtemp), qtemp, res, missing

    def show(self):
        print(self.formQuestion())

class Calculator:
    def __init__(self, seps):
        self.seps = seps
        self.taskDesc = ""
        self.abstracts = []
    
    def parseTask(self, tasks):
        ci = 0
        self.abstracts = []
        while True:
            if ci < len(tasks):
                c = tasks[ci]
                
                if c != '\n':
                    self.taskDesc += c
                    ci += 1
                    continue

                while ci < len(tasks):
                    if tasks[ci] == '\n':
                        ci += 1
                    else:
                        break
            self.abstracts.append(self.parseDesc(len(self.abstracts)+1)) 
            
            if ci >= len(tasks):
                break
        return self.abstracts
        
    def parseDesc(self, abi):
        self.readProgress = 0
        self.notMatchToken = ""
        ab = Abstract(self.taskDesc, abi)
        ab.clear()

        while self.readProgress < len(self.taskDesc):
            date = self.parseDate()
            if date:
                ab.details[4] = date
                continue
            time = self.parseTime()
            if time:
                ab.details[3] = time
                continue
            lat, lon = self.parseLocation()
            print("loc",lat, lon)
            if lon is not None:
                ab.details[6] = lat
                ab.details[5] = lon
                continue
            
            gmt = self.parseGMT()
            if gmt:
                ab.details[0] = gmt
                continue
            
            num, unit = self.parseAngleAltitude()
            if num and num != '':
                if unit != "deg":
                    ab.details[9] = num
                    ab.details[0] = unit
                else:
                    ab.angles.append(num)
                continue

            query = self.parseQuery()
            if query:
                i = querySet[query]
                if i not in ab.queries:
                    ab.queries.append(i)

            self.notMatchToken = ""

        self.taskDesc = ""
        ab.queryReduce()
        ab.formQuestion()
        return ab

    
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
                                noon = t

                    else:
                        t = fromHour
                        self.readProgress = prg

        if fromHour != "" and fromMinute != "":
            self.notMatchToken = ""
            if noon == "":
                t = self.readToken()
                noon = t
            fac = 0
            if noon in ["pm", 'p.m.', "p.m", "am."] and int(fromHour) in range(1, 12):
                fac = 1
            elif noon in ["am", "a.m.", "a.m", "am."] and int(fromHour) == 12:
                fac = -1

            return Time(int(fromHour)+fac*12, int(fromMinute), int(fromSecond), day)
        
        self.notMatchToken = t
        # print(t,2)
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
            if loc[0] != '-' and d == '':
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

            prg = self.readProgress
            t0 = t
            t = self.readToken()
            loc2 = toCoord(t)

            if loc1[1] != '':  
                if loc2 == ("", ''):
                    self.readProgress = prg
                    self.notMatchToken = t0
                    return (None, float(loc1[0]))
            # else:
            #     t = t0
            #     self.readProgress = prg

        if loc2 == ("", ''):
            self.notMatchToken = t
            return (None, None)
        
        self.notMatchToken = ""
        print("nmt",self.taskDesc[self.readProgress:])
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
            self.notMatchToken = ""
            return t
            
        self.notMatchToken = t
        return None
            
    def mapUnit(tok):
        degs = ["degree", "deg", "d"]
        ms = ["m", "meter", "meters", "metre", "metres"]
        kms = ["km", "kilometer", "kilometers", "kilometre", "kilometres"]
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
# c.parseTask("Abu dhabi sunset hour\nlondon sun height july 4")
# print(util.findFloat("0.-2e2.5e25"))
# print("-3".isnumeric())
# ab = Abstract("", 1)
# ab.clear()
# ab.details[6] = 35
# ab.details[5] = 120
# ab.details[0] = 8
# ab.details[3] = Time(12,0,0,0)
# ab.details[4] = Date(6,22)
# ab.queries = [3,4]
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



