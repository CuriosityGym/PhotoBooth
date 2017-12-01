import os,re
from flask import Flask, render_template, request, redirect, session
import paho.mqtt.client as mqtt
mqttConnected=False
keyCode="cg"
OTPNumbers="6"
publishingTotopicName="/CG/photobooth"
app = Flask(__name__)

def on_publish(mqttc, obj, mid):
    print("Published")
    return

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	mqttConnected=True
	
@app.route('/', methods=['GET'])
def index():
        phoneNumber= request.args.get('phoneNumber')
        message=request.args.get('message')
        regularExpression="^"+keyCode+"\s[0-9]{"+OTPNumbers+"}$"
        matched=re.match(regularExpression, message.lower())
        if(matched):        
                responseToBooth="{number:"+phoneNumber+",message:"+matched[0]+"}"
                client = mqtt.Client()
                client.on_connect = on_connect
                client.on_publish = on_publish
                client.connect("iot.eclipse.org", 1883, 60)
                client.loop_start()
                client.publish(publishingTotopicName, responseToBooth)        
                client.loop_stop()
                return "ok"
        else:
                return "Not Ok"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
