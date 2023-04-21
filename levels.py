'''
A level determines the augmented goals produced by each robot.  These goals 
could be manual (i.e. from keyboard input) or autonomous, as determined by the
level.  A goal can be augmented with game_appearance and game_action, which are
labels that affect how the robot is displayed and 
'''

from abc import ABC, abstractmethod
from random import random
from math import atan2, cos, hypot, pi, sin

from utils.vector2d import Vector2D
from wow_tag import WowTag

class AbstractLevel(ABC):
    def __init__(self, value):
        self.value = value
        super().__init__()
    
    @abstractmethod
    def get_goals_and_sprites(self, manual_movement, tags):
        pass

class Sprite:
    def __init__(self, centre_vec, velocity_vec, inner_radius, outer_radius, colour, time_to_live=None):
        self.centre_vec = centre_vec
        self.velocity_vec = velocity_vec
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.colour = colour
        self.time_to_live = None

        self.terminate = False
    def update(self):
        '''Updates the sprite's position.'''
        self.centre_vec = self.centre_vec + self.velocity_vec
        if not self.time_to_live is None:
            if self.time_to_live > 0:
                self.time_to_live -= 1
            else:
                self.terminate = False

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
class TestLevel:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.goal_dict = {}

    def _set_random_goal(self, wow_tag):
        xbound = self.width / 5
        ybound = self.height / 5
        goal_x = xbound + random() * (self.width - 2*xbound)
        goal_y = ybound + random() * (self.height - 2*ybound)
        self.goal_dict[wow_tag.id] = (goal_x, goal_y)

    def get_goals_and_sprites(self, manual_movement, wow_tags):
        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                goal_tuple = get_player_movement_goal(manual_movement, wow_tag)
                if goal_tuple is None:
                    # Remove goal if previously set.
                    if wow_tag.id in self.goal_dict:
                        self.goal_dict.pop(wow_tag.id)
                else: 
                    self.goal_dict[wow_tag.id] = goal_tuple
                continue

            if not wow_tag.id in self.goal_dict:
                # This is the first time we're seeing this robot.  Choose a
                # random goal and store it in goal_dict and  
                self._set_random_goal(wow_tag)
            else:
                # This robot has a goal, if its reached it we'll set a new one.
                (x, y) = wow_tag.x, wow_tag.y
                (goal_x, goal_y) = self.goal_dict[wow_tag.id]
                if hypot(goal_x - x, goal_y - y) < 50:
                    self._set_random_goal(wow_tag)

        # This is not a game, so the list of sprites is empty.
        return self.goal_dict, []

'''
Robot 0 manually controlled and can fire sprites.
'''
class FirstGameLevel:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.goal_dict = {}
        self.enemy_state_dict = {}
        self.fire_timeout_dict = {}
        self.graveyard_list = []

        self.player_bullet_sprites = []
        self.enemy_bullet_sprites = []
        self.deco_sprites = []

    def _set_enemy_goal(self, wow_tag):
        '''An enemy will alternate between goals in the middle third of the
        environment and goals in the right third.'''
        x_bound = self.width / 5
        y_bound = self.height / 5

        id = wow_tag.id
        if id not in self.enemy_state_dict or self.enemy_state_dict[id] == "right_third":
            x_min = (2/3) * self.width 
            x_max = self.width - x_bound
            self.enemy_state_dict[id] = "middle_third"
        else:
            assert self.enemy_state_dict[id] == "middle_third"
            x_min = (1/3) * self.width 
            x_max = (2/3) * self.width
            self.enemy_state_dict[id] = "right_third"

        goal_x = x_min + random() * (x_max - x_min)
        goal_y = y_bound + random() * (self.height - 2*y_bound)
        self.goal_dict[wow_tag.id] = (goal_x, goal_y)

    def get_goals_and_sprites(self, manual_movement, wow_tags):
        for wow_tag in wow_tags:
            # Dead robots don't move.
            if wow_tag.id in self.graveyard_list:
                continue

            if wow_tag.id == 0:
                # BAD: How do we avoid duplicating this code block?
                goal_tuple = get_player_movement_goal(manual_movement, wow_tag)
                if goal_tuple is None:
                    # Remove goal if previously set.
                    if wow_tag.id in self.goal_dict:
                        self.goal_dict.pop(wow_tag.id)
                else: 
                    self.goal_dict[wow_tag.id] = goal_tuple

                if manual_movement == "fire":
                    if not wow_tag.id in self.fire_timeout_dict:
                        self.fire_timeout_dict[wow_tag.id] = 0
                    elif self.fire_timeout_dict[wow_tag.id] > 0:
                        continue

                    vx = 20 * cos(wow_tag.angle)
                    vy = 20 * sin(wow_tag.angle)
                    self.player_bullet_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(vx, vy), 5, 10, "green", time_to_live=100))
                    self.fire_timeout_dict[wow_tag.id] = 10

                continue

            # Enemy behaviour.  If they have a goal
            if not wow_tag.id in self.goal_dict:
                # This is the first time we're seeing this robot.  Choose a
                # random goal and store it in goal_dict and  
                self._set_enemy_goal(wow_tag)
            else:
                # This robot has a goal, if its reached it we'll set a new one.
                (x, y) = wow_tag.x, wow_tag.y
                (goal_x, goal_y) = self.goal_dict[wow_tag.id]
                if hypot(goal_x - x, goal_y - y) < 50:
                    self._set_enemy_goal(wow_tag)

        self.update_sprites(wow_tags)

        for id in self.fire_timeout_dict:
            if self.fire_timeout_dict[id] > 0:
                self.fire_timeout_dict[id] -= 1

        return self.goal_dict, self.player_bullet_sprites + self. enemy_bullet_sprites + self.deco_sprites

    def enemies_firing_at_player(self, player_tag, wow_tags):
        '''The enemies will fire at the player if angled to potentially hit it.'''

        if player_tag is None or 0 in self.graveyard_list:
            return
        player_vec = Vector2D(player_tag.x, player_tag.y)
        for wow_tag in wow_tags:
            if wow_tag.id == 0 or wow_tag.id in self.graveyard_list:
                continue
            enemy_vec = Vector2D(wow_tag.x, wow_tag.y)
            vec = player_vec - enemy_vec
            angle_to_player = atan2(vec.y, vec.x) - wow_tag.angle
            if abs(angle_to_player) < pi/8:
                if not wow_tag.id in self.fire_timeout_dict:
                    self.fire_timeout_dict[wow_tag.id] = 0
                elif self.fire_timeout_dict[wow_tag.id] > 0:
                    continue

                vx = 20 * cos(wow_tag.angle)
                vy = 20 * sin(wow_tag.angle)
                self.enemy_bullet_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(vx, vy), 5, 10, "blue", time_to_live=100))
                self.fire_timeout_dict[wow_tag.id] = 10

    def check_bullet_enemy_collisions(self, wow_tags):
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
                        self.goal_dict.pop(wow_tag.id)
                        self.deco_sprites.append(Sprite(Vector2D(wow_tag.x, wow_tag.y), Vector2D(0, 0), 50, 100, "red"))

    def check_bullet_player_collisions(self, player_tag, wow_tags):
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

    def update_sprites(self, wow_tags):
        for sprite in self.player_bullet_sprites + self.enemy_bullet_sprites:
            sprite.update()

        player_tag = None
        for wow_tag in wow_tags:
            if wow_tag.id == 0:
                player_tag = wow_tag
                break
        self.enemies_firing_at_player(player_tag, wow_tags)
        self.check_bullet_enemy_collisions(wow_tags)
        self.check_bullet_player_collisions(player_tag, wow_tags)

        self.player_bullet_sprites = [b for b in self.player_bullet_sprites if not b.terminate]
        self.enemy_bullet_sprites = [b for b in self.enemy_bullet_sprites if not b.terminate]
