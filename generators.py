import cv2
import numpy as np
from scipy import ndimage
from math import atan2, pi
from utils.angles import get_smallest_signed_angular_difference, normalize_angle_0_2pi

# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

# An arc has a fixed angular extent, defined by these constants.
ARC_START = pi/8
ARC_END = 3*pi/4

class Arc:
    def __init__(self, start_x, start_y, start_angle, stop_angle):
        self.start_x = start_x
        self.start_y = start_y
        self.start_angle = start_angle
        self.stop_angle = stop_angle

'''
This one generates a list of arcs and curves corresponding to the controller's
action for each tag.
'''
class CurveArcGenerator:
    def __init__(self, controller):
        self.controller = controller

    def generate(self, wow_tags, journey_dict):
        arcs = []
        curves = []
        for wow_tag in wow_tags:
            id = wow_tag.id
            if not id in journey_dict:
                continue

            journey = journey_dict[id]
            alpha = get_smallest_signed_angular_difference(wow_tag.angle, atan2(journey.goal_y - wow_tag.y, journey.goal_x - wow_tag.x))

            if True: #abs(alpha) < pi/8:
                # Generate curve for this tag.
                points = self.controller.get_curve_points(journey_dict[id])
                curves.append(points)

            else:
                # Generate arc.  The following ridiculous normalizing and sign-flipping is all to
                # satisfy pygame's arc drawing function.
                # start_angle = normalize_angle_0_2pi(-wow_tag.angle)
                # stop_angle = normalize_angle_0_2pi(-wow_tag.angle + alpha)
                # if start_angle < stop_angle:
                #     arc = Arc(wow_tag.x, wow_tag.y, start_angle, stop_angle)
                # else:
                #     arc = Arc(wow_tag.x, wow_tag.y, stop_angle, start_angle)
                # arcs.append(arc)

                start_angle = normalize_angle_0_2pi(-wow_tag.angle)
                #print(f"alpha: {alpha} , start_angle: {start_angle}")
                if alpha < 0:
                    arc = Arc(wow_tag.x, wow_tag.y, start_angle - ARC_END, start_angle - ARC_START)
                else:
                    arc = Arc(wow_tag.x, wow_tag.y, start_angle + ARC_START, start_angle + ARC_END)
                arcs.append(arc)

                # While we're in the mode of generating arcs, we're not using the journey's start angle 
                # or start position---those may also be growing "stale" as the robot shifts.  We'll
                # constantly update them here, but they'll remain fixed once the angle to the goal
                # goes under the threshold.
                journey.start_x = wow_tag.x
                journey.start_y = wow_tag.y
                journey.start_angle = wow_tag.angle

        return arcs, curves

'''
This one generates an image with control curves already drawn.
'''
class GuidanceImageGenerator:
    def __init__(self, width, height, controller):
        self.width = width
        self.height = height
        self.controller = controller

    def generate(self, wow_tags, journey_dict):
        curves = []
        for wow_tag in wow_tags:
            id = wow_tag.id
            if not id in journey_dict:
                continue

            journey = journey_dict[id]
            alpha = get_smallest_signed_angular_difference(wow_tag.angle, atan2(journey.goal_y - wow_tag.y, journey.goal_x - wow_tag.x))

            # Generate curve for this tag.
            points = self.controller.get_curve_points(journey_dict[id])
            curves.append(points)

        # Creating this image with width rows and height columns to match
        # pygame, even though its in violation of normal numpy convention
        image = np.zeros((self.width, self.height))
        for curve in curves:
            for point in curve:
                image[point[0], point[1]] = 2**32 - 1

        image = ndimage.grey_dilation(image, size=(10, 10))

        return image