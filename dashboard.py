from flask import Flask, render_template, request
import queryProcess as sc
import record
import util

app = Flask(__name__)
calc = sc.Calculator()
calc.table = util.readTable(util.dbfile, True)

@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    tasks = request.form.get('taskDesc')
    adding = request.form.get('adding')
    print(request.form)
    if tasks is not None and tasks != "":
        calc.parseTask(tasks)

    else: 
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
            calc.abstracts[abi].formResponse()
        elif request.form.get("Plot"+str(ab.num)):
            calc.abstracts[abi].formPlot()      

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
        
    return render_template('index.html', abstracts=calc.abstracts, abnum=len(calc.abstracts), abi=calc.abi)

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
        calc.table = util.readTable(util.dbfile, True)
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
        calc.table = util.readTable(util.dbfile, True)

    return render_template('maps.html', table=util.readTable(record.dbfile, False))

    

@app.route('/information', methods=['GET', 'POST']) # show the main page
def infomation():
    return render_template('info.html', info=request.form.get('info'))

@app.route('/plot', methods=['GET', 'POST']) # show the main page
def plot():
    return render_template('plot.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

