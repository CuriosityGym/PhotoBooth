import serial
import time
byteAr=[50, 58, 49, 50, 51, 52, 53,45]

valueList=bytearray(byteAr)
ser=serial.Serial('COM3', 115200,bytesize=8, parity='N', stopbits=1)
print("Sleeping")
time.sleep(5)
print("Waking")
ser.write('2-'.encode())
#ser.write('\r')
#ser.write('\n')
#print("Readings")
time.sleep(10)
#a=ser.readline()
#print(a)
#print("Hello")
ser.close()
