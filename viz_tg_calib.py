#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":

    tg_calib_count = np.load("tg_calib_count.npy")
    tg_calib_x = np.load("tg_calib_x.npy")
    tg_calib_y = np.load("tg_calib_y.npy")

    fig, axs = plt.subplots(2, 2)
    axs[0, 0].imshow(tg_calib_count)
    axs[1, 0].imshow(tg_calib_x)
    axs[1, 1].imshow(tg_calib_y)
    plt.show()