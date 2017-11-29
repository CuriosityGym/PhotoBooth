import os
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)



@app.route('/', methods=['GET'])
def index():
	return "a"
    




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
