import ctypes
import time

import keyboard
import cv2
import numpy as np
import pydirectinput

# Make the process DPI aware to handle DPI scaling
# At the beginning of your script, add:
ctypes.windll.shcore.SetProcessDpiAwareness(1)


# ctypes structure for the point (x, y)
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


# Constants for the mouse input type
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

# ctypes wrappers for high precision mouse events and cursor position
user32 = ctypes.WinDLL('user32', use_last_error=True)


def get_mouse_pos():
    """
    Get the current mouse cursor coordinates.
    """
    point = POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return (point.x, point.y)


def move_relative(dx, dy, calibration_factor=1):
    """
    Move the mouse cursor relative to its current position by (dx, dy),
    adjusted by a calibration factor for precision.
    """
    corrected_dx = int(dx * calibration_factor)
    corrected_dy = int(dy * calibration_factor)
    user32.mouse_event(MOUSEEVENTF_MOVE, corrected_dx, corrected_dy, 0, 0)

import mss
def scr():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)
        screenshot_np = np.array(sct_img)
    return screenshot_np

def distance(coords1, coords2):
    x1, y1 = coords1
    x2, y2 = coords2
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def click():
    """
    Simulate a left mouse button click.
    """
    MOUSEEVENTF_LEFTDOWN = 0x0002  # Left mouse button down
    MOUSEEVENTF_LEFTUP = 0x0004    # Left mouse button up

    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)  # Press the left mouse button
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)    # Release the left mouse button

print("ready")


i = 0
while True:
    while keyboard.is_pressed("shift"):
        i+=1
        current_pos = get_mouse_pos()

        start_time = time.time()
        image = scr()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([100, 150, 0])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        result = np.where(mask == 255, 255, 0).astype(np.uint8)
        image = result
        startY, endY = 100, -100
        cropped_image = image[startY:endY, :]

        contours, _ = cv2.findContours(cropped_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        centers = []

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])+100
                centers.append((cX, cY))

        cv2.imwrite("result.png", cropped_image)

        closest_center = min(centers, key=lambda center: distance(center, current_pos))

        current_pos = get_mouse_pos()
        #print(f"Current mouse position: {current_pos}")
        #print(f"Target center : {closest_center}")

        offset_x, offset_y = closest_center[0] - current_pos[0], closest_center[1] - current_pos[1]
        #print("Offset :",offset_x, offset_y)

        move_relative(offset_x, offset_y)

        current_pos = get_mouse_pos()
        #print(f"Current mouse position: {current_pos}")

        #click only if mouse in a 10 pixel radius of the targetted center
        if abs(distance(current_pos, closest_center)) < 10:
            click()
        #else:
            #print("didn't click", current_pos, closest_center)

        print(time.time() - start_time)
        # time.sleep(0.1)
        # move_relative(-offset_x, -offset_y)








