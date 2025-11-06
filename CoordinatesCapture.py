import cv2 as cv
import numpy as np
import time
import tkinter as tk
import mss
from pynput import keyboard
from main import focuse_window
import win32api
import json

# ----------------------------
# mouse centering
# ----------------------------

def move_mouse_to_center():
    screen_width = win32api.GetSystemMetrics(0)
    screen_height = win32api.GetSystemMetrics(1)
    center_x = screen_width // 2
    center_y = screen_height // 2
    win32api.SetCursorPos((center_x, center_y))


# ----------------------------
# Keybind Listener
# ----------------------------
key_action = {"print_coord": False, "reset": False, "quit": False}

def on_key_press(key):
    try:
        if key.char.lower() == 'p':
            key_action["print_coord"] = True
        elif key.char.lower() == 'r':
            key_action["reset"] = True
        elif key.char.lower() == 'q':
            key_action["quit"] = True
            return False
    except:
        pass

listener = keyboard.Listener(on_press=on_key_press)
listener.start()



# ----------------------------
# Screen Capture Function (Print Coordinates)
# ----------------------------
def capture_screen_with_display(top, left, width, height, fx=0.5, fy=0.5):
    

    t0 = time.time()
    n_frames = 1

    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}

        while True:
            img = sct.grab(monitor)
            img = np.array(img)
            small = cv.resize(img, (0, 0), fx=1, fy=1)
            cv.imshow("Computer Vision", small)

            key = cv.waitKey(1)
            if key_action["quit"]:
                cv.destroyAllWindows()
                break

            if key_action["reset"]:
                key_action["reset"] = False
                print("Reset triggered. Redo selection...")
                cv.destroyAllWindows()
                start_snap_window()
                break

            if key_action["print_coord"]:
                key_action["print_coord"] = False
                coords = {
                    "top": top,
                    "left": left,
                    "width": width,
                    "height": height
                }
                print(f"Captured area: {json.dumps(coords)}") # prints like {"top": 709, "left": 603, "width": 314, "height": 74}
                cv.destroyAllWindows()
                break  # do NOT restart the snap window


# ----------------------------
# Tkinter Snap Window
# ----------------------------
class ScreenCapture:
    def __init__(self, root):
        self.root = root
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)
        self.canvas = tk.Canvas(root, cursor="cross", bg='grey11')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.start_x = None
        self.start_y = None
        self.rect = None

        self.root.bind("<Button-1>", self.on_button_press)
        self.root.bind("<B1-Motion>", self.on_mouse_drag)
        self.root.bind("<ButtonRelease-1>", self.on_button_release)

        # Start quit listener loop
        self.check_quit()

    def on_button_press(self, event):
        self.start_x = self.root.winfo_pointerx()
        self.start_y = self.root.winfo_pointery()
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='red', width=2
        )

    def on_mouse_drag(self, event):
        cur_x, cur_y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = self.root.winfo_pointerx(), self.root.winfo_pointery()
        self.root.destroy()

        top = min(self.start_y, end_y)
        left = min(self.start_x, end_x)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        if width == 0 or height == 0:
            print("Invalid selection. Width and height must be > 0.")
            start_snap_window()
            return

        capture_screen_with_display(top, left, width, height)

    # Quit listener method
    def check_quit(self):
        if key_action.get("quit"):
            print("Exited by user.")
            self.root.destroy()
            return
        self.root.after(100, self.check_quit)


# ----------------------------
# Start Snap Window
# ----------------------------
def start_snap_window():

    # Move mouse to center
    move_mouse_to_center()

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.30)
    root.attributes('-topmost', True)  # Force on top

    ScreenCapture(root)

    # Keep window on top even if Windows tries to re-order
    root.after(200, lambda: (root.lift(), root.focus_force()))


    root.mainloop()


# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    # Bring Roblox on top
    focuse_window("Roblox")
    start_snap_window()




