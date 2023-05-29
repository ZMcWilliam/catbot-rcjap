import time
import cv2
import json
import helper_camera
import numpy as np
from threading import Thread
from picamera2 import Picamera2

cams = helper_camera.CameraController()
cams.start_stream(0)
time.sleep(1)

# Load the calibration map from the JSON file
with open("calibration.json", "r") as json_file:
    calibration_data = json.load(json_file)
calibration_map_black = np.array(calibration_data["calibration_map_b"], dtype=np.float32)
calibration_map_white = np.array(calibration_data["calibration_map_w"], dtype=np.float32)

while True:
    img0 = cams.read_stream(0)
    img0 = img0[0:img0.shape[0]-38, 0:img0.shape[1]-70]
    img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2RGB)

    img0_gray = cv2.cvtColor(img0, cv2.COLOR_RGB2GRAY)
    # img0_gray = cv2.equalizeHist(img0_gray)
    img0_gray = cv2.GaussianBlur(img0_gray, (5, 5), 0)

    print(img0_gray[100][100], calibration_map_black[100][100], calibration_map_white[100][100])

    # img0_gray_scaled = 240 / np.clip(calibration_map, a_min=1, a_max=None) * img0_gray  # Scale white values based on the inverse of the calibration map
    # img0_gray_scaled = np.clip(img0_gray_scaled, 0, 255)    # Clip the scaled image to ensure values are within the valid range
    # img0_gray_scaled = img0_gray_scaled.astype(np.uint8)    # Convert the scaled image back to uint8 data type

    # Scale black values
    img0_gray_scaled_black = img0_gray / np.clip(calibration_map_black, a_min=1, a_max=None) * 255
    img0_gray_scaled_black = np.clip(img0_gray_scaled_black, 0, 255).astype(np.uint8)

    # Scale white values
    img0_gray_scaled_white = 255 / np.clip(calibration_map_white, a_min=1, a_max=None) * img0_gray
    img0_gray_scaled_white = np.clip(img0_gray_scaled_white, 0, 255).astype(np.uint8)

    # Combine the scaled black and white values
    img0_gray_scaled = img0_gray_scaled_black + img0_gray_scaled_white
    img0_gray_scaled = np.clip(img0_gray_scaled, 0, 255).astype(np.uint8)

    cv2.imshow(f"img0", img0)
    cv2.imshow(f"img0_gray", img0_gray)
    cv2.imshow(f"img0_gray_scaled", img0_gray_scaled)
    cv2.imshow(f"img0_gray_scaled_black", img0_gray_scaled_black)
    cv2.imshow(f"img0_gray_scaled_white", img0_gray_scaled_white)

    k = cv2.waitKey(1)
    if (k & 0xFF == ord('q')):
        break

cams.stop()