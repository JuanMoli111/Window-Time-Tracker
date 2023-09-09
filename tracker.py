
import psutil
import os
import time
import threading
import tkinter as tk
from pynput import keyboard

# Global variables for time tracking

app_sessions = {}   #Dictionary to store app sessions and their total time
current_app = ""
label = None        #Initialize the label

#Function to get the active window's title (on Windows)
def get_active_window_title_windows():
    import win32gui
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

# Function to get the active window's title (on macOS)
def get_active_window_title_macos():
    from AppKit import NSWorkspace
    active_app_name = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
    return active_app_name

# Function to track time spent on different apps/websites
def track_time(interval=5):
    global current_app

    while True:

        if os.name == "nt":  # Windows
            active_window_title = get_active_window_title_windows()
        else:
            active_window_title = get_active_window_title_macos()

        if active_window_title:

            current_app = active_window_title

            #Si la ventana no habia sido trackeada antes inicializarla en cero
            if current_app not in app_sessions:
                app_sessions[current_app] = 0
            
            app_sessions[current_app] += interval

        time.sleep(interval)

# Function to stop tracking and add the current app session to the list
def stop_tracking():
    global current_app
    if current_app:
        app_sessions[current_app] = app_sessions.get(current_app, 0) + 1
        current_app = ""

# Function to update the GUI with the app sessions and their total time
def update_gui():
    global label
    while True:
        display_text = "Time spent on different apps:\n"
        for app, total_time in app_sessions.items():
            display_text += f"{app}: {total_time} seconds\n"
        label.config(text=display_text)
        time.sleep(1)

# Function to display the GUI
def display_gui():
    global label

    root = tk.Tk()
    root.title("Time Tracker")

    label = tk.Label(root, text="")
    label.pack()

    threading.Thread(target=update_gui).start()

    root.mainloop()

if __name__ == "__main__":
    try:
        interval = 5  # Time tracking interval in seconds
        print("Tracking time (press Ctrl+C to stop tracking)...")

        # Start time tracking and GUI in separate threads
        tracking_thread = threading.Thread(target=track_time, args=(interval,))
        tracking_thread.daemon = True
        tracking_thread.start()

        gui_thread = threading.Thread(target=display_gui)
        gui_thread.daemon = True
        gui_thread.start()

        # Capture Ctrl+C to stop tracking and update the list
        def on_ctrl_c(key):
            stop_tracking()
            tracking_thread.join()
            gui_thread.join()
            display_gui()
            exit(0)

        with keyboard.Listener(on_press=on_ctrl_c) as listener:
            listener.join()

    except KeyboardInterrupt:
        pass
