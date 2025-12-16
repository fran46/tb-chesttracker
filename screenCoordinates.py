import subprocess
import time
import tkinter as tk
from tkinter import messagebox
import pyautogui

# ================================
# CONFIGURATION
# ================================

# Path to Chrome executable
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

# Game URL
GAME_URL = "https://totalbattle.com/en/"

# ================================
# FULLSCREEN TRANSPARENT OVERLAY
# ================================

# Create a fullscreen, semi-transparent window
root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-alpha", 0.3)  # Transparency level
root.configure(bg="black")

# Dictionary to store mouse coordinates
selection_coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}

# ================================
# BROWSER LAUNCH
# ================================

def open_chrome():
    """Open Chrome in incognito mode and load the game page."""
    print("🚀 Opening Chrome with Total Battle...")

    subprocess.Popen([
        CHROME_PATH,
        "--incognito",
        "--force-device-scale-factor=1",
        "--start-maximized",
        "--no-first-run",
        "--disable-restore-session-state",
        GAME_URL
    ])

# ================================
# MOUSE EVENTS
# ================================

def on_mouse_press(event):
    """Store the starting point of the mouse drag."""
    selection_coords["x1"], selection_coords["y1"] = event.x, event.y


def on_mouse_release(event):
    """Store the end point and calculate the selected region."""
    selection_coords["x2"], selection_coords["y2"] = event.x, event.y

    x = min(selection_coords["x1"], selection_coords["x2"])
    y = min(selection_coords["y1"], selection_coords["y2"])
    width = abs(selection_coords["x1"] - selection_coords["x2"])
    height = abs(selection_coords["y1"] - selection_coords["y2"])

    print(f"Selected region: (x={x}, y={y}, width={width}, height={height})")
    messagebox.showinfo(
        "Region captured",
        f"(x={x}, y={y}, width={width}, height={height})"
    )

    # The window remains open to allow multiple selections

# ================================
# EVENT BINDINGS
# ================================

root.bind("<ButtonPress-1>", on_mouse_press)
root.bind("<ButtonRelease-1>", on_mouse_release)

# ================================
# SCREEN INFO
# ================================

screen_width, screen_height = pyautogui.size()
print(f"Screen resolution: {screen_width}x{screen_height}")
print("👉 Drag the mouse to select a screen region...")

# Launch Chrome
open_chrome()

# Start the Tkinter event loop
root.mainloop()
