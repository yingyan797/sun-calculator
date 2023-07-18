import pandas as pd
from sunTime import sunTimes, calcSun
from sunPosition import sunTimePosition
from dateTime import Date, Time

def timeTests():
    print("\n"+"--Vladivostok 0622--")
    calcSun(43.12, 131.9, 10, Date(6,22))
    print("\n"+"--Calais 0701--")
    calcSun(50.96, 1.85, 2, Date(7,1))

def posTest():
    print(sunTimePosition(51, 0, 1, Date(9,22), Time(12, 0, 45, 0)))

def posTime():
    for h in range(12,15):
        for m in range(60):
          time = Time(h,m,0,0)
          print(time.show(),"--",sunTimePosition(51, 0, 1, Date(6,22), time))

def posDate():
    for d in range(30):
        date = Date(6, d)
        print(date.show(),"--",sunTimePosition(51, 0, 1, date, Time(15,0,0,0)))

def posLocation():
    for lat in range(55):
        print(lat,"N,",0," -- ",sunTimePosition(lat, 0, 1, Date(6,22), Time(15,0,0,0)))
        

def tabulate():
    data = []
    cols = ['London', 'New York', 'Tokyo']
    lats = [51.51, 40.74, 35.67]
    lons = [-0.11, -73.98, 139.74]
    # Assume London uses GMT+0 and New York uses GMT-4 at March 21, which is usually the case
    gmts = [[0,1,1,0], [-4, -4, -4, -5], [9,9,9,9]]
    dates = [Date(3,21), Date(6,22), Date(9,23), Date(12,22)]
    indexes = ["0321", "0622", "0923", "1222"]
    for j in range(4):
        times = []
        for i in range(3):
            sr, ss = sunTimes(lats[i], lons[i], gmts[i][j], dates[j])
            times.append(sr.show()+","+ss.show())
        data.append(times)
        
    sunTable = pd.DataFrame(data, indexes, cols)
    print(sunTable)

posLocation()