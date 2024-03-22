// This device is the air node 
#include <SPI.h>
#include "printf.h"
#include "RF24.h"
RF24 radio(9, 10); // using pin 9 for the CE pin, and pin 10 for the CSN pin
uint8_t address[][6] = {"M2T", "M2A", "M2V"};// Let these addresses be used for the pair
byte payload = 0x00;  

uint8_t fz[4] = {63,127,191,255};    //levels of intensity for the motors

int position_pin[3] = {5,3,6};

unsigned long Rx_data;


void setup() {
  pinMode(2, INPUT);     // set pin 2 as output (anological output)
  pinMode(3, OUTPUT);     // set pin 3 as output (anological output)
  pinMode(4, INPUT);     // set pin 4 as output (anological output)
  pinMode(5, OUTPUT);     // set pin 3 as output (anological output)
  pinMode(6, OUTPUT);     // set pin 3 as output (anological output)


  Serial.begin(500000);     // baudrate of 500000

  // --- From RF24 library example: GettingStarted --- //
  // configure RF
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
  radio.setPayloadSize(sizeof(Rx_data));  // float datatype occupies 2 bytes
  radio.openReadingPipe(1, address[1]);   // pipe 2 "M2A" - Master to Air
  radio.startListening();                 // put radio in RX mode
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


analogWrite(position_pin[(pos-1)],fz[(n-1)]);

unsigned long startMillis = millis();
unsigned long currentMillis = millis();
//
//  
//  Serial.println(currentMillis - startMillis);
  while (currentMillis - startMillis  <= t) {
    currentMillis = millis();
    delay(1);
    //Serial.println(currentMillis - startMillis);
    uint8_t pipe;
    if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
      uint8_t bytes = radio.getPayloadSize(); // get the size of the payload
      radio.read(&Rx_data, bytes);            // fetch payload from FIFO
      if (Rx_data = 999999) {
        Serial.println("StopLabel");
        stopStim();
        currentMillis = 9999;
      };
    }
  }
//delay(2000);
  Serial.println("Finished Stim");
  stopStim(); 
}

void stopStim() {
  Serial.println("STOP");
  digitalWrite (3, LOW);
  digitalWrite (5, LOW);
  digitalWrite (6, LOW);
}
