#!/usr/bin/env python

import cv2
import numpy as np

if __name__ == "__main__":

    tg_calib_count = np.load("tg_calib_count.npy")
    tg_calib_x = np.load("tg_calib_x.npy")
    tg_calib_y = np.load("tg_calib_y.npy")

    cv2.namedWindow("Count", cv2.WINDOW_NORMAL)
    cv2.namedWindow("X", cv2.WINDOW_NORMAL)
    cv2.namedWindow("Y", cv2.WINDOW_NORMAL)

    cv2.imshow("Count", tg_calib_count)
    cv2.imshow("X", tg_calib_x)
    cv2.imshow("Y", tg_calib_y)
    cv2.waitKey(0)