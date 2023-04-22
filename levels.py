'''
A level determines the journeys required for each robot.  These goals 
could be manual (i.e. from keyboard input) or autonomous, as determined by the
level.  A goal can be augmented with game_appearance and game_action, which are
labels that affect how the robot is displayed and 
'''

from abc import ABC, abstractmethod
from random import random
from math import atan2, cos, hypot, pi, sin

from utils.angles import get_smallest_angular_difference
from utils.vector2d import Vector2D
from wow_tag import WowTag

BULLET_TIME_TO_LIVE = 25

class AbstractLevel(ABC):
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    # Updates the level and returns a dictionary of journey objects which
    # specify each robot's "intentions".  This dictionary is keyed by WowTag
    # id's (which in turn come from AprilTag id's).
    @abstractmethod
    def get_journey_dict(self, manual_movement, wow_tags):
        pass

    # A level might also have sprites---graphical elements that are passed
    # on to display.  This is optional, so derived classes can just use this
    # one if they don't have any sprites to show.
    def get_sprites(self):
        return []

class Journey:
    def __init__(self, start_x, start_y, start_angle, goal_x, goal_y):
        self.start_x = start_x
        self.start_y = start_y
        self.start_angle = start_angle
        self.goal_x = goal_x
        self.goal_y = goal_y

class Sprite:
    def __init__(self, centre_vec, velocity_vec, inner_radius, outer_radius, colour, time_to_live=None):
        self.centre_vec = centre_vec
        self.velocity_vec = velocity_vec
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.colour = colour
        self.time_to_live = time_to_live

        self.terminate = False
    def update(self):
        '''Updates the sprite's position.'''
        self.centre_vec = self.centre_vec + self.velocity_vec
        if not self.time_to_live is None:
            if self.time_to_live > 0:
                self.time_to_live -= 1
            else:
                self.terminate = True

def get_player_movement_goal(manual_movement, wow_tag):
    if manual_movement == "forward":
        delta_angle = 0
    elif manual_movement == "left":
        delta_angle = -pi/4
    elif manual_movement == "right":
        delta_angle = pi/4
    else:# manual_movement == "":
        return None

    d = 100
    goal_x = wow_tag.x + d * cos(wow_tag.angle + delta_angle)
    goal_y = wow_tag.y + d * sin(wow_tag.angle + delta_angle)

    return goal_x, goal_y


'''
Robot 0 manually controlled.  All others are given random goals upon entry.  New
random goals are given once they get close to their current goal.
'''
class TestLevel(AbstractLevel):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.journey_dict = {}

    def _set_random_goal(self, wow_tag):
        xbound = self.width / 5
        ybound = self.height / 5
        goal_x = xbound + random() * (self.width - 2*xbound)
        goal_y = ybound + random() * (self.height - 2*ybound)
        self.journey_dict[wow_tag.id] = Journey(wow_tag.x, wow_tag.y, wow_tag.angle, goal_x, goal_y)

    def get_journey_dict(self, manual_movement, wow_tags):
        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                goal_tuple = get_player_movement_goal(manual_movement, wow_tag)
                if goal_tuple is None:
                    # Remove journey if previously set.
                    if wow_tag.id in self.journey_dict:
                        self.journey_dict.pop(wow_tag.id)
                else: 
                    self.journey_dict[wow_tag.id] = Journey(wow_tag.x, wow_tag.y, wow_tag.angle, goal_tuple[0], goal_tuple[1])
                continue

            if not wow_tag.id in self.journey_dict:
                # This is the first time we're seeing this robot.  Choose a
                # random goal and store it in journey_dict.
                self._set_random_goal(wow_tag)
            else:
                # This robot has a goal, if its reached it we'll set a new one.
                (x, y) = wow_tag.x, wow_tag.y
                journey = self.journey_dict[wow_tag.id]
                if hypot(journey.goal_x - x, journey.goal_y - y) < 50:
                    self._set_random_goal(wow_tag)

        return self.journey_dict

    def get_sprites(self):
        sprites = []
        for id in self.journey_dict:
            journey = self.journey_dict[id]
            sprites.append(Sprite(Vector2D(journey.goal_x, journey.goal_y), Vector2D(0, 0), 1, 10, "purple"))
            sprites.append(Sprite(Vector2D(journey.goal_x, journey.goal_y), Vector2D(0, 0), 5, 16, "green"))
        return sprites

'''
Robot 0 manually controlled and can fire sprites.
'''
class FirstGameLevel(AbstractLevel):

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.journey_dict = {}
        self.enemy_state_dict = {}
        self.fire_timeout_dict = {}
        self.graveyard_list = []

        self.player_bullet_sprites = []
        self.enemy_bullet_sprites = []
        self.deco_sprites = []

    def _set_enemy_goal(self, wow_tag, wow_tags):
        '''An enemy will alternate between goals in the middle third of the
        environment and goals in the right third.'''

        # Buffer with the outside boundary of the environment.  i.e. don't choose
        # a goal position closer than this.
        boundary_buffer = self.height / 5

        # Buffer between the horizontal bands.  These bands (described below)
        # are intended to keep enemy robots apart.
        band_buffer = 50
        
        # These width and height 
        width = self.width - 2*boundary_buffer
        height = self.height - 2*boundary_buffer

        # Also, to reduce the chances of collision we'll split the vertical
        # dimension into bands where each robot tries to stay within its closest
        # band.

        enemy_tags = [tag for tag in wow_tags if tag.id != 0]
        n_enemies = len(enemy_tags)
        #print(f"n_enemies: {n_enemies}")
        tags_sorted_by_y = sorted(enemy_tags, key=lambda tag: tag.y)
        i = tags_sorted_by_y.index(wow_tag)
        assert i != -1
        y_min = boundary_buffer + (i/n_enemies) * height + band_buffer
        y_max = boundary_buffer + ((i+1)/n_enemies) * height - band_buffer
        #print(f"min, max: {y_min}, {y_max}")

        id = wow_tag.id
        if id not in self.enemy_state_dict or self.enemy_state_dict[id] == "right_third":
            x_min = (2/3) * self.width 
            x_max = self.width - boundary_buffer
            self.enemy_state_dict[id] = "middle_third"
        else:
            assert self.enemy_state_dict[id] == "middle_third"
            x_min = (1/3) * self.width 
            x_max = (2/3) * self.width
            self.enemy_state_dict[id] = "right_third"

        goal_x = x_min + random() * (x_max - x_min)
        goal_y = y_min + random() * (y_max - y_min)
        self.journey_dict[wow_tag.id] = Journey(wow_tag.x, wow_tag.y, wow_tag.angle, goal_x, goal_y)

    def get_journey_dict(self, manual_movement, wow_tags):
        for wow_tag in wow_tags:
            # Dead robots don't move.
            if wow_tag.id in self.graveyard_list:
                continue

            if wow_tag.id == 0:
                # BAD: How do we avoid duplicating this code block?
                goal_tuple = get_player_movement_goal(manual_movement, wow_tag)
                if goal_tuple is None:
                    # Remove goal if previously set.
                    if wow_tag.id in self.journey_dict:
                        self.journey_dict.pop(wow_tag.id)
                else: 
                    self.journey_dict[wow_tag.id] = Journey(wow_tag.x, wow_tag.y, wow_tag.angle, goal_tuple[0], goal_tuple[1])

                if manual_movement == "fire":
                    if not wow_tag.id in self.fire_timeout_dict:
                        self.fire_timeout_dict[wow_tag.id] = 0
                    elif self.fire_timeout_dict[wow_tag.id] > 0:
                        continue

                    vx = 20 * cos(wow_tag.angle)
                    vy = 20 * sin(wow_tag.angle)
                    self.player_bullet_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(vx, vy), 5, 10, "green", time_to_live=BULLET_TIME_TO_LIVE))
                    self.fire_timeout_dict[wow_tag.id] = 10

                continue

            # Enemy behaviour.  If they have a goal
            if not wow_tag.id in self.journey_dict:
                # This is the first time we're seeing this robot.  Choose a
                # random goal and store it in journey_dict and  
                self._set_enemy_goal(wow_tag, wow_tags)
            else:
                # This robot has a goal, if its reached it we'll set a new one.
                (x, y) = wow_tag.x, wow_tag.y
                journey = self.journey_dict[wow_tag.id]
                if hypot(journey.goal_x - x, journey.goal_y - y) < 50:
                    self._set_enemy_goal(wow_tag, wow_tags)

        self._update_sprites(wow_tags)

        for id in self.fire_timeout_dict:
            if self.fire_timeout_dict[id] > 0:
                self.fire_timeout_dict[id] -= 1

        return self.journey_dict

    def get_sprites(self):

        #goal_sprites = []
        #for id in self.journey_dict:
        #    journey = self.journey_dict[id]
        #    goal_sprites.append(Sprite(Vector2D(journey.goal_x, journey.goal_y), Vector2D(0, 0), 1, 10, "purple"))
        #return self.player_bullet_sprites + self. enemy_bullet_sprites + self.deco_sprites + goal_sprites

        return self.player_bullet_sprites + self. enemy_bullet_sprites + self.deco_sprites

    def _enemies_firing_at_player(self, player_tag, wow_tags):
        '''The enemies will fire at the player if angled to potentially hit it.'''

        if player_tag is None or 0 in self.graveyard_list:
            return
        player_vec = Vector2D(player_tag.x, player_tag.y)
        for wow_tag in wow_tags:
            if wow_tag.id == 0 or wow_tag.id in self.graveyard_list:
                continue
            enemy_vec = Vector2D(wow_tag.x, wow_tag.y)
            vec = player_vec - enemy_vec
            angle_to_player = get_smallest_angular_difference(atan2(vec.y, vec.x), wow_tag.angle)
            assert angle_to_player >= 0
            if angle_to_player < pi/8:
                if not wow_tag.id in self.fire_timeout_dict:
                    self.fire_timeout_dict[wow_tag.id] = 0
                elif self.fire_timeout_dict[wow_tag.id] > 0:
                    continue

                vx = 20 * cos(wow_tag.angle)
                vy = 20 * sin(wow_tag.angle)
                self.enemy_bullet_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(vx, vy), 5, 10, "blue", time_to_live=BULLET_TIME_TO_LIVE))
                self.fire_timeout_dict[wow_tag.id] = 10

    def _check_bullet_enemy_collisions(self, wow_tags):
        '''Check for collision between the player's bullet sprites and enemy tags.'''

        for b in self.player_bullet_sprites:
            for wow_tag in wow_tags:
                if wow_tag.id == 0:
                    continue
                tag_pos = Vector2D(wow_tag.x, wow_tag.y)
                if Vector2D.Distance(tag_pos, b.centre_vec) < 50:
                    b.terminate = True
                    if not wow_tag.id in self.graveyard_list:
                        self.graveyard_list.append(wow_tag.id)
                        self.journey_dict.pop(wow_tag.id)
                        self.deco_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(0, 0), 50, 100, "red"))

    def _check_bullet_player_collisions(self, player_tag, wow_tags):
        '''Check for collision between the enemies' bullet sprites and the player.'''
        if player_tag is None:
            return
        for b in self.enemy_bullet_sprites:
            player_pos = Vector2D(player_tag.x, player_tag.y)
            if Vector2D.Distance(player_pos, b.centre_vec) < 50:
                b.terminate = True
                if player_tag.id not in self.graveyard_list:# Could just say 0, but maybe this will change.
                    self.graveyard_list.append(player_tag.id) 
                    self.deco_sprites.append(Sprite(Vector2D(player_tag.x, player_tag.y), Vector2D(0, 0), 50, 100, "red"))
                    game_over_sprite = Sprite(Vector2D(self.width/2, self.height/2), Vector2D(0, 0), 0, 0, "white")
                    game_over_sprite.text = "Game Over!"
                    self.deco_sprites.append(game_over_sprite)

    def _update_sprites(self, wow_tags):
        for sprite in self.player_bullet_sprites + self.enemy_bullet_sprites:
            sprite.update()

        player_tag = None
        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                player_tag = wow_tag
                break
        self._enemies_firing_at_player(player_tag, wow_tags)
        self._check_bullet_enemy_collisions(wow_tags)
        self._check_bullet_player_collisions(player_tag, wow_tags)

        self.player_bullet_sprites = [b for b in self.player_bullet_sprites if not b.terminate]
        self.enemy_bullet_sprites = [b for b in self.enemy_bullet_sprites if not b.terminate]
