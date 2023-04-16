#!/usr/bin/env python

"""
An Example using pysbpl.

Author: Poine, Schmittle
"""

import os
import numpy as np
import pysbpl
from pysbpl import map_util, planner, plot
from math import pi
from random import random

if __name__ == "__main__":
    pysbl_dir = os.path.dirname(pysbpl.__file__)

    mprim_path = "motion_primitives/mushr.mprim"

    width = 100
    height = 100
    occ_grid = np.zeros((height, width))
    occ_grid[40:60, 40:60] = 1

    map = map_util.Map(mprim_path=mprim_path, unknown_value=1)
    map.load_map(occ_grid, 1, np.array([0, 0, 0]), 0.75, 0.25)

    # rhw = robot half width, rhl = robot half length
    rhl = 5
    rhw = 2
    robot_perimeter = [[-rhl, -rhw],
                       [rhl, -rhw],
                       [rhl, rhw],
                       [-rhl, rhw]]

    params = {
        "map": map,
        "perimeter": robot_perimeter, # robot footprint in robot frame
        "vel": 10,  # speed of translational movement m/s
        "time_45_deg": 1,  # time to turn 45 degrees in place speed of rotational movement seconds
        "mprim_path": (mprim_path).encode(
            "utf-8"
        ),  # path to motion primitives
        # See http://wiki.ros.org/costmap_2d for details on the costmap
        "obs_thresh": 1,  # lethal cost
        "inscribed_thresh": 1,  # likely in collision cost
        "possibly_circumscribed_thresh": 0,  # possibly in collision cost
    }

    sbpl_planner = planner.Planner(**params)

    #start = [-9.52, -2.16, -0.105]
    #goal = [-47.09, -26.117, -0.23]

    #start = [10, 10, 0]
    #goal = [80, 80, 0]
    
    for i in range(100):
        start = [100*random(), 100 * random(), 0]
        goal = [100*random(), 100 * random(), 0]
        path, actions = sbpl_planner.plan(start, goal, init_eps=3.0, backwards_till_solution=False)

    if path is not None:
        g = plot.Window()
        g.display_map(params["map"])
        g.display_path(path)
        g.show()
