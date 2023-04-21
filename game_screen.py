import os
import pygame as pg
from pygame.math import Vector2
from math import cos, pi, sin
from random import random

POSE_RADIUS = 65

class GameScreen:
    def __init__(self, width, height):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "1920,0"
        pg.init()
        self.screen = pg.display.set_mode((width, height), flags=pg.SCALED)
        #pg.display.toggle_fullscreen()
        self.terminate = False

        self.debug_level = 1
        self.MAX_DEBUG_LEVEL = 2
        self.font = pg.freetype.SysFont('arial', 18)
        self.big_font = pg.freetype.SysFont('arial', 36)

    def handle_events(self):
        self.movement = ""

        # Handle events, including key-presses that occur when the key is
        # pressend down, but not subsequently.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    if self.debug_level < self.MAX_DEBUG_LEVEL:
                        self.debug_level += 1
                    else:
                        self.debug_level = 0

        # Handle key presses (key could be held down).
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] or keys[pg.K_q]:
            self.terminate = True
        if keys[pg.K_UP]:
            self.movement = "forward"
        if keys[pg.K_LEFT]:
            self.movement = "left"
        if keys[pg.K_RIGHT]:
            self.movement = "right"
        if keys[pg.K_SPACE]:
            self.movement = "fire"

    def get_movement(self):
        return self.movement

    def update(self, wow_tags, control_curves, sprites):
        # Fill the screen to wipe away anything from last frame
        self.screen.fill("black")

        if self.debug_level > 0:
            for wow_tag in wow_tags:
                centre = Vector2(wow_tag.x, wow_tag.y)
                unit_vector = Vector2(cos(wow_tag.angle), sin(wow_tag.angle))

                pg.draw.circle(self.screen, "purple", centre, POSE_RADIUS, width=2)
                pg.draw.line(self.screen, "purple", centre + 0.7 * POSE_RADIUS * unit_vector, centre + POSE_RADIUS * unit_vector, width=3)

                if self.debug_level == 1:
                    text_surface, rect = self.font.render(str(wow_tag.id), "purple")
                elif self.debug_level == 2:
                    newline = '\n'
                    text_surface, rect = self.font.render(f"id: {wow_tag.id}{newline}pos: {wow_tag.x, wow_tag.y}{newline}angle: {int(wow_tag.angle*180/pi)}", "purple")

                text_position = centre + 1.2 * POSE_RADIUS * unit_vector - 0.5 * Vector2(rect.width, rect.height)
                self.screen.blit(text_surface, text_position)

        for sprite in sprites:
            if hasattr(sprite, 'text'):
                text_surface, rect = self.big_font.render(sprite.text, sprite.colour)
                text_position = Vector2(sprite.centre_vec.x, sprite.centre_vec.y) - 0.5 * Vector2(rect.width, rect.height)
                self.screen.blit(text_surface, text_position)
            else:
                n_points = 10
                points = []
                for i in range(n_points):
                    angle = 2*pi * i / (n_points - 1)
                    radius = sprite.inner_radius + random() * (sprite.outer_radius - sprite.inner_radius)
                    points.append(Vector2(sprite.centre_vec.x + radius * cos(angle), \
                                          sprite.centre_vec.y + radius * sin(angle)))
                pg.draw.polygon(self.screen, sprite.colour, points)
                # Fill the centre with black, so in the case of flames on a dying
                # robot, it doesn't trigger movement.
                pg.draw.circle(self.screen, "black", Vector2(sprite.centre_vec.x, sprite.centre_vec.y), sprite.inner_radius)

        for curve in control_curves:
            pg.draw.lines(self.screen, "white", False, curve, 20)

        # flip() the display to put your work on screen
        pg.display.flip()

        if self.terminate:
            self.close()

    def close(self):
        pg.display.quit()
        pg.quit()