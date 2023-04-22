from math import atan2, pi
from utils.angles import get_smallest_signed_angular_difference, normalize_angle_0_2pi

# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

class Arc:
    def __init__(self, start_x, start_y, start_angle, stop_angle):
        self.start_x = start_x
        self.start_y = start_y
        self.start_angle = start_angle
        self.stop_angle = stop_angle

class GuidanceGenerator:
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
            #alpha = get_smallest_signed_angular_difference(journey.start_angle, atan2(journey.goal_y - journey.start_y, journey.goal_x - journey.start_x))
            alpha = get_smallest_signed_angular_difference(wow_tag.angle, atan2(journey.goal_y - wow_tag.y, journey.goal_x - wow_tag.x))

            if abs(alpha) < pi/8:
                # Generate curve for this tag.
                points = self.controller.get_curve_points(journey_dict[id])
                curves.append(points)

            else:
                # Generate arc.  The following ridiculous normalizing and sign-flipping is all to
                # satisfy pygame's arc drawing function.
                start_angle = normalize_angle_0_2pi(-wow_tag.angle)
                stop_angle = normalize_angle_0_2pi(-wow_tag.angle + alpha)
                if start_angle < stop_angle:
                    arc = Arc(wow_tag.x, wow_tag.y, start_angle, stop_angle)
                else:
                    arc = Arc(wow_tag.x, wow_tag.y, stop_angle, start_angle)
                arcs.append(arc)

                # While we're in the mode of generating arcs, we're not using the journey's start angle 
                # or start position---those may also be growing "stale" as the robot shifts.  We'll
                # constantly update them here, but they'll remain fixed once the angle to the goal
                # goes under the threshold.
                journey.start_x = wow_tag.x
                journey.start_y = wow_tag.y
                journey.start_angle = wow_tag.angle

        return arcs, curves