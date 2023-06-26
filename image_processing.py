import cv2

def capture_and_preprocess(cap, cfg, homography=None):
    ret, image = cap.read()
    h, w = image.shape[:2]
    if w != cfg.input_width or h != cfg.input_height:
        if not capture_and_preprocess.warned:
            print("cv2 is ignoring the specified width/height. Resizing...")
            capture_and_preprocess.warned = True
        image = cv2.resize(image, (cfg.input_width, cfg.input_height))
    if not ret:
        print('Cannot read video.')
        return None, None

    # Undistort the raw image.
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(cfg.calib_K, cfg.calib_D, (w,h), 1, (w,h))
    undistorted = cv2.undistort(image, cfg.calib_K, cfg.calib_D, None, newcameramtx)

    # Warp the raw image.
    warped_image = None
    if homography is not None:
        warped_image = cv2.warpPerspective(undistorted, homography, (cfg.output_width, cfg.output_height))

        return cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY), warped_image
    else:

        return cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY), None

# An attribute to the above function just so that we display the resize warning
# only once.
capture_and_preprocess.warned = False