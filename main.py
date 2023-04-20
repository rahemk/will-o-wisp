#!/usr/bin/env python

import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, cos, pi, sin
# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

from wow_tag import WowTag, raw_tags_to_wow_tags
from config_loader import ConfigLoader
from game_screen import GameScreen

# Customize the level and controller.
from levels import TestLevel
from controllers import SmoothController1
controller = SmoothController1()

def compute_guides(wow_tags, movement_dict):
    guide_positions = []

    #forward, angular = movement_dict[tag['tag_id']]
    for wow_tag in wow_tags:
        c = cos(wow_tag.angle)
        s = sin(wow_tag.angle)
        if not wow_tag.id in movement_dict:
            continue

        movement = movement_dict[wow_tag.id]
        if movement == "":
            continue

        for guide_displacement in cfg.guide_displacement_dict[movement]:
            print(guide_displacement)
            # Movement vector relative to robot frame.
            Rx = guide_displacement[0]
            Ry = guide_displacement[1]

            # Rotate this vector into the world frame.
            Wx = c * Rx - s * Ry
            Wy = s * Rx + c * Ry
            x = wow_tag.x + Wx
            y = wow_tag.y + Wy

            guide_positions.append((x, y))

    return guide_positions

def compute_curves(wow_tags, goal_dict):
    curves = []
    for wow_tag in wow_tags:
        if not wow_tag.id in goal_dict:
            continue
        points = controller.get_curve_points(Vector2(wow_tag.x, wow_tag.y), wow_tag.angle, goal_dict[wow_tag.id])
        curves.append(points)
    return curves


if __name__ == "__main__":

    cfg = ConfigLoader.get()

    game_screen = GameScreen(cfg.output_width, cfg.output_height)

    level = TestLevel(cfg.output_width, cfg.output_height)

    apriltag_detector = Detector(
       families="tag36h11",
       nthreads=5,
       quad_decimate=1.0,
       quad_sigma=0.0,
       refine_edges=1,
       decode_sharpening=0.25,
       debug=0
    )

    output_corners = [[0, 0], [cfg.output_width-1, 0], [cfg.output_width-1, cfg.output_height-1], [0, cfg.output_height-1]]
    homography, status = cv2.findHomography(np.array(cfg.screen_corners), np.array(output_corners))

    if cfg.show_input:
        input_window_name = "Input"
        cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    #pp = pprint.PrettyPrinter(indent=4)

    cap = cv2.VideoCapture(cfg.video_channel)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    while True:

        start_time = time.time()

        ret, raw_image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        # Undistort the raw image.  This also has to be done in picker.py so that
        # the picked corners used to build the homography matrix are consistent.
        h, w = raw_image.shape[:2]
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cfg.calib_K, cfg.calib_D, (w,h), 1, (w,h))
        undistorted = cv2.undistort(raw_image, cfg.calib_K, cfg.calib_D, None, newcameramtx)

        # Warp the raw image.
        warped_image = cv2.warpPerspective(undistorted, homography, (cfg.output_width, cfg.output_height))
        print(warped_image.shape)
        gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

        raw_tags = apriltag_detector.detect(gray_image)

        wow_tags = raw_tags_to_wow_tags(raw_tags)

        game_screen.handle_events()
        manual_movement = game_screen.get_movement()

        # Compute a dictionary of the desired movements for all tags.  The
        # level will determine which robots are manually controlled
        # and which are autonomous.  From the perspective of this script (main.py).
        # There is no difference, they all just have some movement (possibly empty).
        movement_dict = level.get_movements(manual_movement, wow_tags)

        # Similarly, compute a dictionary of the desired goal positions for all
        # tags.
        goal_dict = level.get_goals(manual_movement, wow_tags)

        guide_positions = compute_guides(wow_tags, movement_dict)

        curves = compute_curves(wow_tags, goal_dict)

        game_screen.update(wow_tags, guide_positions, curves)

        if cfg.show_input:
            resize_divisor = 1
            if resize_divisor > 1:
                cv2.resizeWindow(input_window_name, warped_image.shape[1]//resize_divisor, warped_image.shape[0]//resize_divisor)
            cv2.imshow(input_window_name, warped_image)
            cv2.waitKey(10)

        elapsed = time.time() - start_time
        print(f"loop elapsed time: {elapsed}")

    cap.release()