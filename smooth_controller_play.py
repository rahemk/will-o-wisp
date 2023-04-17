#!/usr/bin/env python

import pygame as pg
from pygame.locals import *
from math import atan2, cos, sin

class Controller:
    def __init__(self, start_pos, start_angle, goal_pos):
        self.start_pos = start_pos
        self.start_angle = start_angle
        self.goal_pos = goal_pos

        self.delta_t = 0.01
        self.K_v = 1
        self.K_omega = 0.025

    def get_curve_points(self):
        curve_vertex_list = [self.start_pos]

        x = self.start_pos.x
        y = self.start_pos.y
        theta = self.start_angle

        while (self.goal_pos - pg.math.Vector2(x, y)).magnitude() > 5:

            # Get the goal position in the robot's ref. frame.
            goal_rob_ref = (self.goal_pos - pg.math.Vector2(x, y)).rotate_rad(-theta)

            # Smooth controller 1 (from old 4766 notes) generates the following
            # forward and angular speeds
            v = self.K_v * abs(goal_rob_ref.x)
            omega = self.K_omega * goal_rob_ref.y

            # Velocity in the global frame.
            x_dot = v * cos(theta)
            y_dot = v * sin(theta)

            x += x_dot * self.delta_t
            y += y_dot * self.delta_t
            theta += omega * self.delta_t

            curve_vertex_list.append(pg.math.Vector2(x, y))

        return curve_vertex_list
 
gray = (100,100,100)
lightgray = (200,200,200)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
X,Y,Z = 0,1,2

def main():
    pg.init()
    screen = pg.display.set_mode((1024, 768))
 
    # The first is the start point, the middle is used to set the current angle,
    # the last is the goal point.
    control_points = [pg.math.Vector2(100,100), pg.math.Vector2(150,500), pg.math.Vector2(500,150)]
 
    # The currently selected point
    selected = None
    
    clock = pg.time.Clock()
    
    running = True
    while running:
        for event in pg.event.get():
            if event.type in (QUIT, KEYDOWN):
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                for p in control_points:
                    if abs(p.x - event.pos[X]) < 10 and abs(p.y - event.pos[Y]) < 10 :
                        selected = p
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None
        
        screen.fill(gray)
                
        if selected is not None:
            selected.x, selected.y = pg.mouse.get_pos()
            pg.draw.circle(screen, "purple", (selected.x, selected.y), 12)
        
        # Draw control points
        pg.draw.circle(screen, green, (int(control_points[0].x), int(control_points[0].y)), 8)
        pg.draw.circle(screen, blue, (int(control_points[1].x), int(control_points[1].y)), 4)
        pg.draw.circle(screen, red, (int(control_points[2].x), int(control_points[2].y)), 8)

        ### Draw control "lines"
        pg.draw.lines(screen, lightgray, False, [(x.x, x.y) for x in control_points])

        ### Draw bezier curve
        w = control_points[1] - control_points[0]
        start_angle = atan2(w.y, w.x)
        controller = Controller(control_points[0], start_angle, control_points[2])
        points = controller.get_curve_points()
        pg.draw.lines(screen, pg.Color("red"), False, points, 2)

        ### Flip screen
        pg.display.flip()
        clock.tick(100)
        #print clock.get_fps()
    
if __name__ == '__main__':
    main()