# This is a rather unneccessary dependency, but I like pygame's vector class.
from pygame.math import Vector2

class ControlImageGenerator:
    def __init__(self, controller):
        self.controller = controller

    def generate(self, wow_tags, journey_dict):
        curves = []
        for wow_tag in wow_tags:
            id = wow_tag.id
            if not id in journey_dict:
                continue
            points = self.controller.get_curve_points(journey_dict[id])
            curves.append(points)
        return curves