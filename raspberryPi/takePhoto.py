import paho.mqtt.client as mqtt
import json
import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
import time
import picamera
mqttConnected=False
subscibingTopic="/CG/photobooth"
MAKER_CHANNEL_EVENT_NAME="UPLOAD_DONE"
# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v3'
with open(CLIENT_SECRETS_FILE) as data_file:
        data = json.loads(data_file.read())
        
CLIENT_ID = data["installed"]["client_id"]
CLIENT_SECRET = data["installed"]["client_secret"]

# Check https://developers.google.com/drive/scopes for all available scopes                                                               
OAUTH_SCOPE = SCOPES

# Redirect URI for installed apps                                                                                                         
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	global mqttConnected
	mqttConnected=True

       

def clickPhoto(OTP):
        filename=str(OTP)+".jpg"
        try:
                camera = picamera.PiCamera()
                
                camera.capture(filename)
                print("Photo Saved: "+filename)    
                
        finally:
                camera.close()
        return filename




def get_authenticated_service():
    
    storage = Storage('creds')

    # Attempt to load existing credentials.  Null is returned if it fails.
    credentials = storage.get()
    #print(credentials)
    # Only attempt to get new credentials if the load failed.
    if not credentials:
    # Run through the OAuth flow and retrieve credentials                                                                                 
        flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

        authorize_url = flow.step1_get_authorize_url()
        print ('Go to the following link in your browser: ' + authorize_url)
        code = input('Enter verification code: ').strip()

        credentials = flow.step2_exchange(code)
        storage.put(credentials)
    return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)



def uploadMedia(service, fileName):
    folder_id='1yDr8nyPS2EOUG0DVhcn6-fPqx_FLD-Gd'
    file_metadata = {'name': fileName, 'parents': [folder_id]}
    media = MediaFileUpload(fileName, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
    return file["id"]

def sendToIFTTT(senderPhoneNumber, GoogleDriveFileURL):
	MakerURL="https://maker.ifttt.com/trigger/"+MAKER_CHANNEL_EVENT_NAME+"/with/key/cuMqB78snUe89uLgRaCZkc?"
	MakerURL=MakerURL+"value1="+senderPhoneNumber
	MakerURL=MakerURL+"value2="+GoogleDriveFileURL
	print(MakerURL)
		

def on_message(client, userdata, message):
        try: #well, shit happens
                message=str(message.payload.decode("utf-8"))
                print(message)
                JSONObject=json.loads(message)
                #Sample Message is as {number:"9819057179",message:"123456"}
                recipientNumber=JSONObject["number"]
                recipientOTP=JSONObject["message"]
                fileName=clickPhoto(recipientOTP)
                service=get_authenticated_service()
                fileID=uploadMedia(service,fileName)
                fileURL="https://drive.google.com/file/d/"+fileID+"/view"
                sendToIFTTT(recipientNumber,fileURL)
        except Exception as e:
                print(e)
 

if __name__ == '__main__':
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message=on_message
        client.connect("iot.eclipse.org", 1883, 60)
        #while(not mqttConnected):
        #       print(mqttConnected)
        #       time.sleep(1)

        client.subscribe(subscibingTopic)
        run = True
        while run:
                client.loop() 
