import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)



@app.route('/', methods=['GET'])
def index():
       phoneNumber= request.args.get('phoneNumber')
       message=request.args.get('message')
       print(phoneNumber + " "+ message)
	
    




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
