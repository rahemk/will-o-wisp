from levels import AbstractLevel
'''
Provides a connection to the SwarmJS simulator, which will serve as a source of goals 
for each robot.
'''
 
class SwarmJSLevel(AbstractLevel):
 
    def __init__(self, ADD_ANY_NECESSARY_PARAMS_LIKE_WIDTH_OR_HEIGHT):
        # CONNECT TO SWARMJS
        pass
    
    def get_journey_dict(self, manual_movement, wow_tags):

        # REPLACE THE FOLLOWING WITH DATA FROM SWARMJS.

        # Should return a dictionary where the keys are integer id's (the id of each tag)
        # and the values are Journey objects which contain the robot's start
        # point and angle, as well as goal:
        #   (start_x, start_y, start_angle, goal_x, goal_y):
        # Ignore 'manual_movement'.
        self.journey_dict = {}

        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                self.journey_dict[wow_tag.id] = (wow_tag.x, wow_tag.y, wow_tag.angle, 500, 100)
            elif wow_tag.id == 1:
                self.journey_dict[wow_tag.id] = (wow_tag.x, wow_tag.y, wow_tag.angle, 200, 400)

        return self.journey_dict