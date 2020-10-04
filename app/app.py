"""Import"""

# Web
from flask import Flask, render_template, request
import sys

# Map
from bokeh.resources import CDN
from bokeh.embed import file_html

# App
from appmaps import getMap

app = Flask(__name__)

last_date = "20150601"

# Load the template by default
@app.route('/')
def index():
    html = file_html(getMap(last_date), CDN, "my plot")
    return render_template("index.html", plot=html)

# Receive the selected date for the high precipitation study
@app.route('/api', methods = ['POST','GET'])
def api():
    date = request.values.get('data', '')
    date_f = date.split("-")
    global last_date
    last_date = date_f[0]+date_f[1]+date_f[2]
    html = file_html(getMap(last_date), CDN, "my plot") 
    return html
    
# Render the correct template depending on the scenario   
@app.route('/', methods=['POST','GET'])
def msg_management():
    selectedValue = request.form['options']

    if selectedValue == "hurricanes":
        html = file_html(getMap(last_date), CDN, "my plot")
        return render_template('index.html', plot=html)       
    else:
        html = file_html(getMap(last_date, 2), CDN, "my plot")         
        return render_template("index.html", plot=html)


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
