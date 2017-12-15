import serial
import time

portName='/dev/ttyUSB0'



ser = serial.Serial(portName)
ser.baudRate=115200
ser.write(r'0:12345')     
ser.close()   
