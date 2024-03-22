# Libraries
import sys; sys.path.append('./pylsl')
from pylsl import StreamInlet, resolve_bypred, StreamInfo, StreamOutlet
import time
import serial

# set Arduino COM
if len(sys.argv) > 1:
    ArduinoCOM = sys.argv[1]
else:
    ArduinoCOM = 'COM3'

# // --- Connect through serial protocol to Arduino --- //
arduinoCOM = False 		#Conditional for Arduino connection.
while (not arduinoCOM): 	#Repeat until successful connection 
    try:			#Try if len(ArduinoCOM == 0), then connection was successful
        print("Attempting connection to Arduino.") 
        arduino=serial.Serial(ArduinoCOM,baudrate=500000)	#Create Arduino instance.
        arduino.close() 
        print("Connection successful.")
        arduinoCOM = True					#Change status

    except Exception as e:	#if failed to connect, try connecting again.
        print("Attempting again in 2s")
        time.sleep(2) 

# // --- Open serial communication through serial protocol to Arduino --- // 
try:
    arduino.open()
    print("Arduino communication port opened.")
except Exception as e:
    print(e)
    print("Could not open port or already in use.")

time.sleep(3)
arduino.write(str(b'33083').encode('utf-8'))			#Ping label to Arduino

# // --- Lookup for OpenVibe Marker data Stream --- //
print("Looking for OpenVibe Marker Stream ...")
streams = resolve_bypred('name', 'openvibeMarkers',timeout=1,)

# Pull samples and forward to Arduino 
while(len(streams) == 0):	#stay in loop if connection with OpenVibe fails
    print("OpenVibe Connection failed. Attempting again ...")
    time.sleep(2)  
    streams = resolve_bypred('name', 'openvibeMarkers',timeout=1)
    
print("OpenVibe Connection Stablished :D")
inlet = StreamInlet(streams[0])

# Receive labels from OpenVibe and forward them to Arduino
while True:
    try:
        marker, timestamp = inlet.pull_sample()
        if marker!=0:	#if a label exists, then send characters to Arduino
            for i in range(1):
                data = str(marker[0]).encode('utf-8')
                bytest = arduino.write(str(marker[0]).encode('utf-8'))
            print(marker[0], "at t = ", timestamp)
            print("Sent ", data, "; Marker is ", data)
            time.sleep(0.01)

        if marker[0] == 32770:	#if label is 32770, then close the program
            print('Program finished. Closing Arduino port')
            try:
                arduino.close()
                exit()
            except:
                print("Port closed already") 
                exit()
                break
    except Exception as e: 
        print(e)