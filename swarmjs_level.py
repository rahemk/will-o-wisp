from levels import AbstractLevel
'''
Provides a connection to the SwarmJS simulator, which will serve as a source of goals 
for each robot.
'''
 
class SwarmJSLevel(AbstractLevel):
 
    def __init__(self, ADD_ANY_NECESSARY_PARAMS_LIKE_WIDTH_OR_HEIGHT):
        # CONNECT TO SWARMJS
        pass
    
    def get_goals(self, manual_movement, wow_tags):

        # REPLACE THE FOLLOWING WITH DATA FROM SWARMJS.

        # Should return a dictionary where the keys are integer id's (the id of each tag)
        # and the values are the (goal_x, goal_y) positions.
        # Ignore 'manual_movement'.
        self.robot_goals = {}

        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                self.robot_goals[wow_tag.id] = (500, 100)
            elif wow_tag.id == 1:
                self.robot_goals[wow_tag.id] = (200, 400)

        return self.robot_goals