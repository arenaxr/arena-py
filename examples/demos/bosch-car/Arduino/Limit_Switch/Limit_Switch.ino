// Declare the pins for the Button and the LED<br>int buttonPin = 12;
int LED = 13;
int buttonPin = 12;

void setup() {
   // Define pin #12 as input and activate the internal pull-up resistor
   pinMode(buttonPin, INPUT_PULLUP);
   // Define pin #13 as output, for the LED
   pinMode(LED, OUTPUT);
}

void loop(){
   // Read the value of the input. It can either be 1 or 0
   int buttonValue = digitalRead(buttonPin);
   if (buttonValue == LOW){
      // If button pushed, turn LED on
      digitalWrite(LED,HIGH);
   } else {
      // Otherwise, turn the LED off
      digitalWrite(LED, LOW);
   }
}