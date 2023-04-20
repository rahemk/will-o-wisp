import cv2, time
from pupil_apriltags import Detector
import pprint
import numpy as np
from math import atan2

video_channel = 4

raw_window_name = "Raw"

if __name__ == "__main__":

    at_detector = Detector(
       families="tag36h11",
       nthreads=1,
       quad_decimate=1.0,
       quad_sigma=0.0,
       refine_edges=1,
       decode_sharpening=0.25,
       debug=0
    )

    cv2.namedWindow(raw_window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(raw_window_name, cv2.WND_PROP_TOPMOST, 1)
    pp = pprint.PrettyPrinter(indent=4)

    cap = None 

    if cap is None: cap = cv2.VideoCapture(video_channel)
    width = 1920
    height = 1080
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    time.sleep(5)

    while True:

        start_time = time.time()

        ret, raw_image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        # Convert to grayscale
        gray_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)

        tags = at_detector.detect(gray_image)
        #pp.pprint(f"NUMBER OF TAGS: {len(tags)}")
        
        # Visualize tags
        for tag in tags:
            #print(tag)
            cx = int(tag.center[0])
            cy = int(tag.center[1])
            #cv2.circle(raw_image, (cx, cy), 10, (255,0,255), thickness=5)

            for index in range(4):
                intensity = int(255*((index + 1) / 4.0))
                x = int(tag.corners[index, 0])
                y = int(tag.corners[index, 1])
                cv2.circle(raw_image, (x, y), 10, (intensity, intensity, intensity), thickness=3)
                #cv2.putText(raw_image, str(index), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

            # Estimate the angle, choosing corner 1 as the origin and corner 0
            # as being in the forwards direction, relative to corner 1.
            x = tag.corners[0,0] - tag.corners[1,0]
            y = tag.corners[0,1] - tag.corners[1,1]
            #x = x_vector_imgpts[0][0][0] - origin_imgpts[0][0][0]
            #y = x_vector_imgpts[0][0][1] - origin_imgpts[0][0][1]
            theta = atan2(y, x)
            cv2.putText(raw_image, str(theta), (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        resize_divisor = 1
        if resize_divisor > 1:
            cv2.resizeWindow(raw_window_name, raw_image.shape[1]//resize_divisor, raw_image.shape[0]//resize_divisor)
        cv2.imshow(raw_window_name, raw_image)

        c = cv2.waitKey(10)

        # press ESC or q to exit
        if c == 27 or c == ord('q'):
            break

        elapsed = time.time() - start_time
        print(f"loop elapsed time: {elapsed}")

    if cap is not None: cap.release()
