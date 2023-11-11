from flask import Flask, render_template, request
import queryProcess as sc
import record
import os
import glob

app = Flask(__name__)
calc = sc.Calculator()
calc.table = record.readPlaces(True)

@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    print(request.form)
    written = False
    if request.form.get("clearDesc"):
        calc.tasks = ""
    elif not calc.tasks:
        tasks = request.form.get('taskDesc')
        if not tasks:
            qfile = request.form.get("qfile")
            if qfile:
                f = open("static/questions/"+qfile, "r")
                tasks = f.read()
        if tasks:
            calc.parseTask(tasks)
            written = True
    if not written:
        adding = request.form.get('adding')
        abf = None
        newForm = False
        emptyForm = True
        if calc.abstracts != [] and adding and adding != '':
            abf = calc.abstracts[int(adding)-1]
            abf.conditions = []
        else:
            newForm = True
            abf = sc.Abstract("", 1)
            abf.clear()
        
        qs = ["QHeight", "QDirection", "QTime", "QDate",  "QLat", "Sunrise", "Sunset", "QAlt"]
        for i in range(4):
            if i+1 not in abf.queries and request.form.get(qs[i]) == 'on':
                abf.queries.append(i+1)
                emptyForm = False 
        for i in range(4, 8):
            if i+2 not in abf.queries and request.form.get(qs[i]) == 'on':
                abf.queries.append(i+2)
                emptyForm = False 
        if 0 not in abf.queries and request.form.get("TZ") == 'on':
            abf.queries.append(0)
            emptyForm = False 
        if 11 not in abf.queries and request.form.get("Noon") == 'on':
            abf.queries.append(11)
            emptyForm = False 

        ps = ["PTime", "PDate", "PLat", "PAlt"]
        ivs = [3,4,6,9]
        for i in range(len(ps)):
            if ivs[i] not in abf.ivs and request.form.get(ps[i]) == 'on':
                abf.ivs.append(ivs[i])
                emptyForm = False

        lon = request.form.get('Longitude') 
        ew = request.form.get('EW')
        if lon:
            abf.addLon(float(lon), ew)
            emptyForm = False 

        lat = request.form.get('Latitude') 
        ns = request.form.get('NS')
        if lat:
            abf.addLat(float(lat), ns)
            emptyForm = False 
        
        alt = request.form.get('Altitude')
        unit = request.form.get('unit')
        if alt:
            abf.addAltitude(float(alt), unit)
            emptyForm = False 

        ds = ["Height", "Direction"]
        for i in range(2):
            v = request.form.get(ds[i])
            if v:
                abf.details[i+1] = float(v)
                emptyForm = False 

        gmt = request.form.get('GMT')
        if gmt:
            abf.details[0] = int(gmt)
            emptyForm = False 

        mo = request.form.get('Month')
        d = request.form.get('Day')
        if mo and d:
            abf.addDate(mo, d)
            emptyForm = False 

        h = request.form.get('Hour')
        mi = request.form.get('Minute')
        s = request.form.get('Second')
        if h and mi:
            abf.addTime(h, mi, s)
            emptyForm = False

        abf.queryReduce()
        abf.formQuestion()
        if newForm and not emptyForm:
            calc.abstracts = [abf]
            print("New form")

    for abi in range(len(calc.abstracts)):
        ab = calc.abstracts[abi]
        td = request.form.get("Question"+str(ab.num))
        rs = request.form.get("Reset"+str(ab.num))
        if rs or (td is not None and td != ab.taskDesc):
            calc.taskDesc = td
            calc.abstracts[abi] = calc.parseDesc(ab.num)
        elif request.form.get("Calculate"+str(ab.num)):
            if ab.formResponse():
                res = ""
                for r in ab.response:
                    res += r+","
                record.registerCalc(ab.interpret, ab.conditions, res)
        elif request.form.get("Plot"+str(ab.num)):
            ab.formPlot()

    abi = request.form.get("abiEnter")
    if not abi:
        abi = request.form.get("abiClick")
        if not abi:
            if not calc.abi:
                abi = 1
            elif request.form.get("abip"):
                abi = (calc.abi - 1) % len(calc.abstracts)
            elif request.form.get("abin"):
                abi = (calc.abi + 1) % len(calc.abstracts)
    
    if abi is not None:
        if abi == 0:
            calc.abi = len(calc.abstracts)
        else:
            calc.abi = int(abi)
        
    display = []
    displayNum = 5
    if calc.abi is not None:
        display.append(calc.abi)
        left = min(calc.abi-1, int((displayNum-1)/2))
        right = displayNum-1-left
        i = calc.abi
        while left >= 1:
            i -= 1
            left -= 1
            display = [i] + display
        i = calc.abi
        while right >= 1 and i < len(calc.abstracts):
            i += 1
            right -= 1
            display.append(i)
        i = display[0]
        while right >= 1 and i > 2:
            i -= 1
            right -= 1
            display = [i] + display

        if display[0] > 1:
            display = [0] + display
        if display[-1] < len(calc.abstracts):
            display.append(-1)

    return render_template('index.html', abstracts=calc.abstracts, tasks=calc.tasks,
                           abis = {"abnum": len(calc.abstracts), "abi": calc.abi, "display": display})

@app.route('/maps', methods=['GET', 'POST']) # show the main page
def maps():
    loc = request.form.get('location')
    if loc and loc != "":
        lon = request.form.get('Longitude')
        lat = request.form.get('Latitude')
        ew = request.form.get('EW')
        ns = request.form.get('NS')
        gmt = request.form.get('GMT')
        table = record.registerPlace(loc, lon, lat, ew, ns, gmt)
        calc.table = record.readPlaces(True)
        return render_template('maps.html', location=loc, table=table)
    
    pn = 1
    change = False
    while True:
        p = request.form.get("place"+str(pn))
        if p == None:
            break
        d = request.form.get("delete"+str(pn))
        if d:
            change = True
            record.deletePlace(p)
        u = request.form.get("update"+str(pn))
        if u:
            change = True
            c = request.form.get("coord"+str(pn))
            g = request.form.get("gmt"+str(pn))
            record.updatePlace(p, pn-1, c, g)
        pn += 1
    if change:
        calc.table = record.readPlaces(True)

    return render_template('maps.html', table=record.readPlaces(False))

    

@app.route('/information', methods=['GET', 'POST']) # show the main page
def infomation():
    return render_template('info.html', info=request.form.get('info'))

@app.route('/history', methods=['GET', 'POST']) # show the main page
def history():
    if request.form.get("clearGraphs"):
        files = glob.glob('static/plots/*')
        for f in files:
            os.remove(f)
        f = open(record.plotFile, "w")
        f.write("")
        f.close()
    elif request.form.get("clearCalcs"):
        f = open(record.calcFile, "w")
        f.write("")
        f.close()

    mode = request.form.get("mode")
    hpair = ([],[])
    left = True
    hs = []
    if mode == "Show plot history":
        hs = record.readPlots()
    else:
        hs = record.readCalcs()
    for info in hs:
        if left:
            hpair[0].append(info)
            left = False
        else:
            hpair[1].append(info)

    return render_template('history.html', mode=mode, hpair=hpair, num=len(hs))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

