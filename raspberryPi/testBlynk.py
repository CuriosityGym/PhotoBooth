import BlynkLib



BLYNK_AUTH = 'cdfcfc54ce1d4e7e8d208fda31a2661f'
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Register Virtual Pins
@blynk.VIRTUAL_WRITE(1)
def my_write_handler(value):
        print('Current V1 value: {}'.format(value))
        message=value.split(":")
        recipientNumber=message[0].strip()
        recipientOTP=message[1].strip()
        print(recipientOTP)
@blynk.VIRTUAL_WRITE(2)
def config(value):
        print(value)
if __name__ == '__main__':
	blynk.run()
