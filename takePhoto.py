import picamera
camera = picamera.PiCamera()
camera.brightness = 70
camera.sharpness = 90
camera.contrast = 50
camera.saturation = 40
camera.exposure_mode = 'auto'
camera.meter_mode = 'average'
camera.awb_mode = 'incandescent'
camera.image_effect = 'none'
camera.capture('image.jpg')
