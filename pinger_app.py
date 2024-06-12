import os
import sys
import tkinter as tk
from tkinter import messagebox
from threading import Thread, Event
from ping3 import ping
#from playsound import playsound
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

        self.host_label = tk.Label(root, text="Host:")
        self.host_label.pack(pady=5)

        self.host_entry = tk.Entry(root)
        self.host_entry.pack(pady=5)

        self.result_label = tk.Label(root, text="", fg="blue")
        self.result_label.pack(pady=5)

        self.start_button = tk.Button(root, text="Start Pinging", command=self.start_pinging)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Stop Pinging", command=self.stop_pinging, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

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
        self.ping_thread = Thread(target=self.ping_host, args=(host,))
        self.ping_thread.start()

    def ping_host(self, host):
        while not self.stop_event.is_set():
            root.configure(bg='green')
            response = ping(host, timeout=15)  # Ping with a timeout of 15 seconds
            #print(response) 
            #program will wait 4 pings(60 sec) to check if link will be renewed in other case play sound   
            if response is None:
                j=0
                for i in range(4):
                    result_text = f"{host} is unreachable"
                    root.configure(bg='red')
                    response = ping(host, timeout=15)  # Ping with a timeout of 15 seconds
                    #print(time.time())
                    if response is not None:
                        break
                    if response is None:
                        j=j+1
                    if j==4:
                        # Play the sound
                        sound.play()
                        time.sleep(15)
                        # Stop the sound
                        sound.stop()
                        #print('sound')                
            else:
                result_text = f"{host} link established"

            self.update_result(result_text)
            self.stop_event.wait(1)  # wait for 1 second before the next ping

    def stop_pinging(self):
        sound.stop()
        self.stop_event.set()
        #if self.ping_thread is not None:
        #    self.ping_thread.join()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_result("Pinging stopped.")

    def update_result(self, text):
        self.result_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = PingerApp(root)
    root.mainloop()