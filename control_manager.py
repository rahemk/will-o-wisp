'''
Manages which tags correspond to autonomous robots and which are manually
controlled.
'''
class ControlManager:
    def __init__(self):
        pass
    
    def get_movements(self, manual_movement, tags):

        movement_dict = {}

        for tag in tags:
            movement_dict[tag['id']] = manual_movement

        return movement_dict