from flask import Flask, render_template, request,session, redirect, flash, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    print(request.form)
    return render_template('index.html')

@app.route('/maps', methods=['GET', 'POST']) # show the main page
def maps():
    loc = request.form.get('location')
    return render_template('maps.html', location = loc, url="https://google.com/maps/place/"+loc)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

