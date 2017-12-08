import os,re

from flask import Flask, render_template, request
from flask_uploads import UploadSet, configure_uploads, IMAGES
import paho.mqtt.client as mqtt
photos = UploadSet('photos', IMAGES)
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
        phoneNumber= request.args.get('phoneNumber').strip()
        message=request.args.get('message').strip().lower()
        regularExpression="^("+keyCode+")\s([0-9]{"+OTPNumbers+"})$"
        matched=re.findall(regularExpression, message.lower())
        #matched=matched.trim()
        if(matched):        
                responseToBooth='{"number":"'+phoneNumber+'","message":"' +matched[0][1]+'"}'
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
            
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])
        return filename
    return render_template('upload.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port,debug=True)
