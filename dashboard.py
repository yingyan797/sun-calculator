from flask import Flask, render_template, request,session, redirect, flash, jsonify
import calculator as sc

app = Flask(__name__)
calc = sc.Calculator("~`!@#$%^&*()_+={[]|\\:;<,>?/'\"\n }")

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

        lon = request.form.get('Longitude') 
        ew = request.form.get('ew')
        if lon:
            abf.addLon(float(lon), ew)
            emptyForm = False 

        lat = request.form.get('Latitude') 
        ns = request.form.get('ns')
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
        if rs or td is not None and td != ab.taskDesc:
            calc.taskDesc = td
            calc.abstracts[abi] = calc.parseDesc(ab.num)


    return render_template('index.html', abstracts=calc.abstracts)

@app.route('/maps', methods=['GET', 'POST']) # show the main page
def maps():
    loc = request.form.get('location')
    return render_template('maps.html', location = loc, url="https://google.com/maps/place/"+loc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

