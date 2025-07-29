import os
import pygame as pg
from pygame.math import Vector2
from math import cos, pi, sin
from random import random
from levels import FirstGameLevel, VersusGameLevel, PLAYER_1_TAG_ID, RotatedTextSprite


ARC_RADIUS = 50
ARC_THICKNESS = 30

POSE_RADIUS = 65

class GameScreen:
    def __init__(self, width, height, fullscreen):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "1920,0"
        pg.init()
        self.screen = pg.display.set_mode((width, height), flags=pg.SCALED)
        if fullscreen:
            pg.display.toggle_fullscreen()
        self.terminate = False

        self.debug_level = 1
        self.MAX_DEBUG_LEVEL = 2
        self.font = pg.freetype.SysFont('arial', 18)
        self.big_font = pg.freetype.SysFont('arial', 36)

        self.screenshot_index = 0
        self.do_screenshot = False

    def handle_events(self):
        self.movement = {"p1": "", "p2": ""}
        self.restart = False

        # Handle events, including key-presses that occur when the key is
        # pressed down, but not subsequently.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.terminate = True
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    self.restart = True
                #if event.key == pg.K_d:
                #     if self.debug_level < self.MAX_DEBUG_LEVEL:
                #         self.debug_level += 1
                #     else:
                #         self.debug_level = 0
                # if event.key == pg.K_s:
                #     self.do_screenshot = True

        # Handle key presses (key could be held down).
        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE] or keys[pg.K_q]:
            self.terminate = True
        if keys[pg.K_UP]:
            self.movement["p1"] = "forward"
        if keys[pg.K_LEFT]:
            self.movement["p1"] = "left"
        if keys[pg.K_RIGHT]:
            self.movement["p1"] = "right"
        if keys[pg.K_SPACE]:
            self.movement["p1"] = "fire"

        if keys[pg.K_w]:
            self.movement["p2"] = "forward"
        if keys[pg.K_a]:
            self.movement["p2"] = "left"
        if keys[pg.K_d]:
            self.movement["p2"] = "right"
        if keys[pg.K_RETURN]:
            self.movement["p2"] = "fire"

    def get_movement_for_player1(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]: return "forward"
        if keys[pg.K_LEFT]: return "left"
        if keys[pg.K_RIGHT]: return "right"
        if keys[pg.K_SPACE]: return "fire"
        return ""

    def get_movement_for_player2(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_w]: return "forward"
        if keys[pg.K_a]: return "left"
        if keys[pg.K_d]: return "right"
        if keys[pg.K_RETURN]: return "fire"
        return ""

    def get_do_screenshot(self):
        return self.do_screenshot, self.screenshot_index
    
    def get_restart(self):
        return self.restart

    def update(self, wow_tags, control_arcs, control_curves, sprites, background_image=None, game_over=False, level=None):
        if background_image is not None:
            pg.surfarray.blit_array(self.screen, background_image)
        else:
            # Fill the screen to wipe away anything from last frame
            self.screen.fill("black")

        if self.debug_level > 0:
            for wow_tag in wow_tags:
                centre = Vector2(wow_tag.x, wow_tag.y)
                unit_vector = Vector2(cos(wow_tag.angle), sin(wow_tag.angle))

                if isinstance(level, VersusGameLevel):
                    shield_count = level.shields.get(wow_tag.id, 0)
                    if shield_count > 0 and wow_tag.id not in level.graveyard_list:
                        for i in range(shield_count):
                            outer_radius = POSE_RADIUS + 10 + (shield_count - i - 1) * 6
                            inner_radius = outer_radius - 2  
                            pg.draw.circle(self.screen, (0, 255, 255), centre, outer_radius, width=2)
                            pg.draw.circle(self.screen, (0, 0, 0), centre, inner_radius)
                    
                    if wow_tag.id == PLAYER_1_TAG_ID:
                        color = "blue"
                    else:
                        color = "red"            
                elif isinstance(level, FirstGameLevel):
                    if wow_tag.id == PLAYER_1_TAG_ID:
                        color = "blue"
                    else:
                        color = "purple"  
                else:
                    color = "purple"

                pg.draw.circle(self.screen, color, centre, POSE_RADIUS, width=2)
                pg.draw.line(self.screen, color, centre + 0.7 * POSE_RADIUS * unit_vector, centre + POSE_RADIUS * unit_vector, width=3)

                if self.debug_level == 1:
                    text_surface, rect = self.font.render(str(wow_tag.id), color)
                elif self.debug_level == 2:
                    newline = '\n'
                    text_surface, rect = self.font.render(f"id: {wow_tag.id}{newline}pos: {wow_tag.x, wow_tag.y}{newline}angle: {int(wow_tag.angle*180/pi)}", "purple")

                text_position = centre + 1.2 * POSE_RADIUS * unit_vector - 0.5 * Vector2(rect.width, rect.height)
                self.screen.blit(text_surface, text_position)

        for sprite in sprites:
            if isinstance(sprite, RotatedTextSprite):
                font = pg.freetype.SysFont("arial", sprite.font_size, bold=True)
                text_surface, _ = font.render(sprite.text, sprite.colour)
                text_surface = pg.transform.rotate(text_surface, sprite.angle)
                rect = text_surface.get_rect(center=(sprite.centre_vec.x, sprite.centre_vec.y))
                self.screen.blit(text_surface, rect)
                continue
            if hasattr(sprite, "text"):
                    font_size = getattr(sprite, "font_size", None)
                    if font_size is None:
                        font_size = 36
                    font = pg.freetype.SysFont("arial", font_size, bold=True)
                    text_surface, rect = font.render(sprite.text, sprite.colour, size=font_size)
                    text_pos = Vector2(sprite.centre_vec.x, sprite.centre_vec.y) - 0.5 * Vector2(rect.width, rect.height)

                    self.screen.blit(text_surface, text_pos)
            else:
                if sprite.flicker:
                    n_points = 10
                    points = []
                    for i in range(n_points):
                        angle = 2*pi * i / n_points
                        radius = sprite.inner_radius + random() * (sprite.outer_radius - sprite.inner_radius)
                        points.append(Vector2(sprite.centre_vec.x + radius * cos(angle), \
                                            sprite.centre_vec.y + radius * sin(angle)))
                    pg.draw.polygon(self.screen, sprite.colour, points)
                else:
                    pg.draw.circle(self.screen, sprite.colour, Vector2(sprite.centre_vec.x, sprite.centre_vec.y), sprite.outer_radius)

                # Fill the centre with black, so in the case of flames on a dying
                # robot, it doesn't trigger movement.
                pg.draw.circle(self.screen, "black", Vector2(sprite.centre_vec.x, sprite.centre_vec.y), sprite.inner_radius)

        for arc in control_arcs:
            # Setting a non-zero width in the arc function leaves holes.  We fill these in
            # by drawing it multiple times at slightly shifted positions.
            rect = pg.Rect(arc.start_x - ARC_RADIUS, arc.start_y - ARC_RADIUS, 2*ARC_RADIUS, 2*ARC_RADIUS)
            pg.draw.arc(self.screen, "white", rect, arc.start_angle, arc.stop_angle, width=ARC_THICKNESS)
            pg.draw.arc(self.screen, "white", rect.move(0,1), arc.start_angle, arc.stop_angle, width=ARC_THICKNESS)
            pg.draw.arc(self.screen, "white", rect.move(1,0), arc.start_angle, arc.stop_angle, width=ARC_THICKNESS)
            pg.draw.arc(self.screen, "white", rect.move(1,1), arc.start_angle, arc.stop_angle, width=ARC_THICKNESS)

        for curve in control_curves:
            pg.draw.lines(self.screen, "white", False, curve, 20)
        
        if game_over:
            for wow_tag in wow_tags:
                centre = Vector2(wow_tag.x, wow_tag.y)
                pg.draw.circle(self.screen, "black", centre, POSE_RADIUS - 5)

        pg.display.flip()

        if self.do_screenshot:
            filename = f"screenshots/screen_{self.screenshot_index:02}.png"
            try:
                pg.image.save(self.screen, filename)
            except:
                print(f"Problem writing to {filename}.")
            self.screenshot_index += 1
            self.do_screenshot = False

        if self.terminate:
            self.close()

    def close(self):
        pg.display.quit()
        pg.quit()