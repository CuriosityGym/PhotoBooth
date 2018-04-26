import picamera

      
filename="1.jpg"
camera = picamera.PiCamera()
camera.brightness = cameraBrightness
camera.contrast = cameraContrast                
camera.awb_mode = 'sunlight'
camera.capture(filename)
camera.close()

