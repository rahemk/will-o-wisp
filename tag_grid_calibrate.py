#!/usr/bin/env python
'''

'''

import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, hypot, pi

from wow_tag import WowTag, raw_tags_to_wow_tags
from config_loader import ConfigLoader
from tag_grid_panner import TagGridPanner
from image_processing import capture_and_preprocess

if __name__ == "__main__":

    cfg = ConfigLoader.get()
    tag_size = 50
    calibrate = True

    if cfg.show_input:
        input_window_name = "Input"
        cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    #pp = pprint.PrettyPrinter(indent=4)

    panner = TagGridPanner(cfg.output_width, cfg.output_height, tag_size, cfg.fullscreen)

    tag_centres_image = np.zeros((cfg.output_height, cfg.output_width))

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

    cap = cv2.VideoCapture(cfg.video_channel)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.input_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.input_height)

    if calibrate:
        size = (cfg.output_height, cfg.output_width)
        tg_calib_count = np.zeros(size)
        tg_calib_x = np.zeros(size)
        tg_calib_y = np.zeros(size)

    def callback(reference_tags):
        tag_centres_image = np.zeros((cfg.output_height, cfg.output_width))

        gray_image, warped_image = capture_and_preprocess(cap, cfg, homography=homography)

        raw_tags = apriltag_detector.detect(gray_image)

        detected_tags = raw_tags_to_wow_tags(raw_tags)

        # We are either calibrating or measuring the error.
        if calibrate:
            for detected_tag in detected_tags:
                x, y = detected_tag.x, detected_tag.y
                for ref_tag in reference_tags:
                    if detected_tag.id == ref_tag.id:
                        #if tg_calib_count[y,x] == 0:
                        tg_calib_count[y,x] += 1
                        tg_calib_x[y,x] = ref_tag.x
                        tg_calib_y[y,x] = ref_tag.y
                        #else:
                        #    print(f"multiple detected tags correspond to tag {ref_tag.id}")
                    
        else:
            average_error = 0
            for ref_tag in reference_tags:
                matched_tag = None
                for detected_tag in detected_tags:
                    if detected_tag.id == ref_tag.id:
                        matched_tag = detected_tag

                if matched_tag is not None:
                    average_error += hypot(ref_tag.x - matched_tag.x, ref_tag.y - matched_tag.y)
                #tag_centres_image[tag.y, tag.x] = 255
            average_error /= len(reference_tags)
            print(f"average error: {average_error}")

        #cv2.imshow("Detected Tag Centres", tag_centres_image.astype(np.uint8))
        #cv2.waitKey(1)

        if cfg.show_input:
            resize_divisor = 1
            if resize_divisor > 1:
                cv2.resizeWindow(input_window_name, warped_image.shape[1]//resize_divisor, warped_image.shape[0]//resize_divisor)
            cv2.imshow(input_window_name, warped_image)
            cv2.waitKey(10)

    panner.pan_tags(callback)

    cap.release()

    np.save("tg_calib_count", tg_calib_count)
    np.save("tg_calib_x", tg_calib_x)
    np.save("tg_calib_y", tg_calib_y)