import json
settingsFile="settings.json"

##with open(settingsFile) as data_file:    
##    cameraSettings = json.load(data_file)
##
##cameraBrightness=cameraSettings["brightness"]
##cameraContrast=cameraSettings["contrast"]
##
##print(cameraBrightness)
##print(cameraContrast)


        
settings={}
settings["brightness"]=str(69)
settings["contrast"]=str(72)
json_data = json.dumps(settings)
#print(json_data)
saveSettings(json_data)


