from temporal import Date, Time
from queryAbstract import Abstract
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

degs = ["degree", "deg", "d"]
ms = ["m", "meter", "meters", "metre", "metres"]
kms = ["km", "kilometer", "kilometers", "kilometre", "kilometres"]

class Calculator:
    def __init__(self, seps=util.seps):
        self.seps = seps
        self.tasks = ""
        self.taskDesc = ""
        self.abi = None
        self.abstracts = []
    
    def parseTask(self, tasks):
        ci = 0
        self.tasks = tasks
        self.abstracts = []
        self.abi = None
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



