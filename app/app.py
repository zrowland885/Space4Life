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


@app.route('/')
def index():
    print('Before render_template', file=sys.stdout)
    return render_template("index.html")


@app.route('/', methods=['POST','GET'])
def msg_management():
    selectedValue = request.form['options']

    if selectedValue == "hurricanes":
        print('selectedvalue =', file=sys.stdout)
        print(selectedValue)
        html = file_html(getMap(), CDN, "my plot")
        return render_template('index.html', plot=html)       
    else:
        print("fires\n")              
        return render_template("index.html")


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
