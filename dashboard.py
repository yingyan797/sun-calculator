from flask import Flask, render_template, request,session, redirect, flash, jsonify
import calculator as sc

app = Flask(__name__)
calc = sc.Calculator("~`!@#$%^&*()_-+={[]|\\:;<,>?/'\"\n }", sc.Abstract())


@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    print(request.form)
    task = request.form.get('taskDesc')
    fq = ""
    if task is not None:
        calc.taskDesc = task
        ab = calc.parseTask()
        fq = ab.formQuestion()
    
    if len(request.form) >= 0:
        for (k,v) in request.form.items():
            fq += k+": "+v+"; "
    
    return render_template('index.html', understand=fq)

@app.route('/maps', methods=['GET', 'POST']) # show the main page
def maps():
    loc = request.form.get('location')
    return render_template('maps.html', location = loc, url="https://google.com/maps/place/"+loc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

