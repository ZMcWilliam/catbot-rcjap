import json
import time
import cv2
import numpy as np
from helpers import camera as c

cam = c.CameraStream(camera_num=0)
cam.wait_for_image()

calibration_images = {
    "w": []
}

NUM_CALIBRATION_IMAGES = 100

time.sleep(1)

# Load the calibration map from the JSON file if it exists
calibration_data = {
    "calibration_value_w": 0,
    "calibration_map_w": [],
    "calibration_map_w_obst": [],
    "calibration_map_w_silver": [],
}

try:
    with open("calibration.json", "r", encoding="utf-8") as json_file:
        calibration_data = json.load(json_file)
except FileNotFoundError:
    pass # If the file doesn't exist, we'll create it later

while True:
    requested = input("Enter 'w' for white calibration or 'q' to quit: ")

    if requested == "q":
        break

    if requested not in calibration_images:
        continue

    calibration_images[requested] = []

    while NUM_CALIBRATION_IMAGES > len(calibration_images[requested]):
        img0 = cam.read_stream()
        img0_resized = cam.resize_image(img0)
        img0_gray = cv2.cvtColor(img0_resized, cv2.COLOR_BGR2GRAY)
        img0_gray = cv2.GaussianBlur(img0_gray, (5, 5), 0)

        img0_resized_obst = cam.resize_image_obstacle(img0)
        img0_gray_obst = cv2.cvtColor(img0_resized_obst, cv2.COLOR_BGR2GRAY)
        img0_gray_obst = cv2.GaussianBlur(img0_gray_obst, (5, 5), 0)

        img0_resized_silver = cam.resize_image(img0, offset_y=0)
        img0_gray_silver = cv2.cvtColor(img0_resized_silver, cv2.COLOR_BGR2GRAY)
        img0_gray_silver = cv2.GaussianBlur(img0_gray_silver, (5, 5), 0)

        calibration_images[requested].append(img0_gray)
        calibration_images[requested + "_obst"] = img0_gray_obst
        calibration_images[requested + "_silver"] = img0_gray_silver
        print(f"Calibration image {len(calibration_images[requested])} of {NUM_CALIBRATION_IMAGES} captured.")

        time.sleep(0.01)
        cv2.imshow("img0_gray", img0_gray)
        cv2.imshow("img0_gray_obst", img0_gray_obst)
        cv2.imshow("img0_gray_silver", img0_gray_silver)
        k = cv2.waitKey(1)
        if k & 0xFF == ord('q'):
            break

    for suffix in ["", "_obst", "_silver"]:
        # Calculate the average grayscale value across all calibration images
        calibration_data["calibration_value_" + requested + suffix] = np.mean([np.mean(img_gray) for img_gray in calibration_images[requested]])
        # Create an empty calibration map
        calibration_map = np.zeros_like(calibration_images[requested + suffix][0], dtype=np.float32)
        # Calculate the calibration map
        for img_gray in calibration_images[requested + suffix]:
            calibration_map += img_gray

        calibration_map //= len(calibration_images[requested + suffix])

        calibration_data["calibration_map_" + requested + suffix] = calibration_map.tolist()

    # Save the calibration map to the JSON file
    with open("calibration.json", "w", encoding="utf-8") as json_file:
        json.dump(calibration_data, json_file)

    print("Calibration images captured, updated calibration.json")

cam.stop()
