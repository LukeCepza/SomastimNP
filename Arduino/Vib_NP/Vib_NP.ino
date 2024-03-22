// This device is the vibration node
#include <SPI.h>
#include "printf.h"
#include "RF24.h"

RF24 radio(9, 10); // using pin 9 for the CE pin, and pin 10 for the CSN pin
uint8_t address[][6] = {"M2T", "M2A", "M2V"}; // Let these addresses be used for the pair

//////////// Haptic Drivers
#include <Sparkfun_DRV2605L.h> //SparkFun Haptic Motor Driver Library 
#include <Wire.h> //I2C library 
SFE_HMD_DRV2605L HMD; //Create haptic motor driver object
uint8_t rtpn[4] = {24, 32, 64, 128}; //levels of intensity for the motors

//String   = "0000000";

unsigned long Rx_data;
void setup() {
  Serial.begin(500000);

  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);

  HMD.begin();
  HMD.Mode(0x05);            // Internal trigger input mode -- Must use the GO() function to trigger playback.
  HMD.MotorSelect(0b00110110);     // 1: LRA Mode ; 011: 4x Braking factor; 01: Medium (default) loop gain ; 10 : 15x (default)
  HMD.Library(2);            // 1-5 & 7 for ERM motors, 6 for LRA motors
  delay(10);

  while (!Serial) {
    // some boards need to wait to ensure access to serial over USB
  }
  // initialize the transceiver on the SPI bus
  if (!radio.begin()) {
    Serial.println(F("radio hardware is not responding!!"));
    delay(200);
    while (1) {} // hold in infinite loop
  }
  radio.setPALevel(RF24_PA_LOW);          // RF24_PA_MAX is default.
  radio.setPayloadSize(sizeof(Rx_data));  // float datatype occupies 4 bytes
  radio.openReadingPipe(1, address[2]); // using pipe 1}
  radio.startListening(); // put radio in RX mode

}

void loop() {
  uint8_t pipe;

  if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
    uint8_t bytes = radio.getPayloadSize(); // get the size of the payload
    radio.read(&Rx_data, bytes);            // fetch payload from FIFO
    if (Rx_data != 999999)
    {
    readStimuli(Rx_data);
    }
  }
}

void readStimuli(long Rx_data) {
  int t = Rx_data % 10000; // Extracts the last 4 digits (0200)
  Rx_data /= 10000; // Remove the last 4 digits
  int n = Rx_data % 10; // Extracts the next digit (2)
  Rx_data /= 10; // Remove the extracted digit
  int pos = Rx_data; // The remaining value is the first digit (1)

  // Print the values of t, n, and pos
  Serial.println(Rx_data);
  Serial.print("  t: ");  t = t * 10;  Serial.print(t);
  Serial.print("  int: "); Serial.print(n);
  Serial.print("  pos: "); Serial.println(pos);

  digitalWrite(pos + 1, HIGH);
  HMD.RTP(100);
  delay(10);
  HMD.RTP(rtpn[(n-1)]);
  
  unsigned long startMillis = millis();
  unsigned long currentMillis = millis();
  
  Serial.println(currentMillis - startMillis);
  while (currentMillis - startMillis <= t) {
    currentMillis = millis();
    Serial.println(currentMillis - startMillis);
    uint8_t pipe;
    if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
      uint8_t bytes = radio.getPayloadSize(); // get the size of the payload
      radio.read(&Rx_data, bytes);            // fetch payload from FIFO
      if (Rx_data = 999999) {
        Serial.println("StopLabel");
        stopStim();
        currentMillis = 9999;
      }
    }
  
  }
  Serial.println("Finished Stim");
  stopStim();
}

void stopStim() {
  HMD.RTP(0x00);
  Serial.println("STOP");
  digitalWrite (2, LOW);
  digitalWrite (3, LOW);
  digitalWrite (4, LOW);
}
