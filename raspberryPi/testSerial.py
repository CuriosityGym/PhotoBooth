import serial
import time
byteAr=[50, 58, 49, 50, 51, 52, 53,45]
SerialCommandSeperator=":"
SerialCommandEnd="-"
def sendSerialMessage(messageType, message):
        messageData=messageType+SerialCommandSeperator+message+SerialCommandEnd
        messageData=messageData.encode()
        print(messageData)
        ser.write(messageData)

valueList=bytearray(byteAr)
ser=serial.Serial('COM3', 115200,bytesize=8, parity='N', stopbits=1)
print("Sleeping")
time.sleep(5)
print("Waking")
sendSerialMessage("0", str(12344))
#ser.write('\r')
#ser.write('\n')
#print("Readings")
time.sleep(2)
#a=ser.readline()
#print(a)
#print("Hello")
ser.close()
