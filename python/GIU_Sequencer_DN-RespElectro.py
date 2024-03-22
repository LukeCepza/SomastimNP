import tkinter as tk
import threading
import time
from pylsl import StreamInfo, StreamOutlet
import serial
import sys

class InterfaceApp:
    def __init__(self, root,serial_port):
        self.root = root
        self.root.title("Task Interface")
        self.root.geometry("400x300")
        self.root.configure(bg="#f0f0f0")
        self.rest = 3 # def 25
        self.airstim = 1 # def 12
        self.vibstim = 1 # def 3
        self.carstim = 1 # def 6
        self.task_list = [
            ("Air 1 P1", self.airstim, self.rest, "33738"),
            ("Air 1 P2", self.airstim, self.rest, "33738"),
            ("Air 1 P3", self.airstim, self.rest, "33738"),
            ("Air 2 P1", self.airstim, self.rest, "33739"),
            ("Air 2 P2", self.airstim, self.rest, "33739"),
            ("Air 2 P3", self.airstim, self.rest, "33739"),
            ("Air 3 P1", self.airstim, self.rest, "33740"),
            ("Air 3 P2", self.airstim, self.rest, "33740"),
            ("Air 3 P3", self.airstim, self.rest, "33740"),
            ("Air 4 P1", self.airstim, self.rest, "33741"),
            ("Air 4 P2", self.airstim, self.rest, "33741"),
            ("Air 4 P3 & Long Rest", 3, 30, "33741"),            
            ("Vib 1 P1", self.vibstim, self.rest, "33732"),
            ("Vib 1 P2", self.vibstim, self.rest, "33732"),
            ("Vib 1 P3", self.vibstim, self.rest, "33732"),
            ("Vib 2 P1", self.vibstim, self.rest, "33733"),
            ("Vib 2 P2", self.vibstim, self.rest, "33733"),
            ("Vib 2 P3", self.vibstim, self.rest, "33733"),
            ("Vib 3 P1", self.vibstim, self.rest, "33734"),
            ("Vib 3 P2", self.vibstim, self.rest, "33734"),
            ("Vib 3 P3", self.vibstim, self.rest, "33734"),
            ("Vib 4 P1", self.vibstim, self.rest, "33735"),
            ("Vib 4 P2", self.vibstim, self.rest, "33735"),
            ("Vib 4 P3 & Long Rest", 3, 30, "33735"),  
            ("Car 1 P1", self.carstim , self.rest, "33731"),
            ("Car 1 P2", self.carstim , self.rest, "33731"),
            ("Car 1 P3", self.carstim , self.rest, "33731"),
            ("Car 2 P1", self.carstim , self.rest, "33732"),
            ("Car 2 P2", self.carstim , self.rest, "33732"),
            ("Car 2 P3", self.carstim , self.rest, "33732"),
            ("Car 3 P1", self.carstim , self.rest, "33733"),
            ("Car 3 P2", self.carstim , self.rest, "33733"),
            ("Car 3 P3", self.carstim , self.rest, "33733"),
            ("Car 4 P1", self.carstim , self.rest, "33734"),
            ("Car 4 P2", self.carstim , self.rest, "33734"),
            ("Car 4 P3 & Long Rest", 3, 30, "33734"),
            ("End", None, None, "33732"),
            ("None", None, None, None),
                            ]
        
        self.current_index = 0
        self.is_task_active = False
        self.auto_start = tk.IntVar()  # IntVar to store checkbox value
        self.timer = None
        
        self.current_task = tk.StringVar()
        self.next_task = tk.StringVar()
        self.previous_task = tk.StringVar()
        self.timer_label = tk.StringVar()
        
        self.current_label = tk.Label(root, textvariable=self.current_task, font=("Helvetica", 16), bg="#f0f0f0")
        self.next_label = tk.Label(root, textvariable=self.next_task, font=("Helvetica", 14), bg="#f0f0f0")
        self.previous_label = tk.Label(root, textvariable=self.previous_task, font=("Helvetica", 14), bg="#f0f0f0")
        self.timer_display = tk.Label(root, textvariable=self.timer_label, font=("Helvetica", 14), bg="#f0f0f0")
        
        self.auto_start_checkbox = tk.Checkbutton(root, text="Auto Start", variable=self.auto_start, command=self.auto_run, font=("Helvetica", 12))
        self.send_button = tk.Button(root, text="Start Task", command=self.start_task, font=("Helvetica", 12))
        
        # Create LSL outlet for markers
        self.create_lsl_outlet()
        
        self.connect_serial_port(serial_port)

        self.update_labels()
        
        self.previous_label.pack(pady=5)
        self.current_label.pack(pady=(20, 5))
        self.next_label.pack(pady=5)
        self.timer_display.pack(pady=10)
        self.send_button.pack(pady=(10, 20))
        self.auto_start_checkbox.pack(pady=5)

    def update_labels(self):
        self.current_task.set("Current Task: " + self.task_list[self.current_index][0])
        self.next_task.set("Next Task: " + self.task_list[(self.current_index + 1) % len(self.task_list)][0])
        self.previous_task.set("Previous Task: " + self.task_list[(self.current_index - 1) % len(self.task_list)][0])
        
    def auto_run(self):
        if self.auto_start.get() == 1:
            self.start_task()  # Automatically start if checkbox is checked
            self.root.after(1000, self.auto_run)  # Call auto_run after 1000 milliseconds (1 second)

    def start_task(self):
        if not self.is_task_active:
            self.is_task_active = True
            task_name, task_duration, rest_duration, marker_value = self.task_list[self.current_index]
            self.current_task.set("Current Task: " + task_name)
            self.send_button.config(state=tk.DISABLED)
            if marker_value:
                self.send_lsl_marker(marker_value)
                self.send_serial_command(marker_value)
            self.timer = threading.Thread(target=self.task_timer, args=(task_duration, rest_duration))
            self.timer.start()
        
    def task_timer(self, task_duration, rest_duration):
        while task_duration > 0:
            self.timer_label.set(f"Time left: {task_duration} s")
            self.root.update()
            time.sleep(1)
            task_duration -= 1
        
        if rest_duration is not None:
            for t in range(rest_duration, 0, -1):
                self.timer_label.set(f"Rest Time: {t} s")
                self.root.update()
                time.sleep(1)
            
        self.timer_label.set("")
        self.is_task_active = False
        self.send_button.config(state=tk.NORMAL)
        self.current_index = (self.current_index + 1) % len(self.task_list)
        self.update_labels()
        
    def create_lsl_outlet(self):
        self.stream_name = "MyMarkerS"
        self.stream_type = "Markers"
        self.num_channels = 1
        self.channel_format = "int32"
        self.stream_info = StreamInfo(self.stream_name, self.stream_type, self.num_channels, 0, self.channel_format)
        self.outlet = StreamOutlet(self.stream_info)
        
    def connect_serial_port(self,serial_port):
        self.serial_port = serial.Serial(serial_port, baudrate=500000)  # Replace "COM1" with your port
    def send_lsl_marker(self, marker_value):
        try:
            self.outlet.push_sample([int(marker_value)])
        except Exception as e:
            print("Error sending LSL marker:", e)
    def send_serial_command(self, marker_value):
        try:
            self.serial_port.write(str(marker_value).encode('utf-8'))
        except Exception as e:
            print("Error sending Serial marker:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        serial_port = sys.argv[1]  # Get serial port from command-line argument
        root = tk.Tk()
        app = InterfaceApp(root, serial_port)
        root.mainloop()
    else:
        print("Usage: python your_script.py serial_port")