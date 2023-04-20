#!/usr/bin/env python

import cv2, json
import numpy as np

from config_loader import ConfigLoader
cfg = ConfigLoader.get()

def mouse_callback(event, x, y, flags, param):
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

    cap = cv2.VideoCapture(cfg.video_channel)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    while True:
        ret, image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        # Undistort the image to match future processing in main.py.
        h, w = image.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cfg.calib_K, cfg.calib_D, (w,h), 1, (w,h))
        image = cv2.undistort(image, cfg.calib_K, cfg.calib_D, None, newcameramtx)

        for pt in clicked_points:
            cv2.circle(image, pt, 10, (255,0,255), thickness=5)

        #resize_divisor = 1
        #cv2.resizeWindow(window_name, image.shape[1]//resize_divisor, image.shape[0]//resize_divisor)
        cv2.imshow(window_name, image)
        c = cv2.waitKey(10)

        # press ESC or q to exit
        if c == 27 or c == ord('q'):
            break

    cap.release()