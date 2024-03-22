import tkinter as tk
import subprocess
import serial
from pylsl import StreamOutlet, StreamInfo
# Define the function to execute a command
def execute_command(command):
    subprocess.run(command, shell=True)

# Define the function to send a message via serial
def stimulate(message):
    print(message)
    outlet.push_sample([message])
    #serial_port.write(str(message).encode('utf-8'))  # Encode the message as bytes and send

# Create a stream info with the desired parameters
stream_name = "MyMarkerS"
stream_type = "Markers"
num_channels = 1  # Number of marker channels
channel_format = "int32"  # Data format of the marker channels
stream_info = StreamInfo(stream_name, stream_type, num_channels, 0, channel_format)

# next make an outlet
outlet = StreamOutlet(stream_info)
print(outlet)
# Open the serial port
#serial_port = serial.Serial("COM3", baudrate=500000)  # Replace "COM1" with your port


# Create the main application window
root = tk.Tk()
root.title("Command Buttons")

# Create a list of button labls and commands
button_data = [
    # N       , TT      , O 
    # 1 AIr   , 100ms   , F1 V1
    # 2 Caress,  x      , F2 V2
    # 3 Vib   , TT      , F3 V3
    # --------
    # Air       | 1 , 2 , 3 , 4 | 5000
    # Vib       |               |
    # Caress    |               |
    #
    # 
    #
    ("Air 1", 33031), 
    ("Air 2", 33032),  
    ("Air 3", 33033),
    ("Air 4", 33034),

    ("Caress 1", "33031"),
    ("Caress 2", "33031"),  
    ("Caress 3", "33031"),
    ("Caress 4", "33031"),

    ("Vibration 1", "33031"),
    ("Vibration 2", "33031"),  
    ("Vibration 3", "33031"),
    ("Vibration 4", "33031"),
    # ... Add more buttons and commands here
]

# Create and place buttons in a grid
for row, (label, message) in enumerate(button_data):
    button = tk.Button(root, text=label, command=lambda msg=message: stimulate(msg))
    button.grid(row=row // 4, column=row % 4, padx=10, pady=10)

# Start the main event loop
root.mainloop()
