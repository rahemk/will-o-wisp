'''
A level determines the goals produced by each robot.  These goals could
be manual (i.e. from keyboard input) or autonomous, as determined by the level. 
'''

from abc import ABC, abstractmethod
from random import random
from math import cos, hypot, pi, sin
 
class AbstractLevel(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    @abstractmethod
    def get_goals(self, manual_movement, tags):
        pass

'''
Robot 0 manually controlled.  All others are given random goals upon entry.
'''
class TestLevel:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.robot_goals = {}

    def _set_random_goal(self, wow_tag):
        goal_x = random() * self.width
        goal_y = random() * self.height
        self.robot_goals[wow_tag.id] = (goal_x, goal_y)

    def get_goals(self, manual_movement, wow_tags):
        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                if manual_movement == "forward":
                    delta_angle = 0
                elif manual_movement == "left":
                    delta_angle = -pi/4
                elif manual_movement == "right":
                    delta_angle = pi/4
                elif manual_movement == "":
                    # Remove goal if previously set.
                    if wow_tag.id in self.robot_goals:
                        self.robot_goals.pop(wow_tag.id)
                    continue
                else:
                    assert False, f'Invalid movement: {manual_movement}'

                d = 100
                goal_x = wow_tag.x + d * cos(wow_tag.angle + delta_angle)
                goal_y = wow_tag.y + d * sin(wow_tag.angle + delta_angle)

                self.robot_goals[wow_tag.id] = (goal_x, goal_y)
                continue

            if not wow_tag.id in self.robot_goals:
                # This is the first time we're seeing this robot.  Choose a
                # random goal and store it in robot_goals and  
                self._set_random_goal(wow_tag)
            else:
                # This robot has a goal, if its reached it we'll set a new one.
                (x, y) = wow_tag.x, wow_tag.y
                (goal_x, goal_y) = self.robot_goals[wow_tag.id]
                if hypot(goal_x - x, goal_y - y) < 50:
                    self._set_random_goal(wow_tag)

        return self.robot_goals

class MohLevel(AbstractLevel):
 
    def __init__(self, value):
        # CONNECT TO SWARMJS
        pass
    
    @abstractmethod
    def get_goals(self, manual_movement, wow_tags):
        # INSERT CODE
        pass
