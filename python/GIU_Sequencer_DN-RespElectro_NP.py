import tkinter as tk
import threading
import time
from pylsl import StreamInfo, StreamOutlet
import serial
import sys
from tkinter import messagebox


class InterfaceApp_NP:
    def __init__(self, root, serial_port, LSLMarkerStream):
        self.root = root
        self.root.title("NeuroPain Volunteer")
        self.root.geometry("512x400")
        self.root.configure(bg="#f0f0f0")
        root.protocol("WM_DELETE_WINDOW", lambda: self.on_closing("1997"))
        self.win_closed = "1997"

        # Labels and rest duration related variables       
        self.stop_tag = "99999"
        self.rest = 3
        self.airstim = 6
        self.vibstim = 3
        self.carstim = 4
        self.task_list = [[("Air 1 P1", self.airstim, self.rest, "2110600"),
                           ("Air 1 P2", self.airstim, self.rest, "2210600"),
                           ("Air 1 P3", self.airstim, self.rest, "2310600"),
                           ("Air 2 P1", self.airstim, self.rest, "2120600"),
                           ("Air 2 P2", self.airstim, self.rest, "2220600"),
                           ("Air 2 P3", self.airstim, self.rest, "2320600"),
                           ("Air 3 P1", self.airstim, self.rest, "2130600"),
                           ("Air 3 P2", self.airstim, self.rest, "2230600"),
                           ("Air 3 P3", self.airstim, self.rest, "2330600"),
                           ("Air 4 P1", self.airstim, self.rest, "2140600"),
                           ("Air 4 P2", self.airstim, self.rest, "2240600"),
                           ("Air 4 P3 & Long Rest", self.airstim, self.rest, "2340600")],
                          [("Vib 1 P1", self.vibstim, self.rest, "3110300"),
                           ("Vib 1 P2", self.vibstim, self.rest, "3210300"),
                           ("Vib 1 P3", self.vibstim, self.rest, "3310300"),
                           ("Vib 2 P1", self.vibstim, self.rest, "3120300"),
                           ("Vib 2 P2", self.vibstim, self.rest, "3220300"),
                           ("Vib 2 P3", self.vibstim, self.rest, "3320300"),
                           ("Vib 3 P1", self.vibstim, self.rest, "3130300"),
                           ("Vib 3 P2", self.vibstim, self.rest, "3230300"),
                           ("Vib 3 P3", self.vibstim, self.rest, "3330300"),
                           ("Vib 4 P1", self.vibstim, self.rest, "3140300"),
                           ("Vib 4 P2", self.vibstim, self.rest, "3240300"),
                           ("Vib 4 P3 & Long Rest", self.vibstim, self.rest, "3340300")],
                          [("Car 1 P1", self.carstim, self.rest, "1110400"),
                           ("Car 1 P2", self.carstim, self.rest, "1110400"),
                           ("Car 1 P3", self.carstim, self.rest, "1110400"),
                           ("Car 2 P1", self.carstim, self.rest, "1120400"),
                           ("Car 2 P2", self.carstim, self.rest, "1120400"),
                           ("Car 2 P3", self.carstim, self.rest, "1120400"),
                           ("Car 3 P1", self.carstim, self.rest, "1130400"),
                           ("Car 3 P2", self.carstim, self.rest, "1130400"),
                           ("Car 3 P3", self.carstim, self.rest, "1130400"),
                           ("Car 4 P1", self.carstim, self.rest, "1140400"),
                           ("Car 4 P2", self.carstim, self.rest, "1140400"),
                           ("Car 4 P3 & Long Rest", self.carstim, 30, "1140400")]]
        
        self.save_labels = [("Save P1", "1100000"), ("Save P2", "1200000"), ("Save P3", "1300000")]
        self.load_labels = [("Load P1", "1190000"), ("Load P2", "1290000"), ("Load P3", "1390000")]

        # States:
        self.tabs = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
                     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        
        self.mod_select = 0
        self.is_task_active = False
        self.stop = False

        # Titles of buttons of Mod
        tab_txt = ["Air", "Vib", "Car"]
        self.Mods_Buttons = [tk.Button(root, text=tab_txt[i], command=lambda mod=i: self.UpdateTab(mod), font=("Helvetica", 12)) for i in range(3)]
        self.Mods_Buttons[0].place(x=240, y=10)
        self.Mods_Buttons[1].place(x=320, y=10)
        self.Mods_Buttons[2].place(x=400, y=10)

        # Titles of buttons of Intensity
        text_order = ["1", "1", "1", "2", "2", "2", "3", "3", "3", "4", "4", "4"]
        self.IntMatrix = [tk.Button(root, text=text_order[i], command=lambda idx=i: self.UpdateGrid(idx), font=("Helvetica", 12)) for i in range(12)]
        
        y_pos = 20
        x_pos = 30
        y_dif = 40
        x_dif = 60
        for b in range(1, 5):
            for a in range(0, 3):
                self.IntMatrix[a + 3 * (b - 1)].place(x=x_pos + x_dif * a, y=y_pos + y_dif * b)

        # Buttons for save and load actions
        self.save_buttons = [tk.Button(root, text=self.save_labels[i][0], command=lambda lbl=self.save_labels[i][1]: self.send_serial_command(lbl), font=("Helvetica", 12)) for i in range(3)]
        self.load_buttons = [tk.Button(root, text=self.load_labels[i][0], command=lambda lbl=self.load_labels[i][1]: self.send_serial_command(lbl), font=("Helvetica", 12)) for i in range(3)]
        
        for i in range(3):
            self.save_buttons[i].place(x=300, y=80 + 40 * i)
            self.load_buttons[i].place(x=400, y=80 + 40 * i)

        # Initially hide the save and load buttons
        self.toggle_save_load_buttons(False)

        # Auto Run
        self.auto_start = tk.IntVar()  # IntVar to store checkbox value
        self.auto_start_checkbox = tk.Checkbutton(root, text="Auto Start", variable=self.auto_start, command=self.auto_run, font=("Helvetica", 12))
        self.auto_start_checkbox.place(x=30, y=300)

        # Timer label
        self.timer_label = tk.StringVar()
        self.timer_display = tk.Label(root, textvariable=self.timer_label, font=("Helvetica", 14), bg="#f0f0f0")
        self.timer_display.place(x=250, y=300)
       
        self.current_task = tk.StringVar()
        self.current_task_display = tk.Label(root, textvariable=self.current_task, font=("Helvetica", 14), bg="#f0f0f0")
        self.current_task_display.place(x=250, y=250)
       
        # Initialize conditions
        self.Mods_Buttons[self.mod_select].config(bg="green")
        self.create_lsl_outlet(LSLMarkerStream)
        self.connect_serial_port(serial_port)
        self.readp = threading.Thread(target=self.read_serial_port)
        self.readp.start()
        self.UpdateTab(0)

    def UpdateTab(self, mod):
        self.mod_select = mod
        for m in range(0, 3):
            self.Mods_Buttons[m].config(bg="white")
        self.Mods_Buttons[self.mod_select].config(bg="green")
        for a in range(0, 12):
            if self.tabs[self.mod_select][a] == -1:
                self.IntMatrix[a].config(bg="green")
                self.IntMatrix[a]["state"] = "disabled"
            elif self.tabs[self.mod_select][a] > 0:
                self.IntMatrix[a].config(bg="red")
                self.IntMatrix[a]["state"] = tk.NORMAL
            else:
                self.IntMatrix[a].config(bg="white")
                self.IntMatrix[a]["state"] = tk.NORMAL
        
        # Show or hide save/load buttons based on the selected mod
        self.toggle_save_load_buttons(self.mod_select == 2)

    def UpdateGrid(self, idx):
        if self.tabs[self.mod_select][idx] != -1:
            self.stimulating_button(idx)

    def toggle_save_load_buttons(self, show):
        state = "normal" if show else "hidden"
        for i in range(3):
            if state == "hidden":
                self.save_buttons[i].place_forget()
                self.load_buttons[i].place_forget()
            else:
                self.save_buttons[i].place(x=300, y=80 + 40 * i)
                self.load_buttons[i].place(x=400, y=80 + 40 * i)
            self.save_buttons[i].update()
            self.load_buttons[i].update()

    def disable_notone(self):
        for a in range(0, 12):
            if self.tabs[self.mod_select][a] != -1:
                self.IntMatrix[a]["state"] = "disable"
        for mod in range(0, 3):
            self.Mods_Buttons[mod]["state"] = "disable"

    def enable_notone(self):
        for a in range(0, 12):
            if self.tabs[self.mod_select][a] != -1:
                self.IntMatrix[a]["state"] = tk.NORMAL
        for mod in range(0, 3):
            self.Mods_Buttons[mod]["state"] = tk.NORMAL

    def turn_green(self, idx):
        self.IntMatrix[idx].config(bg="green")
        self.IntMatrix[idx]["state"] = "disable"
        self.tabs[self.mod_select][idx] = -1
        self.root.update()
    
    def turn_red(self, idx):
        self.IntMatrix[idx].config(bg="red")
        self.IntMatrix[idx]["state"] = "disable"
        self.tabs[self.mod_select][idx] += 1
        self.root.update()

    def enable_red(self, idx):
        self.IntMatrix[idx].config(bg="red")
        self.IntMatrix[idx]["state"] = tk.NORMAL
        self.root.update()

    def stimulating_button(self, idx):
        self.IntMatrix[idx].config(bg="yellow")
        self.IntMatrix[idx]["state"] = "disable"
        self.root.update()
        self.start_task(idx)
        
    def start_task(self, idx):
        if not self.is_task_active:
            self.stop = False
            self.is_task_active = True
            task_name, task_duration, rest_duration, marker_value = self.task_list[self.mod_select][idx]
            self.current_task.set("Current Task: " + task_name)
            if marker_value:
                self.send_lsl_marker(marker_value)
                self.send_serial_command(marker_value)
                print("sending lsl and serial")
            self.disable_notone()
            self.timer = threading.Thread(target=self.task_timer, args=(idx, task_duration, rest_duration))
            self.timer.start()
        if not self.stop:
            self.IntMatrix[idx].config(bg="yellow")
            self.IntMatrix[idx]["state"] = "disable"
        
    def task_timer(self, idx, task_duration, rest_duration):
        while task_duration > 0:
            self.timer_label.set(f"Time left: {task_duration:.3f} s")
            self.root.update()
            time.sleep(0.025)
            task_duration -= 0.025
            if self.stop:
                task_duration = 0
        if not self.stop:
            self.turn_green(idx)
        else:
            self.turn_red(idx)
        self.current_task.set("Current Task: None")
        if rest_duration is not None:
            while rest_duration > 0:
                self.timer_label.set(f"Rest Time: {rest_duration:.3f} s")
                self.root.update()
                time.sleep(0.025)
                rest_duration -= 0.025
        self.enable_notone()
        self.timer_label.set("")
        self.is_task_active = False

    def stopped(But):
        But.config(fg="red")

    def auto_run(self):
        if self.auto_start.get() == 1 and self.mod_select != 2:
            idxes = self.tabs[self.mod_select]
            idx = next((i for i, num in enumerate(idxes) if num != -1), None)
            if idx is not None:
                self.root.after(1000, self.auto_run)  # Call auto_run after 1000 milliseconds (1 second)
                if not self.is_task_active:
                    self.stimulating_button(idx)  # Instead of start_task

    def create_lsl_outlet(self, LSLMarkerStream):
        self.stream_name = LSLMarkerStream
        self.stream_type = "Markers"
        self.num_channels = 1
        self.channel_format = "int32"
        self.stream_info = StreamInfo(self.stream_name, self.stream_type, self.num_channels, 0, self.channel_format)
        self.outlet = StreamOutlet(self.stream_info)

    def connect_serial_port(self, serial_port):
        self.serial_port = serial.Serial(serial_port, baudrate=500000)

    def send_lsl_marker(self, marker_value):
        try:
            self.outlet.push_sample([int(marker_value)])
        except Exception as e:
            print("Error sending LSL marker:", e)

    def read_serial_port(self):
        while True:
            while self.serial_port.in_waiting > 0:
                data = self.serial_port.readline().decode().strip()
                print(data)
                if data == "STOP" and self.is_task_active:
                    self.is_task_active = False
                    self.stop = True
                    self.send_serial_command("999999")
                    self.send_serial_command("999999")
                    self.send_serial_command("999999")
                    self.send_lsl_marker(self.stop_tag)
                    self.auto_start.set(0)

    def send_serial_command(self, marker_value):
        try:
            self.serial_port.write(str(marker_value).encode('utf-8'))
        except Exception as e:
            print("Error sending Serial marker:", e)

    def on_closing(self, win_closed):
        if messagebox.askokcancel("Confirm Close", "Do you want to finish the experiment"):
            self.send_lsl_marker(win_closed)
            print("Window is closing")
            self.serial_port.close()
            root.destroy()


if __name__ == "__main__":
    if len(sys.argv) > 2:
        serial_port = sys.argv[1]  # Get serial port from command-line argument
        LSLMarkerStream = sys.argv[2]
        root = tk.Tk()
        app = InterfaceApp_NP(root, serial_port, LSLMarkerStream)
        root.mainloop()
    else:
        print("Usage: python your_script.py serial_port")
