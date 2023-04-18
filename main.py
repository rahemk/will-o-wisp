#!/usr/bin/env python

import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, cos, pi, sin
# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

from game_screen import GameScreen

# Customize the level and controller.
from levels import TestLevel
from controllers import SmoothController1
controller = SmoothController1()

def raw_tags_to_tags(raw_tags):
    tags = []
    for raw_tag in raw_tags:
        cx = int(raw_tag.center[0])
        cy = int(raw_tag.center[1])
        #cv2.circle(raw_image, (cx, cy), 10, (255,0,255), thickness=5)

        # Estimate the angle, choosing corner 1 as the origin and corner 0
        # as being in the forwards direction, relative to corner 1.
        x = raw_tag.corners[0,0] - raw_tag.corners[1,0]
        y = raw_tag.corners[0,1] - raw_tag.corners[1,1]
        tag_angle = atan2(y, x) + pi/2
        #cv2.putText(raw_image, str(theta), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        tags.append({'id': raw_tag.tag_id, 'x': cx, 'y': cy, 'angle': tag_angle})
    return tags

def compute_guides(tags, movement_dict):
    guide_positions = []

    #forward, angular = movement_dict[tag['tag_id']]
    for tag in tags:
        c = cos(tag['angle'])
        s = sin(tag['angle'])
        if not tag['id'] in movement_dict:
            continue

        movement = movement_dict[tag['id']]
        if movement == "":
            continue

        for guide_displacement in guide_displacement_dict[movement]:
            print(guide_displacement)
            # Movement vector relative to robot frame.
            Rx = guide_displacement[0]
            Ry = guide_displacement[1]

            # Rotate this vector into the world frame.
            Wx = c * Rx - s * Ry
            Wy = s * Rx + c * Ry
            x = tag['x'] + Wx
            y = tag['y'] + Wy

            guide_positions.append((x, y))

    return guide_positions

def compute_curves(tags, goal_dict):
    curves = []

    for tag in tags:
        if not tag['id'] in goal_dict:
            continue

        points = controller.get_curve_points(Vector2(tag['x'], tag['y']), tag['angle'], goal_dict[tag['id']])
        curves.append(points)

    return curves


if __name__ == "__main__":

    try:
        config_filename = 'config_lab.json'
        config_dict = json.load(open(config_filename, 'r'))

        video_channel = config_dict['video_channel']
        show_input = bool(config_dict['show_input'])
        output_width = config_dict['output_width']
        output_height = config_dict['output_height']
        screen_corners = []
        screen_corners.append( config_dict['upper_left'] )
        screen_corners.append( config_dict['upper_right'] )
        screen_corners.append( config_dict['lower_right'] )
        screen_corners.append( config_dict['lower_left'] )
        guide_displacement_dict = {
            "left": [config_dict['left_guide_displacement']],
            "forward": [config_dict['left_guide_displacement'], config_dict['right_guide_displacement']],
            "right": [config_dict['right_guide_displacement']]
        }
    except:
        print('Cannot load config: %s'% config_filename)  

    game_screen = GameScreen(output_width, output_height)

    level = TestLevel(output_width, output_height)

    apriltag_detector = Detector(
       families="tag36h11",
       nthreads=5,
       quad_decimate=1.0,
       quad_sigma=0.0,
       refine_edges=1,
       decode_sharpening=0.25,
       debug=0
    )

    output_corners = [[0, 0], [output_width-1, 0], [output_width-1, output_height-1], [0, output_height-1]]
    homography, status = cv2.findHomography(np.array(screen_corners), np.array(output_corners))

    if show_input:
        input_window_name = "Input"
        cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    cap = None 
    pp = pprint.PrettyPrinter(indent=4)

    while True:

        start_time = time.time()

        if cap is None: cap = cv2.VideoCapture(video_channel)
        ret, raw_image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        # Warp the raw image.
        warped_image = cv2.warpPerspective(raw_image, homography, (output_width, output_height))
        gray_image = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)

        raw_tags = apriltag_detector.detect(gray_image)

        tags = raw_tags_to_tags(raw_tags)

        game_screen.handle_events()
        manual_movement = game_screen.get_movement()

        # Compute a dictionary of the desired movements for all tags.  The
        # level will determine which robots are manually controlled
        # and which are autonomous.  From the perspective of this script (main.py).
        # There is no difference, they all just have some movement (possibly empty).
        movement_dict = level.get_movements(manual_movement, tags)

        # Similarly, compute a dictionary of the desired goal positions for all
        # tags.
        goal_dict = level.get_goals(manual_movement, tags)

        guide_positions = compute_guides(tags, movement_dict)

        curves = compute_curves(tags, goal_dict)

        game_screen.update(tags, guide_positions, curves)

        if show_input:
            resize_divisor = 1
            if resize_divisor > 1:
                cv2.resizeWindow(input_window_name, warped_image.shape[1]//resize_divisor, warped_image.shape[0]//resize_divisor)
            cv2.imshow(input_window_name, warped_image)
            cv2.waitKey(10)

        elapsed = time.time() - start_time
        print(f"loop elapsed time: {elapsed}")

    if cap is not None: cap.release()