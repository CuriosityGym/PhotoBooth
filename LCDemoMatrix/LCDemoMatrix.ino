//We always have to include the library
#include "LedControl.h"

/*
 Now we need a LedControl to work with.
 ***** These pin numbers will probably not work with your hardware *****
 pin 12 is connected to the DataIn 
 pin 11 is connected to the CLK 
 pin 10 is connected to LOAD 
 We have only a single MAX72XX.
 */
LedControl lc=LedControl(12,11,10,6);

/* we always wait a bit between updates of the display */
unsigned long delaytime=100;

void setup() {
  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  lc.shutdown(0,false);
  lc.shutdown(1,false);
  lc.shutdown(2,false);
  lc.shutdown(3,false);
  lc.shutdown(4,false);
  lc.shutdown(5,false);
  /* Set the brightness to a medium values */
  lc.setIntensity(0,3);
  lc.setIntensity(1,3);
  lc.setIntensity(2,3);
  lc.setIntensity(3,3);
  lc.setIntensity(4,3);
  lc.setIntensity(5,3);
  /* and clear the display */
  lc.clearDisplay(0);
  lc.clearDisplay(1);
  lc.clearDisplay(2);
  lc.clearDisplay(3);
  lc.clearDisplay(4);
  lc.clearDisplay(5);
  //lc.setLed(0,2,7,true);
  //lc.setColumn(0,2,0x55);
}

/*
 This method will display the characters for the
 word "Arduino" one after the other on the matrix. 
 (you need at least 5x7 leds to see the whole chars)
 */

byte zero[16]={B00000000,
B00000000,
B00000000,
B00111110,
B01100001,
B01010001,
B01001001,
B01001001,
B01001001,
B01001001,
B01000101,
B01000011,
B00111110,
B00000000,
B00000000,
B00000000}; 




void loop() { 
 int i;
for(i=0;i<8;i++)
{
  lc.setRow(0,i,zero[i]);
  lc.setRow(1,i,zero[i]);
}

for(i=8;i<16;i++)
{
  lc.setRow(3,i-8,zero[i]);
  lc.setRow(4,i-8,zero[i]);
  
}
  
}
