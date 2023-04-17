'''
A level manages the movements produced by each robot.  These movements could
be manual (i.e. from keyboard input) or autonomous. 
'''

from abc import ABC, abstractmethod
from random import random
from math import cos, sin
 
class AbstractLevel(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    @abstractmethod
    def get_movements(self, manual_movement, tags):
        pass

'''
All robots manually controlled.
'''
class JustManualLevel:
    def get_movements(self, manual_movement, tags):
        movement_dict = {}
        for tag in tags:
            movement_dict[tag['id']] = manual_movement
        return movement_dict

'''
Robot 0 manually controlled.  All others are given random goals upon entry.
'''
class TestLevel:

    def __init__(self, width, height):
        self.robot_states = {}

    def get_movements(self, manual_movement, tags):
        movement_dict = {}

        for tag in tags:
            if tag['id'] == 0:
                movement_dict[0] = manual_movement
                continue

            if not tag['id'] in self.robot_states:
                # This is the first time we're seeing this robot.  Choose a
                # goal that's direct ahead of this robot.
                goal_distance = 100
                goal_x = tag['x'] + goal_distance * cos(tag['angle'])
                goal_x = tag['x'] + goal_distance * sin(tag['angle'])


        return movement_dict