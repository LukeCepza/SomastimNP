import tkinter as tk
import time

def change_text():
    button.config(text="Hello?")
    root.update()
    time.sleep(3)
    button.config(text="Bye", fg="red", bg ="blue")

root = tk.Tk()
root.title("Button Example")

button = tk.Button(root, text="Hello", command=change_text)
button.pack(padx=20, pady=20)

root.mainloop()