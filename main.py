#!/usr/bin/env python

import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, cos, pi, sin
# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

from wow_tag import WowTag, raw_tags_to_wow_tags, apply_tg_calibration_to_raw_tags
from config_loader import ConfigLoader
from game_screen import GameScreen
from image_processing import capture_and_preprocess
from config_loader import venue

# Customize the level and controller.
from levels import DummyLevel, SynchronyLevel, TestLevel, FirstGameLevel, VersusGameLevel
from generators import CurveArcGenerator
#from generators import GuidanceImageGenerator
from controllers import SmoothController1
#from controllers import DubinsController
#from controllers import DubinsLightController
curve_arc_generator = CurveArcGenerator(SmoothController1())
#guidance_generator = GuidanceGenerator(DubinsController())

if __name__ == "__main__":

    cfg = ConfigLoader.get()

    game_screen = GameScreen(cfg.output_width, cfg.output_height, cfg.fullscreen)

    #guidance_image_generator = GuidanceImageGenerator(cfg.output_width, cfg.output_height, DubinsLightController())

    #level = DummyLevel(cfg.output_width, cfg.output_height)
    #level = TestLevel(cfg.output_width, cfg.output_height)
    #level = SynchronyLevel(cfg.output_width, cfg.output_height)
    #level = FirstGameLevel(cfg.output_width, cfg.output_height)
    level = VersusGameLevel(cfg.output_width, cfg.output_height)

    apriltag_detector = Detector(
       families="tag36h11",
       nthreads=5,
       quad_decimate=1.0,
       quad_sigma=0.0,
       refine_edges=1,
       decode_sharpening=0.25,
       debug=0
    )

    homography = None
    if cfg.use_homography:
        output_corners = [[0, 0], [cfg.output_width-1, 0], [cfg.output_width-1, cfg.output_height-1], [0, cfg.output_height-1]]
        homography, status = cv2.findHomography(np.array(cfg.screen_corners), np.array(output_corners))

    if cfg.use_tg_calibration:
        directory = f"tg_calib_{venue}/delta_{cfg.tg_delta}"

        tg_calib_count = np.load(f"{directory}/tg_calib_count_interp.npy")
        tg_calib_x = np.load(f"{directory}/tg_calib_x_filtered.npy")
        tg_calib_y = np.load(f"{directory}/tg_calib_y_interp.npy")

    if cfg.show_input:
        input_window_name = "Input"
        cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    #pp = pprint.PrettyPrinter(indent=4)

    cap = cv2.VideoCapture(cfg.video_channel, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Turn off autofocus
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    while True:

        start_time = time.time()

        gray_image, warped_image = capture_and_preprocess(cap, cfg, homography=homography)

        raw_tags = apriltag_detector.detect(gray_image)

        if cfg.use_tg_calibration:
            raw_tags = apply_tg_calibration_to_raw_tags(raw_tags, tg_calib_count, tg_calib_x, tg_calib_y)

        wow_tags = raw_tags_to_wow_tags(raw_tags)

        game_screen.handle_events()

        if game_screen.get_restart():
            if isinstance(level, FirstGameLevel):
                level = FirstGameLevel(cfg.output_width, cfg.output_height)
            elif isinstance(level, VersusGameLevel):
                level = VersusGameLevel(cfg.output_width, cfg.output_height)
            game_screen.restart = False

        do_screenshot, screenshot_index = game_screen.get_do_screenshot()

        if isinstance(level, VersusGameLevel):
            manual_movement = {
                "p1": game_screen.get_movement_for_player1(),
                "p2": game_screen.get_movement_for_player2()
            }
        else:
            manual_movement = game_screen.get_movement_for_player1()


        # The level is responsibility for determine the application's evolution.
        # This is communicated in a dictionary of journeys for tags (i.e. robots)
        # and a list of sprites which are graphical elements.
        journey_dict = level.get_journey_dict(manual_movement, wow_tags)

        sprites = level.get_sprites()

        arcs, curves = curve_arc_generator.generate(wow_tags, journey_dict)
        #curve_image = guidance_image_generator.generate(wow_tags, journey_dict)
        #cv2.imshow("curve_image", curve_image)
        #cv2.waitKey(1)

        game_screen.update(wow_tags, arcs, curves, sprites, game_over=getattr(level, "game_over", False), level=level)
        #game_screen.update(wow_tags, [], [], sprites, background_image=curve_image)

        if do_screenshot:
            #filename_raw = f"screenshots/raw_{screenshot_index:02}.png"
            filename_warped = f"screenshots/warped_{screenshot_index:02}.png"
            try:
                #cv2.imwrite(filename_raw, raw_image)
                cv2.imwrite(filename_warped, warped_image)
            except:
                #print(f"Problem writing to {filename_raw} or {filename_warped}")
                print(f"Problem writing to {filename_warped}")

        if cfg.show_input:
            resize_divisor = 1
            if resize_divisor > 1:
                cv2.resizeWindow(input_window_name, gray_image.shape[1]//resize_divisor, gray_image.shape[0]//resize_divisor)
            cv2.imshow(input_window_name, gray_image)
            cv2.waitKey(10)

        elapsed = time.time() - start_time
        print(f"loop elapsed time: {elapsed}")

        #time.sleep(0.1)

    cap.release()