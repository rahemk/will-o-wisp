'''
A controller creates a curve for a robot to follow.
'''

from abc import ABC, abstractmethod
from random import random
from math import atan2, cos, sin

# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2
 
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
        self.delta_t = 0.01
        self.K_v = 1
        self.K_omega = 0.025

    def get_curve_points(self, start_pos, start_angle, goal_pos):
        curve_vertex_list = [start_pos]

        x = start_pos.x
        y = start_pos.y
        theta = start_angle

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

            curve_vertex_list.append(Vector2(x, y))

        return curve_vertex_list