
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal_I2C lcd(0x27,16,2); // set the LCD address to 0x27 for a 16 chars and 2 line display

//Photo Resistors (PR)
#define HOOD_PR_PIN A1
#define ENGINE_PR_PIN A0
#define WHEEL_PR_L_PIN A3
#define WHEEL_PR_R_PIN A2
//Limit Switches (LS)
#define HEADLIGHT_LS_L_PIN 11
#define HEADLIGHT_LS_R_PIN 12

void setup() {
  //Prepare I2C LCD
  lcd.init();
  lcd.backlight();

  //Prepare pins
  pinMode(HOOD_PR_PIN, INPUT);
  pinMode(ENGINE_PR_PIN, INPUT);
  pinMode(WHEEL_PR_L_PIN, INPUT);
  pinMode(WHEEL_PR_R_PIN, INPUT);
  pinMode(HEADLIGHT_LS_L_PIN, INPUT_PULLUP);
  pinMode(HEADLIGHT_LS_R_PIN, INPUT_PULLUP);
  
  //Enable the serial comunication
  Serial.begin(115200); 
  Serial.setTimeout(1);
}

//Helper Function to Print to LCD and Serial
void printSerialLCD(String label, int value, int x, int y) {
  lcd.setCursor(x, y);
  lcd.print(label);
  lcd.setCursor(x+3, y);
  lcd.print(value);
  Serial.print(value);
}

void loop() {
  //Get Data from Input Pins
  int a = digitalRead(HOOD_PR_PIN);
  int b = digitalRead(ENGINE_PR_PIN);
  int c = digitalRead(WHEEL_PR_L_PIN);
  int d = digitalRead(WHEEL_PR_R_PIN);
  int e = 1-digitalRead(HEADLIGHT_LS_L_PIN);
  int f = 1-digitalRead(HEADLIGHT_LS_R_PIN);

  //Display values to I2C LCD 
  printSerialLCD("HO=",a,0,0);
  printSerialLCD("EN=",b,0,1);
  printSerialLCD("WL=",c,6,0);
  printSerialLCD("WR=",d,6,1);
  printSerialLCD("HL=",e,12,0);
  printSerialLCD("HR=",f,12,1);

  //Serial Print New line
  Serial.println();

  //Short delay
  delay(15);
}
