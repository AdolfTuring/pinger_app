import os
import sys
import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from ping3 import ping
import pygame
import time

pygame.mixer.init()
sound = pygame.mixer.Sound('alert.mp3')

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class PingerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pinger App")

        # Host input
        self.host_label = tk.Label(root, text="Host:")
        self.host_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.host_entry = tk.Entry(root)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Timeout selection
        self.timeout_label = tk.Label(root, text="Ping timeout (sec.):")
        self.timeout_label.grid(row=0, column=2, padx=5, pady=5, sticky='e')

        self.timeout_var = tk.IntVar(value=15)
        self.timeout_menu = tk.OptionMenu(root, self.timeout_var, 1, 5, 15, 30, 60)
        self.timeout_menu.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Alert time selection
        self.alert_label = tk.Label(root, text="Alert Time (sec.):")
        self.alert_label.grid(row=0, column=4, padx=5, pady=5, sticky='e')

        self.alert_var = tk.IntVar(value=60)
        self.alert_menu = tk.OptionMenu(root, self.alert_var, 30, 60, 90, 120)
        self.alert_menu.grid(row=0, column=5, padx=5, pady=5, sticky='w')

        # Result display
        self.result_label = tk.Label(root, text="Please enter the IP and select suitable for you values to Ping!", fg="blue")
        self.result_label.grid(row=1, column=0, columnspan=6, padx=5, pady=5)

        # Start and Stop buttons
        self.start_button = tk.Button(root, text="Start Pinging", command=self.start_pinging)
        self.start_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.stop_button = tk.Button(root, text="Stop Pinging", command=self.stop_pinging, state=tk.DISABLED)
        self.stop_button.grid(row=2, column=3, columnspan=3, padx=5, pady=5)

        self.stop_event = Event()
        self.ping_thread = None

    def start_pinging(self):
        host = self.host_entry.get().strip()
        if not host:
            messagebox.showwarning("Input Error", "Please enter a host.")
            return

        self.result_label.config(text="")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.stop_event.clear()
        self.ping_thread = Thread(target=self.ping_host, args=(host, self.timeout_var.get(), self.alert_var.get()))
        self.ping_thread.start()

    def ping_host(self, host, timeout, alert_time):
        while not self.stop_event.is_set():
            root.configure(bg='green')
            response = ping(host)
            
            if response is None:
                root.configure(bg='red')
                result_text = f"{host} is unreachable. Waiting {alert_time}/sec."
                self.update_result(result_text)
                res1=0
                #Check if network will be available durring Alert time
                for i in range(3):
                    if self.stop_event.is_set():
                        break
                    response = ping(host)
                    if response is None:
                        res1 += 1
                    else:
                        break
                    if res1==3:
                        # Play the sound
                        sound.play()
                        time.sleep(15)
                        # Stop the sound
                        sound.stop()
                    time.sleep(alert_time/3)
                
            else:
                result_text = f"{host} link established"
            
            self.update_result(result_text)
            if not self.stop_event.wait(timeout):
                continue
            

    def stop_pinging(self):
        sound.stop()
        self.stop_event.set()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_result("Pinging stopped.")

    def update_result(self, text):
        self.result_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PingerApp(root)
    root.mainloop()