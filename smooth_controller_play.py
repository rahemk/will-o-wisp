#!/usr/bin/env python

'''
An interactive test environment for SmoothController1.
'''

import pygame as pg
from pygame.locals import *
from math import atan2, cos, sin
from controllers import SmoothController1

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
        controller = SmoothController1()
        points = controller.get_curve_points(control_points[0], start_angle, control_points[2])
        pg.draw.lines(screen, pg.Color("white"), False, points, 10)

        ### Flip screen
        pg.display.flip()
        clock.tick(100)
        #print clock.get_fps()
    
if __name__ == '__main__':
    main()