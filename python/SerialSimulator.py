import serial

# Replace 'COMx' with the name of your virtual serial port
serial_port = 'COM36'
baud_rate = 500000
try:
    ser = serial.Serial(port=serial_port, baudrate=baud_rate)

    while True:
        char = input("Enter a character (or 'q' to quit): ")
        if char.lower() == 'q':
            break  # Exit the loop if 'q' is entered
        ser.write(char.encode())  # Send the character as bytes

    ser.close()  # Close the serial port when you're done

except serial.serialutil.SerialException:
    print(f"Failed to open serial port '{serial_port}'")
except KeyboardInterrupt:
    print("Program terminated by the user.")