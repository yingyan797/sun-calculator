from dateTime import Date, Time
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

class Abstract:
    def __init__(self, taskDesc, num):
        self.taskDesc = taskDesc
        self.num = num
        self.interpret = ""
        self.response = ""

    def clear(self):
        self.queries = []
        self.angles = []
        self.gmt = 0
        self.details = [None for i in range(10)]
        self.interpret = ""

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
            else:
                qi += 1

    def formQuestion(self):
        if self.queries == []:
            self.interpret += "Sorry, I can't unserstand your question."
            return
        qs = ["What is the height angle of the sun (below horizon)?", "What is the height angle of the sun (above horizon)?", 
              "What is the direction of the sun (angle clockwise from North)?", "What time of the day is it when", 
              "Which date is it when", "What is the longitude of a location where", "What is the latitude of a location where", 
              "When does sunrise occur?", "When does sunset occur?", "What altitude of observation (in meters) is it where"]
        self.interpret += qs[self.queries[0]]
        for qi in self.queries[1:]:
            self.interpret += "\nand\n"+qs[qi]

        if self.details[1]:
            self.interpret += " the sun is at "+str(self.details[1])+" degree above horizon?"
        if self.details[2]:
            self.interpret += " the sun's direction is "+str(self.details[2])+" degree clockwise from North?"
        
        self.interpret += " Given that:\n"
        if self.details[6] is not None:
            self.interpret += "  At geographical location "+util.showLat(self.details[6])
        if self.details[5] is not None:
            self.interpret += " "+util.showLon(self.details[5])+"\n"
        if self.gmt:
            self.interpret += "  Time zone is GMT"
            if self.gmt > 0:
                self.interpret += '+'+str(self.gmt)+'\n'
            else:
                self.interpret += str(self.gmt)+'\n'
        if self.details[4]:
            self.interpret += "  On the date "+self.details[4].show()
        if self.details[3]:
            self.interpret += "  At the time of "+self.details[3].show()
        if self.details[9]:
            self.interpret += " Observing at an altitude of "+str(self.details[9])+self.details[0]
        

    def formResponse(self):
        resp = 0  
    
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
            if lon is not None:
                ab.details[6] = lat
                ab.details[5] = lon
                continue
            
            gmt = self.parseGMT()
            if gmt:
                ab.gmt = gmt
                continue
            
            num, unit = self.parseAngleAltitude()
            if num:
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

            if loc2 == ("", '') and loc1[1] != '':
                self.readProgress = prg
                self.notMatchToken = t0
                return (None, float(loc1[0]))
            else:
                t = t0
                self.readProgress = prg

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
            sym = self.precSymbol()
            t = self.readToken()
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
# print(float("-.25"))

'''
calculate the sunset hour of london 51N 0.1E gmt+1 on june 25
what is the sunrise hour at chicago gmt-5 51N 0w on july 4th?
calculate the sunset hour of london on june 25
what time of dhabi on june 25 is the sun height 75 degree?
what time of dhabi 24_N 95_E gmt 4 on june 25 is the sun 75 degree above horizon and direction at 315 deg?
what date is dubai 24_N 95_E at the time of 17:25 when sun direction is 285 deg?
'''



