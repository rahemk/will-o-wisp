'''
A level manages the movements produced by each robot.  These movements could
be manual (i.e. from keyboard input) or autonomous. 
'''

from abc import ABC, abstractmethod
from random import random
from math import cos, hypot, pi, sin
 
class AbstractLevel(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    @abstractmethod
    def get_movements(self, manual_movement, tags):
        pass

    @abstractmethod
    def get_goals(self, manual_movement, tags):
        pass

'''
All robots manually controlled.
'''
class JustManualLevel(AbstractLevel):
    def get_movements(self, manual_movement, tags):
        movement_dict = {}
        for tag in tags:
            movement_dict[tag['id']] = manual_movement
        return movement_dict

    def get_goals(self, manual_movement, tags):
        # The robots have no goals.  That is why they fail.
        return {}

'''
Robot 0 manually controlled.  All others are given random goals upon entry.
'''
class TestLevel:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.robot_goals = {}

    def _set_random_goal(self, tag):
        goal_x = random() * self.width
        goal_y = random() * self.height
        self.robot_goals[tag['id']] = (goal_x, goal_y)

    def get_movements(self, manual_movement, tags):
        return {}

    def get_goals(self, manual_movement, tags):
        for tag in tags:
#            if tag['id'] == 0:
            if tag['id'] == -1:
                if manual_movement == "forward":
                    delta_angle = 0
                elif manual_movement == "left":
                    delta_angle = -pi/4
                elif manual_movement == "right":
                    delta_angle = pi/4
                elif manual_movement == "":
                    # Remove goal if previously set.
                    if tag['id'] in self.robot_goals:
                        self.robot_goals.pop(tag['id'])
                    continue
                else:
                    assert False, f'Invalid movement: {manual_movement}'

                d = 100
                goal_x = tag['x'] + d * cos(tag['angle'] + delta_angle)
                goal_y = tag['y'] + d * sin(tag['angle'] + delta_angle)

                self.robot_goals[tag['id']] = (goal_x, goal_y)
                continue

            if tag['id'] == 0:
                if not tag['id'] in self.robot_goals:
                    # This is the first time we're seeing this robot.  Choose a
                    # random goal and store it in robot_goals and  
                    self._set_random_goal(tag)
                else:
                    # This robot has a goal, if its reached it we'll set a new one.
                    (x, y) = tag['x'], tag['y']
                    (goal_x, goal_y) = self.robot_goals[tag['id']]
                    if hypot(goal_x - x, goal_y - y) < 50:
                        self._set_random_goal(tag)

        return self.robot_goals

class MohLevel(AbstractLevel):
 
    def __init__(self, value):
        # CONNECT TO SWARMJS
        pass
    
    @abstractmethod
    def get_movements(self, manual_movement, tags):
        pass

    @abstractmethod
    def get_goals(self, manual_movement, tags):
        # INSERT CODE
        pass
