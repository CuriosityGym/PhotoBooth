import os
from flask import Flask, render_template, request, redirect, session
import paho.mqtt.client as mqtt
mqttConnected=False
publishingTotopicName="/CG/photobooth"
app = Flask(__name__)


def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	#mqttConnected=True
@app.route('/', methods=['GET'])
def index():
        phoneNumber= request.args.get('phoneNumber')
        message=request.args.get('message')
        client = mqtt.Client()
        client.on_connect = on_connect	
        client.connect("iot.eclipse.org", 1883, 60)
        client.loop_start()
        client.publish(publishingTotopicName, message)        
        client.loop_stop()
        return "OK"
	
    




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
