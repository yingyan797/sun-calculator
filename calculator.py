from dateTime import Date, Time

months = {
    "january": "1",
    "jan": "1",
    "february": "2",
    "feb": "2",
    "march": "3",
    "mar": "3",
    "april": "4",
    "apr": "4",
    "may": "5",
    "june": "6",
    "jun": "6",
    "july": "7",
    "jul": "7",
    "august": "8",
    "aug": "8",
    "september": "9",
    "sep": "9",
    "october": "10",
    "oct": "10",
    "november": "11",
    "nov": "11",
    "december": "12",
    "dec": "12"
}

class Calculator:
    def __init__(self, seps):
        self.seps = seps
        self.taskDesc = ""
        self.readProgress = 0
        self.notMatchToken = ""

    def prompt(self):
        print("Hello earth scientist, I'm sun calculator.")

        while True:
            self.taskDesc = input("**Please describe what you want to calculate, or press Enter to skip and fill a form.\n--")
            if self.taskDesc == "":

                return
            elif self.parseTask():
                return
            else:
                print("Sorry, I cannot understand your request. Could you describe differently?")
    
    def parseTask(self):
        while self.readProgress < len(self.taskDesc):
            date = self.parseDate()
            if date:
                print("Date:",date.show())
                continue
            time = self.parseTime()
            if time:
                print("Time:",time.show())
                continue
            loc = self.parseLocation()
            if loc:
                print("Lat:",loc[0], "Lon:",loc[1])
            
            self.notMatchToken = ""

        
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
        
        if t in months.keys():
            # July 4th
            fromMonth = months[t]
            t = self.readToken()
            if t == "the":
                t = self.readToken()
                fromDay = toDayStr(t)
            else:
                fromDay = toDayStr(t)
            
        elif t.isnumeric():  
            if int(t) in range(1,13) and self.precSymbol() in ",_/-\\":
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
                    if t in months.keys():
                        fromMonth = months[t]
                    
                elif t in months.keys():
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
        seps = ":,_/-\\"

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
            
            elif len(t) == 2 and self.precSymbol() in seps :
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
            loc = ""
            deci = False

            if tok[0] == '.':
                deci = True
                loc += "0."
                tok = tok[1:]

            for c in tok:
                if c == '.':
                    if not deci:
                        loc += '.'
                        deci = True
                    else:
                        return (loc, '')

                if c.isdigit():
                    loc += c
                if loc != "":
                    if c in 'ne':
                        return (loc, c)
                    if c == 's':
                        return ('-'+loc, 'n')
                    if c == 'w':
                        return ('-'+loc, 'e')
                
            return (loc, '')
        
        prg = self.readProgress
        t0 = t
        loc1 = toCoord(t)
        if loc1 != ("", ''):
            if loc1[1] == '' and self.precSymbol() == '-':
                loc1 = '-'+loc1[0], 'n'

            t = self.readToken()
            loc2 = toCoord(t)
            if loc2 != ("", ''):
                if loc2[1] == '' and self.precSymbol() == '-':
                    loc2 = '-'+loc2[0], 'e'
            else:
                self.readProgress = prg
                t = t0

        if loc1 == ("", '') or loc2 == ("", ''):
            self.notMatchToken = t
            return None
        
        if loc1[1] == 'e':
            return (float(loc2[0]), float(loc1[0]))
        return (float(loc1[0]), float(loc2[0]))

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
       

c = Calculator("~`!@#$%^&*()_-+={[]|\\:;<,>?/'\"\n }")
c.taskDesc = "what time of dhabi on june 25, 27 of july is the 12:31_15 am sun at 103E, 37N height 75 degree?"
c.parseTask()


'''
calculate the sunset hour of london on june 25
what time of dhabi on june 25 is the sun height 75 degree?
what date is dubai 17:25 sun direction 285?
'''



