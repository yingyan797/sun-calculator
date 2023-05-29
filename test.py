import pandas as pd
from model import sunTimes, calcSun
from dateTime import Date

def tests():
    print("\n"+"--Vladivostok 0622--")
    calcSun(49.6, -1.8, 2, Date(6,22))
    print("\n"+"--Calais 0701--")
    calcSun(50.96, 1.85, 2, Date(7,1))

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

tests()