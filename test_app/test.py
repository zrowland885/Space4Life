from flask import Flask, render_template
import sys


app = Flask(__name__)

@app.route('/')
def index():
    print('Before render_template', file=sys.stdout)
    return render_template("index.html")
    

@app.route('/', methods=['POST','GET'])
def msg_management():
    print('in post', file=sys.stdout)
    selectedValue = request.form['options']
    print('selectedvalue =', file=sys.stdout)
    print(selectedValue)
    
 
    
if __name__ == '__main__':
  # Threaded option to enable multiple instances for multiple user access support
  app.run(threaded=True, port=5000)