// This device is the caress node 
#include <SPI.h>
#include "printf.h"
#include "RF24.h"
#include <EEPROM.h> // Include the EEPROM library

RF24 radio(9, 10); // using pin 9 for the CE pin, and pin 10 for the CSN pin
uint8_t address[][6] = {"M2T", "M2A", "M2V"}; // RF pairs
uint8_t vel[4] = {60, 90, 120, 180}; //levels of intensity for the motors
int pos2final[3][4];
int pos1final[3][4];

int pos1[3];
int pos2[3];

byte payload = 0x00;
bool side = 1;
int delt = 5; //ms to wait

unsigned long Rx_data;
int t; 
int vel_idx; 

uint8_t pipe;
uint8_t bytes;

int loc;

int eepromAddress;
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
    Dynamixel.setMode(SERVO_01, SERVO, CW_LIMIT_ANGLE, CCW_LIMIT_ANGLE);delay(5); 
    Dynamixel.setMaxTorque(SERVO_01,0x2FF);
    Dynamixel.setMaxTorque(SERVO_02,0x2FF); 

    // Servos calculate final position for each velocity and location.
    CalculateFinalPositions();
} 
//**************************END SETUP*******************************//

//**************************** LOOP *********************************//
void loop()
{
  if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
    bytes = radio.getPayloadSize(); // get the size of the payload
    radio.read(&Rx_data, bytes);            // fetch payload from FIFO
    if (Rx_data != 999999)
    {
    readStimuli(Rx_data);
    }
  }
} //**************************** END LOOP ***************************//

void readStimuli(long Rx_data) {
  
  t = Rx_data % 10000; // Extracts the last 4 digits (0200)
  Rx_data /= 10000; // Remove the last 4 digits
  vel_idx = Rx_data % 10; // Extracts the next digit (2)
  Rx_data /= 10; // Remove the extracted digit
  loc = Rx_data; // The remaining value is the first digit (1)

  if (vel_idx == 0) {  // If the intensity is 0, save the position
      SaveCurrentLocation(loc-1);
      return;
  } 
  else if (vel_idx == 9) { // If the intensity is 9, load the saved position
      Move2Location(loc - 1);
      return;
  }

  for (int rep = 0; rep <4 ; rep++){
      
      if (side) {
          mov_final(vel_idx-1, loc-1);
      } else {
          mov_init(vel_idx-1, loc-1);
      }

      side = !side;
      
      for (int t_c = 0; t_c < 200; t_c++) {
          if (radio.available(&pipe)) {             // is there a payload? get the pipe number that recieved it
            bytes = radio.getPayloadSize(); // get the size of the payload
            radio.read(&Rx_data, bytes);            // fetch payload from FIFO
            if (Rx_data = 999999) {
              OpenServosFull();
              break;
              }
          }
          delayMicroseconds(delt*990);
      }
  }
  OpenServosHalf();
}

void mov_final(int vel_idx, int loc){
    Dynamixel.servo(SERVO_01, pos1final[loc][vel_idx], vel[vel_idx]);delay(3); //move motors to initial position
    Dynamixel.servo(SERVO_02, pos2final[loc][vel_idx], vel[vel_idx]);delay(3);
}

void mov_init(int vel_idx, int loc){
    Dynamixel.servo(SERVO_01, pos1[loc], vel[vel_idx]);delay(3); //move motors to initial position
    Dynamixel.servo(SERVO_02, pos2[loc], vel[vel_idx]);delay(3);
}

void SaveCurrentLocation(int loc) {
    pos1[loc] = Dynamixel.readPosition(SERVO_01);
    pos2[loc] = Dynamixel.readPosition(SERVO_02);

    Serial.println("Saving Position: " + String(loc));
    Serial.println("pos1 = " + String(pos1[loc]));
    Serial.println("pos2 = " + String(pos2[loc]));

    int eepromAddress = loc * 4; // Each position will take 4 bytes (2 bytes for each servo position)

    // Save pos1 to EEPROM
    EEPROM.write(eepromAddress, (pos1[loc] >> 8) & 0xFF);
    EEPROM.write(eepromAddress + 1, pos1[loc] & 0xFF);

    // Save pos2 to EEPROM
    EEPROM.write(eepromAddress + 2, (pos2[loc] >> 8) & 0xFF);
    EEPROM.write(eepromAddress + 3, pos2[loc] & 0xFF);

    Serial.println("Position saved to EEPROM.");

    OpenServosHalf();
}

void CalculateFinalPositions() {
    int eepromAddress;
    for (int locIndex = 0; locIndex < 3; locIndex++) {
        eepromAddress = locIndex * 4; // Each position will take 4 bytes (2 bytes for each servo position)
        pos1[locIndex] = (EEPROM.read(eepromAddress) << 8) + EEPROM.read(eepromAddress + 1);
        pos2[locIndex] = (EEPROM.read(eepromAddress + 2) << 8) + EEPROM.read(eepromAddress + 3);
        for (int velIndex = 0; velIndex < 4; velIndex++) {
            pos1final[locIndex][velIndex] = pos1[locIndex] - vel[velIndex] * 1 * 2.27;
            pos2final[locIndex][velIndex] = pos2[locIndex] - vel[velIndex] * 1 * 2.27;
        }
    }
}

void Move2Location(int loc) {
    Serial.println("Loaded Position: " + String(loc));
    Serial.println("pos1 = " + String(pos1[loc]));
    Serial.println("pos2 = " + String(pos2[loc]));

    // Move the servos to the loaded positions
    Dynamixel.servo(SERVO_01, pos1[loc], 0x2FF);
    delay(3);
    Dynamixel.servo(SERVO_02, pos2[loc], 0x2FF);
    delay(3);
}

void OpenServosFull() {
    Serial.println("STOP");
    Dynamixel.servo(SERVO_01, 0, 0x2FF);delay(2); //move motors to initial position
    Dynamixel.servo(SERVO_02, 1023, 0x2FF);delay(2);  
}

void OpenServosHalf() {
    Serial.println("STOP");
    Dynamixel.servo(SERVO_01, 0, 0x2FF);delay(2); //move motors to initial position
    Dynamixel.servo(SERVO_02, 512, 0x2FF);delay(2);  
}


