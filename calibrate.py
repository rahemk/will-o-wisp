#!/usr/bin/env python
"""
Calibrate the camera using .png files in the current directory of the format
XX.png, where XX is a 2-digit integer.  This will produce calib_K.json (K is
the camera matrix) and calib_D.json (D is the distortion coefficients).
"""

import cv2, os
import numpy as np
import json

#
# Parameters
#
BOARD_SHAPE = (6,9)

window_name = "Calibration"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

#
# The objp array defines the coordinates of the calibration board as a grid.  
#
objp = np.zeros((1, BOARD_SHAPE[0]*BOARD_SHAPE[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:BOARD_SHAPE[0], 0:BOARD_SHAPE[1]].T.reshape(-1, 2)

#
# Look for .png files (expected to have the format XX.png where XX is a 2-digit
# integer) in the 'calibration_images' directory and sort them.
#
datadir = "./"
img_files = np.array([datadir + f for f in os.listdir(datadir) if f.endswith(".png") ])
print(img_files)
print(img_files[0].split("."))
numbers_in_files = [int(p.split(".")[1].split("/")[1]) for p in img_files]
order = np.argsort(numbers_in_files)
img_files = img_files[order]
print(img_files)

#
# Compute the corners from each chessboard image.
#
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
for image_file in img_files:
    print(f"image_file: {image_file}")
    img = cv2.imread(image_file)
    img_shape = img.shape[:2]

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, BOARD_SHAPE, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, BOARD_SHAPE, corners2, ret)
        cv2.imshow(window_name, img)

        # Pause for 500 milliseconds.  Increase this to see the corners
        # detected for each calibration image more carefully.
        cv2.waitKey(500)

#
# Calibrate!
#
K = np.zeros((3, 3))
D = np.zeros((4, 1))
result_tuple = cv2.calibrateCamera(
    objpoints,
    imgpoints,
    gray.shape[::-1],
    K,
    D)
retval, K, D, rvecs, tvecs = result_tuple
# print(result_tuple)

#
# Estimate the re-projection error for this calibration
#
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], K, D)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2)/len(imgpoints2)
    mean_error += error
mean_error = mean_error / len(objpoints)
print(f"error: {mean_error}")

#
# Write the calibration data (i.e. the K and D arrays) to .json files.
#
with open("calib_K.json", "w") as calib_file:
    json.dump(K.tolist(), calib_file, indent=4)
with open("calib_D.json", "w") as calib_file:
    json.dump(D.tolist(), calib_file, indent=4)

print("Wrote calib_K.json and calib_D.json to the current directory.  You might want to move them elsewhere.")