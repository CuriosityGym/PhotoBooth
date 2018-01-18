import serial
import time

portName='COM3'

byteArray=[53,13,10]

ser = serial.Serial(portName)
#ser.baudRate=115200
for byteval in byteArray:
    ser.write(byteval)
a=ser.read()
print(a)
ser.close()   
