'''
A controller creates a curve for a robot to follow.
'''

from abc import ABC, abstractmethod
from random import random
from math import atan2, cos, sin, pi
from utils.angles import normalize_angle_pm_pi, get_smallest_signed_angular_difference
from levels import Journey

from PathPlanning.DubinsPath.dubins_path_planner import plan_dubins_path

# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

'''
def compute_curves(controller, wow_tags, goal_dict):
    curves = []
    for wow_tag in wow_tags:
        if not wow_tag.id in goal_dict:
            continue
        points = controller.get_curve_points(Vector2(wow_tag.x, wow_tag.y), wow_tag.angle, goal_dict[wow_tag.id])
        curves.append(points)
    return curves
'''

class AbstractController(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    @abstractmethod
    def get_curve_points(self):
        pass

'''
Based on Smooth Controller 1 from 2018 notes for COMP 4766. 
'''
class SmoothController1(AbstractController):
    def __init__(self):
        self.delta_t = 0.001
        self.K_v = 1
        self.K_omega = 0.02

    def get_curve_points(self, journey):
        start_pos = Vector2(journey.start_x, journey.start_y)

        # Adjust the start position, by shifting it forwards to begin underneath the
        # robot's front sensor array.
        #ahead_distance = 20
        #start_pos += Vector2(ahead_distance * cos(journey.start_angle), ahead_distance * sin(journey.start_angle))

        goal_pos = Vector2(journey.goal_x, journey.goal_y)
        curve_vertex_list = [(int(journey.start_x), int(journey.start_y))]

        x = start_pos.x
        y = start_pos.y
        theta = journey.start_angle

        while (goal_pos - Vector2(x, y)).magnitude() > 5:

            # Get the goal position in the robot's ref. frame.
            goal_rob_ref = (goal_pos - Vector2(x, y)).rotate_rad(-theta)

            # Smooth controller 1 (from old 4766 notes) generates the following
            # forward and angular speeds
            v = self.K_v * abs(goal_rob_ref.x)
            omega = self.K_omega * goal_rob_ref.y

            # Velocity in the global frame.
            x_dot = v * cos(theta)
            y_dot = v * sin(theta)

            x += x_dot * self.delta_t
            y += y_dot * self.delta_t
            theta += omega * self.delta_t

            curve_vertex_list.append((int(x), int(y)))

        return curve_vertex_list

'''
Dubins model:
https://atsushisakai.github.io/PythonRobotics/
'''
class DubinsController(AbstractController):
    def __init__(self):
        pass

    def get_curve_points(self, journey):

        start_x = journey.start_x
        start_y = journey.start_y
        start_yaw = journey.start_angle
        end_x = journey.goal_x
        end_y = journey.goal_y

        # BAD: Journeys don't have a goal angle.  So what is a sensible value to enter here???
        end_yaw = journey.start_angle

        curvature = 1/50.0
        path_x, path_y, path_yaw, mode, _ = plan_dubins_path(
                start_x, start_y, start_yaw, end_x, end_y, end_yaw, curvature)

        curve_vertex_list = []
        for i in range(len(path_x)):
            x = path_x[i]
            y = path_y[i]
            curve_vertex_list.append((int(x), int(y)))

        return curve_vertex_list

'''
A simplified version of Dubins path planning where the movement begins with a circular arc,
followed by a straight line segment towards the goal.
'''
class DubinsLightController(AbstractController):
    def __init__(self):
        self.turning_radius = 75
        self.arrival_threshold = self.turning_radius + 25
        self.bearing_threshold = 0.2
        self.delta_angle = 0.05

        self.smooth_controller = SmoothController1()

    def get_curve_points(self, journey):
        start_vec = Vector2(journey.start_x, journey.start_y)
        goal_vec = Vector2(journey.goal_x, journey.goal_y)
        curve_vertex_list = []#(int(journey.start_x), int(journey.start_y))]

        to_goal_vec = Vector2(journey.goal_x - journey.start_x, journey.goal_y - journey.start_y)

        if to_goal_vec.magnitude() <= self.arrival_threshold:
            return []

        # Bearing of goal relative to journey start.
        bearing = atan2(to_goal_vec.y, to_goal_vec.x) - journey.start_angle
        bearing = normalize_angle_pm_pi(bearing)
        #bearing = get_smallest_signed_angular_difference(journey.start_angle, atan2(journey.goal_y - journey.start_y, journey.goal_x - journey.start_x))

        # Depending on the sign of bearing, the centre for the arc will be left/right of the robot.
        turn_centre_angle = pi/2
        delta_angle = self.delta_angle
        if bearing < 0:
            turn_centre_angle *= -1
            delta_angle *= -1
        turn_centre_vec = start_vec + Vector2(self.turning_radius, 0).rotate_rad(journey.start_angle + turn_centre_angle)

        vec = start_vec
        angle_travelled = 0
        i = 0
        while i < 1000 and abs(bearing) > self.bearing_threshold:
            vec = turn_centre_vec + (start_vec - turn_centre_vec).rotate_rad(angle_travelled)
            angle_travelled += delta_angle
            i += 1

            curve_vertex_list.append((int(vec.x), int(vec.y)))

            to_goal_vec = Vector2(journey.goal_x - vec.x, journey.goal_y - vec.y)
            bearing = atan2(to_goal_vec.y, to_goal_vec.x) - journey.start_angle - angle_travelled
            bearing = normalize_angle_pm_pi(bearing)
            #bearing = get_smallest_signed_angular_difference(journey.start_angle, atan2(journey.goal_y - vec.y, journey.goal_x - vec.x) + angle_travelled)
        assert i < 1000, "Maximum steps in loop exceeded."

        remaining_journey = Journey(vec.x, vec.y, journey.start_angle + angle_travelled, journey.goal_x, journey.goal_y)
        smooth_list = self.smooth_controller.get_curve_points(remaining_journey)

        return curve_vertex_list + smooth_list
