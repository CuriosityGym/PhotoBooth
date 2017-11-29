import re
keyCode="TakePhoto"
OTPNumbers="6"
myString=""

regularExpression="^"+keyCode+"\s[0-9]{"+OTPNumbers+"}$"
#print(regularExpression)
a=re.match(regularExpression, "TakePhoto 123456")
print(a[0])
