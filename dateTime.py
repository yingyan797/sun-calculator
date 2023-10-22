ydays = 365.25  # The number of days per year on average
dsecs = 86400   # The number of seconds per day
# mdays: The number of days in each months
# on average, assume February has 28.25 days
mdays = [31,28.25,31,30,31,30,31,31,30,31,30,31]
months = ["January", "February", "March", "April", 
          "May", "June", "July", "August", 
          "September", "October", "November", "December"]
 
class Date:
    def __init__(self, m, d):
        self.month = m
        self.day = d
    def before(self, other):
        if self.month < other.month:
            return -1
        if self.month > other.month:
            return 1
        return self.day - other.day
    def diff(self, other):
        spanMonths = []
        dayDiff = other.day - self.day
        cmp = self.before(other)
        m1 = 0
        m2 = 0
        if cmp == 0:
            return (0, [], 0)
        if cmp > 0:
            m1 = other.month
            m2 = self.month
            dayDiff *= (-1)
        else:
            m2 = other.month
            m1 = self.month 
        while m1 < m2:
            spanMonths.append(m1)
            m1 += 1
        return (cmp, spanMonths, dayDiff)
    
    def daysToRef(self, ref):
        (cmp, spanMonths, dayDiff) = self.diff(ref)
        days = 0
        for m in spanMonths:
            days += mdays[m-1]
        days += dayDiff
        if cmp < 0:
            return (-1)*days
        return days
    
    def show(self):
        return months[self.month-1]+" "+str(self.day)


class Time:
    def __init__(self, h, m, s, d):
        self.hour = h
        self.minute = m
        self.second = s
        self.day = d
    # subtract time by a period (diff :: Time)
    def pred(self, diff):
        s = self.second - diff.second
        m = self.minute - diff.minute
        h = self.hour - diff.hour
        d = self.day - diff.day
        if s < 0:
            s += 60
            m -= 1
        if m < 0:
            m += 60
            h -= 1
        if h < 0:
            h += 24
            d -= 1            
        return Time(h,m,s,d)
    # add time by a period (diff :: Time)
    def succ(self, diff):
        s = self.second + diff.second
        m = self.minute + diff.minute
        h = self.hour + diff.hour
        d = self.day + diff.day
        if s >= 60:
            s -= 60
            m += 1
        if m >= 60:
            m -= 60
            h += 1
        if h >= 24:
            h -= 24
            d += 1
        return Time(h,m,s,d)
    
    def toSecs(self):
        return self.day*dsecs + self.hour*3600 + self.minute*60 + self.second
    
    def show(self):
        m = str(self.minute)
        s = str(int(self.second))
        h = str(self.hour)
        d = ""
        if self.minute < 10:
            m = "0"+m
        if self.second < 10:
            s = "0"+s
        if self.hour < 10:
            h = "0"+h
        if self.day > 0:
            d = " <"+str(self.day)+" day after>"
        if self.day < 0:
            d = " <"+str(-self.day)+" day before>"
        return h+":"+m+":"+s+d
    