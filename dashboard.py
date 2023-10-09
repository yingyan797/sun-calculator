from flask import Flask, render_template, request,session, redirect, flash, jsonify
import calculator as sc

app = Flask(__name__)
calc = sc.Calculator("~`!@#$%^&*()_-+={[]|\\:;<,>?/'\"\n }")

@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    tasks = request.form.get('taskDesc')
    print(request.form)
    if tasks is not None and tasks != "":
        calc.parseTask(tasks)
    else:
        for abi in range(len(calc.abstracts)):
            ab = calc.abstracts[abi]
            td = request.form.get("Question"+str(ab.num))
            if td is not None and td != ab.taskDesc:
                calc.taskDesc = td
                calc.abstracts[abi] = calc.parseDesc(ab.num)

    return render_template('index.html', abstracts=calc.abstracts)

@app.route('/maps', methods=['GET', 'POST']) # show the main page
def maps():
    loc = request.form.get('location')
    return render_template('maps.html', location = loc, url="https://google.com/maps/place/"+loc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

