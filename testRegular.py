import re
keyCode="cg"
OTPNumbers="6"
myString="cg 345677"

regularExpression="^("+keyCode+")\s([0-9]{"+OTPNumbers+"})$"
#print(regularExpression)
a=re.findall(regularExpression, myString)
print(a[0][1])
