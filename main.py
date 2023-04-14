import cv2, json, pprint, time
import numpy as np
from pupil_apriltags import Detector
from math import atan2, cos, pi, sin

from game_screen import GameScreen
#from controller_set import ControllerSet

if __name__ == "__main__":

    try:
        config_filename = 'config_lab.json'
        config_dict = json.load(open(config_filename, 'r'))

        video_channel = config_dict['video_channel']
        manual_mode = config_dict['manual_mode']
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

    #cv2.namedWindow(input_window_name, cv2.WINDOW_NORMAL)
    #cv2.setWindowProperty(input_window_name, cv2.WND_PROP_TOPMOST, 1)

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

        tags = apriltag_detector.detect(gray_image)

        movement = ""
        if manual_mode == 1:
            movement = game_screen.get_movement()
        else:
            # Compute a dictionary of the desired movements for all tags.  Tags
            # not corresponding to active robots will not have an entry.
            #movement_dict = controller_set.get_movements(decoded_tags)
            assert False, 'Only manual mode supported.'

        robot_poses = []
        guide_positions = []

        for tag in tags:
            #print(tag)
            cx = int(tag.center[0])
            cy = int(tag.center[1])
            #cv2.circle(raw_image, (cx, cy), 10, (255,0,255), thickness=5)

            # Estimate the angle, choosing corner 1 as the origin and corner 0
            # as being in the forwards direction, relative to corner 1.
            x = tag.corners[0,0] - tag.corners[1,0]
            y = tag.corners[0,1] - tag.corners[1,1]
            tag_angle = atan2(y, x) + pi/2
            #cv2.putText(raw_image, str(theta), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            robot_poses.append((cx, cy, tag_angle))

            #forward, angular = movement_dict[tag['tag_id']]
            c = cos(tag_angle)
            s = sin(tag_angle)
            if movement != "":
                for guide_displacement in guide_displacement_dict[movement]:
                    print(guide_displacement)
                    # Movement vector relative to robot frame.
                    Rx = guide_displacement[0]
                    Ry = guide_displacement[1]

                    # Rotate this vector into the world frame.
                    Wx = c * Rx - s * Ry
                    Wy = s * Rx + c * Ry
                    x = cx + Wx
                    y = cy + Wy

                    guide_positions.append((x, y))

        game_screen.update(robot_poses, guide_positions)

        #resize_divisor = 1
        #if resize_divisor > 1:
        #    cv2.resizeWindow(input_window_name, input_image.shape[1]//resize_divisor, input_image.shape[0]//resize_divisor)
        #cv2.imshow(input_window_name, input_image)
        #cv2.waitKey(10)

        elapsed = time.time() - start_time
        print(f"loop elapsed time: {elapsed}")

    if cap is not None: cap.release()