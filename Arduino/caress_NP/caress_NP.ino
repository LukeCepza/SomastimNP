// This device is the caress node 
#include <SPI.h>
#include "printf.h"
#include "RF24.h"
RF24 radio(9, 10); // using pin 9 for the CE pin, and pin 10 for the CSN pin
uint8_t address[][6] = {"M2T", "M2A", "M2V"}; // RF pairs
uint8_t vel[4] = {60, 90, 120, 180}; //levels of intensity for the motors

int pos1 , pos2;
byte payload = 0x00;
byte pos = 0;
bool side = 1;

unsigned long Rx_data;

//-----------------Servos-----------------//
//Libraries used: https://github.com/zcshiner/Dynamixel_Serial/blob/master/Dynamixel%20Institution%20V2.pdf
#include <Dynamixel_Serial.h>     // Library needed to control Dynamixal servo
#define SERVO_01 0x01             // ID of which we will set Dynamixel too
#define SERVO_02 0x02             // ID of which we will set Dynamixel too
#define SERVO_ControlPin 0x02     // Control pin of buffer chip, NOTE: this does not matter becasue we are not using a half to full contorl buffer.
#define SERVO_SET_Baudrate 500000 // Baud rate speed which the Dynamixel will be set too (57600)
#define CW_LIMIT_ANGLE 0x001      // lowest clockwise angle is 1, as when set to 0 it set servo to wheel mode
#define CCW_LIMIT_ANGLE 0x3FF     // Highest anit-clockwise angle is 0XFFF, as when set to 0 it set servo to wheel mode
//****************************SET UP******************************//
void setup()
{
    //------------------Radio ------------------//
    // initialize the transceiver on the SPI bus
    Serial.begin(SERVO_SET_Baudrate);
    while (!Serial)
    {
        // some boards need to wait to ensure access to serial over USB
    }
    if (!radio.begin())
    {
        Serial.println(F("radio hardware is not responding!!"));
        delay(200);
        while (1)
        {
        } // hold in infinite loop
    }
    radio.setPALevel(RF24_PA_LOW);         // RF24_PA_MAX is default.
    radio.setPayloadSize(sizeof(Rx_data)); // float datatype occupies 2 bytes
    radio.openReadingPipe(1, address[0]);  // pipe 1/6 - "M2T" - Master to Touch
    radio.startListening();                // put radio in RX mode

    //-----------------Servos-----------------//
    Dynamixel.begin(SERVO_SET_Baudrate);  // We now need to set Ardiuno to the new Baudrate speed
    Dynamixel.setDirectionPin(SERVO_ControlPin);
    Dynamixel.setStatusPaketReturnDelay(SERVO_01, 6);          // Set Return packet delay to 6 uSec
    Dynamixel.setStatusPaketReturnDelay(SERVO_02, 6);          // Set Return packet delay to 6 uSec
    Dynamixel.setMode(SERVO_02, SERVO, CW_LIMIT_ANGLE, CCW_LIMIT_ANGLE);delay(5);
    Dynamixel.setMode(SERVO_01, SERVO, CW_LIMIT_ANGLE, CCW_LIMIT_ANGLE);delay(5);// set mode to SERVO and set angle limits  
    Dynamixel.setMaxTorque(SERVO_01,0x2FF);
    Dynamixel.setMaxTorque(SERVO_02,0x2FF); 
    pos1 = Dynamixel.readPosition(SERVO_01);
    pos2 = Dynamixel.readPosition(SERVO_02);
    Serial.println("pos1 = " + String(pos1));
    Serial.println("pos2 = " + String(pos2));

} 
//**************************END SETUP*******************************//

//**************************** LOOP *********************************//
void loop()
{
  uint8_t pipe;

  if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
    uint8_t bytes = radio.getPayloadSize(); // get the size of the payload
    radio.read(&Rx_data, bytes);            // fetch payload from FIFO
    if (Rx_data != 999999)
    {
    readStimuli(Rx_data);
    }
  }
} //**************************** END LOOP ***************************//

void readStimuli(long Rx_data) {

    pos1 = Dynamixel.readPosition(SERVO_01);
    pos2 = Dynamixel.readPosition(SERVO_02);

    if(pos1 - pos2 > 640){
      Serial.println("Motor cannot make full stim");}
    
    if(1023-pos > pos2){
      side = !side;
      }
  
  int t = Rx_data % 10000; // Extracts the last 4 digits (0200)
  Rx_data /= 10000; // Remove the last 4 digits
  int n = Rx_data % 10; // Extracts the next digit (2)
  Rx_data /= 10; // Remove the extracted digit
  int pos = Rx_data; // The remaining value is the first digit (1)

  // Print the values of t, n, and pos
  Serial.println(Rx_data);
  Serial.print("  t: ");  t = t * 10;  Serial.print(t);
  Serial.print("  int: "); Serial.print(n);

  Serial.println("Pos abs = " + String(abs(pos1 - pos2)));

  unsigned long startMillis = millis();
  unsigned long currentMillis = millis();

  Serial.println(currentMillis - startMillis);

  Serial.println("Stimulating");
  int i = 0;
  while (currentMillis - startMillis <= t) {
    currentMillis = millis();
    if(currentMillis - startMillis - 1000*i > 1000) {
        i++;
        Serial.println("moving");
        if (side) {
            stim_r(vel[n-1], 1);
            side = !side;
        } else {
            stim_l(vel[n-1], 1);
            side = !side;}}  

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
  //stopStim();    
  }

void stim_r(int vel, int t){

  //Serial.println("pos2 = " + String(pos1 + vel * t * 2.27));
  //Serial.println("pos1 = " + String(pos2 + vel * t * 2.27));
    Dynamixel.servo(SERVO_01, (pos1 - vel * t * 2.27), vel);delay(3); //move motors to initial position
    Dynamixel.servo(SERVO_02, (pos2 - vel * t * 2.27), vel);delay(3);
}

void stim_l(int vel, int t){
    //Serial.println("pos2 = " + String(pos1));
    //Serial.println("pos1 = " + String(pos2));
    Dynamixel.servo(SERVO_01, pos1, vel);delay(3); //move motors to initial position
    Dynamixel.servo(SERVO_02, pos2, vel);delay(3);
}

void stopStim() {
    Serial.println("STOP");
    Dynamixel.servo(SERVO_01, 0, 0x900);delay(1); //move motors to initial position
    Dynamixel.servo(SERVO_02, 1023, 0x900);delay(1);  
}
