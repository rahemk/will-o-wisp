#!/usr/bin/env python

import cv2

# Parameters
video_channel = 0
calib_dir = "calib_images_macbook/"
window_name = "Input"

# State variables and initialization
save_index = 0
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

if __name__ == "__main__":

    cap = None
    print("Hit space to capture images.")

    while True:
        if cap is None: cap = cv2.VideoCapture(video_channel)
        #width = 1280
        #height = 720
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        ret, image = cap.read()
        if not ret:
            print('Cannot read video.')
            break

        #resize_divisor = 1
        #cv2.resizeWindow(window_name, image.shape[1]//resize_divisor, image.shape[0]//resize_divisor)
        cv2.imshow(window_name, image)
        c = cv2.waitKey(10)
        #print(f"key: {c}")

        if c == 32:
            filename = f"{calib_dir}{save_index:02}.png"
            print(f"Saving: {filename}")
            cv2.imwrite(filename, image)
            save_index += 1

        # press ESC or q to exit
        if c == 27 or c == ord('q'):
            break

    if cap is not None: cap.release()
