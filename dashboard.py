from flask import Flask, render_template, request,session, redirect, flash, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST']) # show the main page
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

