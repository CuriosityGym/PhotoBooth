#include <LedMatrixSPI.h>
const byte NUM_ROWS = 2;
const byte NUM_COLS = 5;
#define NEW_CODE '0'
#define CODE_RECIEVED '1'
#define READY '2'
#define COUNT_DOWN '3'
#define FLASH '4'
#define UPLOADING '5'
#define DONE '6'

LedMatrixSPI lm = LedMatrixSPI(NUM_ROWS, NUM_COLS);
String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete
void setup() {

  lm.scrollDelay(20);      // Sets the delay for scrolling text. 0 = fastest
  lm.setIntensity(1);     // Sets the LED intensity. Default is 1.
  lm.setFont(FONT8x8);    // Sets the char font. Either FONT8x8 (default) or FONT5x7.
  //lm.setFont(FONT8x8);
  Serial.begin(115200);
}
int code = 11123;
char codeValue[7];
char recievedCommand;
char readyText[6] = "Ready?" ;
char countDownText[7] = "In     " ;
int val = 0;
char arrowHeads[] = {30, 32, 30, 32, 30, 32, 32};
void loop() {

  if (stringComplete) {
    //Serial.println();
    recievedCommand = inputString[0];
    switch (recievedCommand)
    {
      case NEW_CODE:
        lm.clearScreen();
        Serial.println("New Code");
        codeValue[0] = inputString[2];
        codeValue[1] = inputString[3];
        codeValue[2] = inputString[4];
        codeValue[3] = inputString[5];
        codeValue[4] = inputString[6];
        showText(codeValue, FONT8x8);
        break;

      case CODE_RECIEVED:
        Serial.println("CODE_RECIEVED");
        eraseDisplay();
        break;

      case READY:
        Serial.println("READY");
        showText(readyText, FONT5x7);
        break;

      case COUNT_DOWN:
        Serial.println("COUNT_DOWN");
        countDownText[3] = inputString[2];
        lm.clearScreen();
        showText(countDownText, FONT5x7);
        break;

      case FLASH:
        showText("Smile", FONT5x7);
        delay(1000);
        lm.clearScreen();
        triggerFlash();
        break;

      case UPLOADING:
        Serial.println("UPLOADING");
        lm.clearScreen();
        startUploadAnimation(arrowHeads, FONT8x8);
        break;
      case DONE:
        Serial.println("DONE");
        lm.clearScreen();
        showMultiLine("Done","Thanks!");
        break;  


    }
    inputString = "";
    stringComplete = false;
  }
  //val=val+1;

  //showText(arrowHeads,FONT8x8);
  //delay(100);




}

void triggerFlash()
{

}

void startUploadAnimation(char displayText[], int fontSize)
{
  int arrayElements = strlen(displayText);
  Serial.println(displayText);
  byte multiplier = 8;
  byte shiftRight = 0;
  lm.setFont(FONT8x8);
  if (fontSize == FONT5x7)
  {
    lm.setFont(FONT5x7);
    multiplier = 6;
    shiftRight = 1;
  }
  for (int j = 15; j > -6; j--)
  {
    for (int i = 0; i < arrayElements; i++)
    {

      lm.printChar(displayText[i], (i * multiplier) + shiftRight, j);
    }
    lm.update();
    delay(50);

  }
  //lm.update();
}


void showText(char displayText[], int fontSize)
{
  int arrayElements = strlen(displayText);
  Serial.println(displayText);
  byte multiplier = 8;
  byte shiftRight = 0;
  lm.setFont(FONT8x8);
  if (fontSize == FONT5x7)
  {
    lm.setFont(FONT5x7);
    multiplier = 6;
    shiftRight = 1;
  }
  for (int i = 0; i < arrayElements; i++)
  {

    lm.printChar(displayText[i], (i * multiplier) + shiftRight, 4);

  }
  lm.update();
}

void eraseDisplay()
{
  int rowsCount = NUM_ROWS << 3;
  int columnsCount = NUM_COLS << 3;
  for (int i = 0; i < columnsCount; i++)
  {
    for (int j = 0; j < rowsCount; j++)
    {
      lm.setLed(i, j, false);
      lm.update();
      delay(1);
    }
  }
}

void showMultiLine(char topLineText[], char bottomLine[])
{
  int arrayElementsTop = strlen(topLineText);
  int arrayElementsBottom = strlen(bottomLine);
  //Serial.println(displayText);
  
    lm.setFont(FONT5x7);
    byte multiplier = 6;
    byte shiftRight = 1;
  
  for (int i = 0; i < arrayElementsTop; i++)
  {

    lm.printChar(topLineText[i], (i * multiplier) + shiftRight, 1);

  }
  lm.update();
  delay(1000);
  for (int i = 0; i < arrayElementsBottom; i++)
  {

    lm.printChar(bottomLine[i], (i * multiplier) + shiftRight, 9);

  }
  lm.update();
  
}




void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}



