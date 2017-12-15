import BlynkLib
import json
import os
import google.oauth2.credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
import time
import picamera
import requests
import serial
import PIL.Image
import PIL.ImageEnhance

portName='/dev/ttyUSB0'


BLYNK_AUTH = 'cdfcfc54ce1d4e7e8d208fda31a2661f'
blynk = BlynkLib.Blynk(BLYNK_AUTH)
MAKER_CHANNEL_EVENT_NAME="upload_done"
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

##def on_connect(client, userdata, flags, rc):
##	print("Connected with result code "+str(rc))
##	global mqttConnected
##	mqttConnected=True

       

def clickPhoto(OTP):
        filename=str(OTP)+".jpg"
        try:
                camera = picamera.PiCamera()
                camera.brightness = 70
                camera.contrast = 70
                camera.saturation = 0
                camera.awb_mode = 'incandescent'
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
	MakerURL=MakerURL+"value1="+str(senderPhoneNumber)
	MakerURL=MakerURL+"&value2=Here is your Selfie. Download it from "+GoogleDriveFileURL
	#print(MakerURL)
	r= requests.get(MakerURL)
	print(r)
		
def addWatermark(fileName):
        base_path = fileName
        watermark_path = 'watermark.png'
        base = PIL.Image.open(base_path)
        baseWidth, baseHeight=base.size
        watermark = PIL.Image.open(watermark_path)
        watermarkWidth, watermarkHeight=watermark.size
        watermark.putalpha(100)
        
        brightness = 1
        watermark = PIL.ImageEnhance.Brightness(watermark).enhance(brightness)

        # apply the watermark
        some_xy_offset = (baseWidth-watermarkWidth-10, baseHeight-watermarkHeight-10)
        # the mask uses the transparency of the watermark (if it exists)
        base.paste(watermark, some_xy_offset, mask=watermark)
        base.save(fileName)
        
def sendSerialMessage(messageType, message):
     return True

def deleteFile(fileName):
        os.remove(fileName)
        

# Register Virtual Pins
@blynk.VIRTUAL_WRITE(1)
def my_write_handler(value):
        print('Current V1 value: {}'.format(value))
        message=value.split(":")
        recipientNumber=message[0]
        recipientOTP=message[1]
        
        try: #well, shit happens               
                #Sample Message is as {number:"9819057179",message:"123456"}
                #recipientNumber=JSONObject["number"]
                #recipientOTP=JSONObject["message"]
                fileName=clickPhoto(recipientOTP)
                addWatermark(fileName)
                service=get_authenticated_service()
                fileID=uploadMedia(service,fileName)
                deleteFile(fileName)
                fileURL="https://drive.google.com/file/d/"+str(fileID)+"/view"
                sendToIFTTT(recipientNumber,fileURL)
        except Exception as e:
                print(e)
    
        
##def on_message(client, userdata, message):
##        try: #well, shit happens
##                message=str(message.payload.decode("utf-8"))
##                print(message)
##                JSONObject=json.loads(message)
##                #Sample Message is as {number:"9819057179",message:"123456"}
##                recipientNumber=JSONObject["number"]
##                recipientOTP=JSONObject["message"]
##                fileName=clickPhoto(recipientOTP)
##                addWatermark(fileName)
##                service=get_authenticated_service()
##                fileID=uploadMedia(service,fileName)
##                fileURL="https://drive.google.com/file/d/"+str(fileID)+"/view"
##                #sendToIFTTT(recipientNumber,fileURL)
##        except Exception as e:
##                print(e)
 

if __name__ == '__main__':
        blynk.run()

        
