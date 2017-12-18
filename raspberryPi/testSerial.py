import serial
import time
byteAr=[48, 58, 49, 50, 51, 52, 53,124]
numIn='0:12345'
valueList=bytearray(byteAr)
ser=serial.Serial('/dev/ttyUSB0', 115200,bytesize=8, parity='N', stopbits=1)
print("Sleeping")
time.sleep(5)
print("Waking")
ser.write(valueList)
#ser.write('\r')
#ser.write('\n')
print("Readings")
time.sleep(1)
a=ser.readline()
print(a)
print("Hello")
ser.close()
