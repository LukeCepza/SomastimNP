// LCD
#include <Wire.h>
#include "DFRobot_LCD.h"
DFRobot_LCD lcd(16, 2); //16 characters and 2 lines of show

// This device is a TX node aka the master
#include <SPI.h>
#include "printf.h"
#include "RF24.h"

//instance of radio
RF24 radio(9, 10); // Arduino pin 9 for the CE pin and pin 10 for the CSN pin
// Let these addresses be used for the pair

String Fmar = "0000000";
//unsigned uint32_t Fmar = 0;
unsigned long Tx_data;

uint8_t address[][6] = {"M2T", "M2A", "M2V"};

String Mods[3] = {"CAR", "AIR", "VIB"};

const int interruptPin = 2; // The pin that will trigger the interrupt

void setup() {
  // LCD
  lcd.init();
  // put your setup code here, to run once:
  Serial.begin(500000);
  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }
  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    lcd.setRGB(250, 0, 0);
    lcd.setCursor(0, 0);
    lcd.print("not responding! ");
    lcd.setCursor(0, 1);
    lcd.print("Radio hardware  ");
    delay(20);
    while (1) {} // hold in infinite loop
  }
  radio.setPALevel(RF24_PA_LOW);          // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(Tx_data));  // float datatype occupies 4 bytes
  radio.stopListening();        // put radio in TX mode



  pinMode(interruptPin, INPUT_PULLUP); // Set the interrupt pin as an input with a pull-up resistor
  attachInterrupt(digitalPinToInterrupt(interruptPin), stopStimuli, FALLING);
}


void loop() {
  // put your main code here, to run repeatedly:
  delay(1);
  SerialEvent();
  
}

void sendStimuli(unsigned long Tx_data){  
  
  unsigned long start_timer = micros();               // start the timer
  bool report = radio.write(&Tx_data, sizeof(Tx_data));  // transmit & save the report
  unsigned long end_timer = micros();                 // end the timer

//  if (Tx_data == 999999) {
//      Serial.println("STOP");
//      }
  delay(2);

  if (report) {
    delay(2);
    lcd.setRGB(0, 250, 0);
    lcd.setCursor(0, 1);
    lcd.print("   Successful   ");  } 
  else {
    // print if reception of label in sub- modules failed
    Serial.println(F("Transmission failed or timed out")); // payload was not delivered
    lcd.setRGB(250, 0, 0);
    lcd.setCursor(0, 1);
    lcd.print("     Failed     ");
  }
}

void SerialEvent() {
  // put your main code here, to run repeatedly:
  String Fmar = "";
  unsigned int Fmar_len = Fmar.length();     // previous length of the String

  while (Serial.available()) {
    delay(1);
    char markers = Serial.read(); 
    Fmar += markers;
  }
  Fmar_len = Fmar.length();     // previous length of the String
  if (Fmar != "") {
  }
  // Check if the string is long enough to split
  if (Fmar_len == 7) {
    Serial.println("DATA");
    String stim_mod = Fmar.substring(0, 1);   // Extract the first character
    Tx_data = Fmar.substring(1, 7).toInt();

    radio.openWritingPipe(address[stim_mod.toInt() - 1]); 
    sendStimuli(Tx_data);
    lcd.setRGB(0, 0, 100);
    lcd.setCursor(0, 0);
    String lcdMessage = Mods[stim_mod.toInt() - 1] +  " P" + Fmar.substring(1, 2) + " I" +Fmar.substring(2, 3)+ " "+Fmar.substring(3, 7) + "0ms";
    lcd.print(lcdMessage);
  }
  else if (Fmar.indexOf("33083") >= 0) {  
      Serial.print("Hi, its Arduino!");
      lcd.setRGB(0, 0, 100);
      lcd.setCursor(0, 0);
      lcd.print("Ping Received");
      lcd.setRGB(0, 250, 0);
      lcd.setCursor(0, 1);
      lcd.print("   Successful   ");
    }
  else if (Fmar.indexOf("999999") >= 0) {  
    sendStimuli(999999);
    }
}

void stopStimuli(){
Serial.println("STOP");
}
