import cv2
import numpy as np
from scipy import interpolate

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

def interpolate_missing_values(image, image_with_zeros_for_missing):
    # https://stackoverflow.com/questions/37662180/interpolate-missing-values-2d-python/39596856#39596856
    mask = image_with_zeros_for_missing == 0

    h, w = image.shape[:2]
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))

    known_x = xx[~mask]
    known_y = yy[~mask]
    known_v = image[~mask]
    missing_x = xx[mask]
    missing_y = yy[mask]

    interp_values = interpolate.griddata(
        (known_x, known_y), known_v, (missing_x, missing_y),
        method='linear', fill_value=0
    )

    interp_image = image.copy()
    interp_image[missing_y, missing_x] = interp_values

    return interp_image