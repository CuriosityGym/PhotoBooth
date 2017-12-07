import paho.mqtt.client as mqtt
import json
subscibingTopic="/CG/photobooth"

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	mqttConnected=True
def on_message(client, userdata, message):
    try: #well, shit happens
        message=str(message.payload.decode("utf-8"))
        print(message)
        JSONObject=json.loads(message)
        #Sample Message is as {number:"9819057179",message:"123456"}
        recipientNumber=JSONObject["number"]
        recipientOTP=JSONObject["message"]
    except Exception as e:
        print(e)
        
def uploadToDrive(filePath)




if __name__ == '__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message=on_message
    client.connect("iot.eclipse.org", 1883, 60)
    client.subscribe(subscibingTopic)
    client.loop_start() 
