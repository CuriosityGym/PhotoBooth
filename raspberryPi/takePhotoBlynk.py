#!/usr/bin/python
import BlynkLib
import json
import os, sys
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
from random import randint
import math

dirname, filename = os.path.split(os.path.abspath(__file__))
sys.stdout = open(os.path.join(dirname,'PhotoBooth.log'), 'w')
appJSONName=os.path.join(dirname,"app.json")
settingsFile=os.path.join(dirname,"settings.json")

with open(appJSONName) as data_file:    
    appData = json.load(data_file)
    

adminPhone=appData["adminPhone"]
adminShutdownCode=appData["adminCode"]
BLYNK_AUTH = appData["blynkToken"]
MAKER_CHANNEL_EVENT_NAME=appData["MAKER_CHANNEL_NAME"]

with open(settingsFile) as data_file:    
    appSettings = json.load(data_file)

cameraBrightness=int(appSettings["brightness"])
cameraContrast=int(appSettings["contrast"])
chunkSize=int(appSettings["chunkSize"])
portName='/dev/ttyUSB0'
baudRate=115200
SerialCommandSeperator=":"
SerialCommandEnd="-"
serialConn=serial.Serial(portName, baudRate,bytesize=8, parity='N', stopbits=1)
time.sleep(5) #sleep the Pi for a while, since the Connected Arduino Boots Up
#Random OTP Generator
numberofDigits=5
LowRange=math.pow(10,numberofDigits-1)
HighRange=math.pow(10,numberofDigits)-1

#Semaphores to Sequence the Process
OTPAccepted=False
OTPGenerated=False




blynk = BlynkLib.Blynk(BLYNK_AUTH)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = os.path.join(dirname,"client_secret.json")

# This access scope grants read-only access to the authenticated user's Drive
# account.
SCOPES = ['https://www.googleapis.com/auth/drive']
API_SERVICE_NAME = 'drive'
API_VERSION = 'v2'
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
        global cameraBrightness
        global cameraContrast
        try:
                camera = picamera.PiCamera()
                camera.brightness = cameraBrightness
                camera.contrast = cameraContrast                
                camera.awb_mode = 'auto'
                camera.capture(filename)
                print("Photo Saved: "+filename)    
                
        finally:
                camera.close()
        return filename




def get_authenticated_service():
    
    storage = Storage(os.path.join(dirname,'creds'))

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
        fileNameFullPath=os.path.join(dirname,fileName)
        print(fileNameFullPath)
        folder_id='1yDr8nyPS2EOUG0DVhcn6-fPqx_FLD-Gd'
        #file_metadata = {'name': fileName, 'parents': [{'id': folder_id}]}
        file_metadata = {'title': fileName,'mimeType': 'image/jpeg','parents': [{'id': folder_id}]}
        media = MediaFileUpload(fileNameFullPath, mimetype='image/jpeg',resumable=True,chunksize=chunkSize)
        request = service.files().insert(body=file_metadata,media_body=media).execute()
        print(request["id"])
        return request["id"]
        

def sendToIFTTT(senderPhoneNumber, GoogleDriveFileURL):
	MakerURL="https://maker.ifttt.com/trigger/"+MAKER_CHANNEL_EVENT_NAME+"/with/key/c1BVwMuv-fI8ryLpLIihJe?"
	MakerURL=MakerURL+"value1=+"+str(senderPhoneNumber)
	MakerURL=MakerURL+"&value2=Here is your Selfie. Download it from "+GoogleDriveFileURL
	print(MakerURL)
	r= requests.get(MakerURL)
	print(r)
		
def addWatermark(fileName):
        base_path = os.path.join(dirname,fileName)
        watermark_path = os.path.join(dirname,'watermark.png')
        print(base_path)
        print(watermark_path)
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
        base.save(os.path.join(dirname,fileName))
        
def sendSerialMessage(messageType, message):
        messageData=messageType+SerialCommandSeperator+message+SerialCommandEnd
        messageData=messageData.encode()
        print(messageData)
        global serialConn
        serialConn.write(messageData)

def deleteFile(fileName):
        os.remove(os.path.join(dirname,fileName))
        
def getOTP():
        return randint(LowRange, HighRange)
        
def setNextOTP():
        global OTPGenerated
        global currentRandomNumber
        print(OTPGenerated)
        if(not OTPGenerated):                
                currentRandomNumber=getOTP()
                print("OTP Generated is:" +str(currentRandomNumber))
                sendSerialMessage("0",str(currentRandomNumber))
                OTPGenerated=True

def shutdown():
    command = "/usr/bin/sudo /sbin/shutdown now"
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
        
        
# Register Virtual Pins
@blynk.VIRTUAL_WRITE(1)
def recieveSMSInformation(value):
        global OTPGenerated
        global currentRandomNumber
        print('Current V1 value: {}'.format(value))
        message=value.split(":")
        recipientNumber=message[0].strip()
        recipientNumber=recipientNumber[-10:] #remove all country codes and extra characters 
        recipientOTP=message[1].strip()
        print(currentRandomNumber)
        print(recipientOTP)
        print(OTPGenerated)
        if(recipientNumber==adminPhone and recipientOTP==adminShutdownCode): #verify if it is to shutdown the device
                print("Shutdown Recieved")
                shutdown()
                return
                
        if(OTPGenerated and str(recipientOTP)==str(currentRandomNumber)):
                print("OTP confirmed")
                try: #well, shit happens
                        OTPAccepted=True
                        sendSerialMessage("1","0")## OTP has been Confirmed
                        time.sleep(2)
                        sendSerialMessage("2","0") #Ready?
                        time.sleep(2)
                        for countDown in range(5,0,-1):
                                sendSerialMessage("3",str(countDown)) #start Countdown from 5 seconds
                                time.sleep(1)
                        sendSerialMessage("4","0")#Ask User to Smile
                        time.sleep(2)
                        fileName=clickPhoto(recipientOTP)                        
                        sendSerialMessage("5","0") #Show Please Wait.. Text
                        addWatermark(fileName)                        
                        service=get_authenticated_service()                        
                        fileID=uploadMedia(service,fileName)                        
                        deleteFile(fileName)                        
                        fileURL="https://drive.google.com/file/d/"+str(fileID)+"/view"
                        sendToIFTTT(recipientNumber,fileURL)                      
                        sendSerialMessage("6","0") #Process is Done
                        time.sleep(3)
                        OTPGenerated=False
                        OTPAccepted=False
                        setNextOTP()
                except Exception as e:
                        print(e)

                        
def saveSettings(settingsJSON):
        f = open(settingsFile, 'r+')       
        f.seek(0)
        f.write(settingsJSON)
        f.truncate()
        f.close()


# Register Virtual Pins
@blynk.VIRTUAL_WRITE(2)
def configSettings(value):
        print(value)
        global cameraBrightness
        global cameraContrast
        try:               
                cameraSettings=value.split(":")
                cameraBrightness=int(cameraSettings[0].strip())
                cameraContrast=int(cameraSettings[1].strip())
                settings={}
                settings["brightness"]=str(cameraBrightness)
                settings["contrast"]=str(cameraContrast)
                json_data = json.dumps(settings)
                saveSettings(json_data)
                fileName=str(cameraBrightness)+"-"+str(cameraContrast)
                fileName=clickPhoto(fileName)
                service=get_authenticated_service()                        
                fileID=uploadMedia(service,fileName)
                deleteFile(fileName)
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
        run=True
        while(run):
                if(not OTPGenerated):                
                        currentRandomNumber=getOTP()
                        print("OTP Generated is:" +str(currentRandomNumber))
                        sendSerialMessage("0",str(currentRandomNumber))
                        OTPGenerated=True
                blynk.run()

        
