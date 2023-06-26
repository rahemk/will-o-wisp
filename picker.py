#!/usr/bin/env python

import cv2, json
import numpy as np

from image_processing import capture_and_preprocess
from config_loader import ConfigLoader
cfg = ConfigLoader.get()

def mouse_callback(event, x, y, flags, param):
    print("MOUSE")
    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(clicked_points)

# State variables and initialization
window_name = "Input"
image = None
clicked_points = []
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
cv2.setMouseCallback(window_name, mouse_callback)

if __name__ == "__main__":

    undistort = True

    cap = cv2.VideoCapture(cfg.video_channel)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    while True:
        image, _ = capture_and_preprocess(cap, cfg)

        for pt in clicked_points:
            cv2.circle(image, pt, 10, (255,0,255), thickness=5)

        #resize_divisor = 1
        #cv2.resizeWindow(window_name, image.shape[1]//resize_divisor, image.shape[0]//resize_divisor)
        cv2.imshow(window_name, image)
        c = cv2.waitKey(10)

        cv2.imwrite("camera.png", image);

        # press ESC or q to exit
        if c == 27 or c == ord('q'):
            break

    cap.release()