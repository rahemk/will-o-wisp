#!/usr/bin/env python

import pygame as pg
from pygame.locals import *

def interpolate(v1, v2, t):
    x = (1-t) * v1.x + t * v2.x
    y = (1-t) * v1.y + t * v2.y
    return pg.math.Vector2(x, y)

class QuadBezier:
    def __init__(self, control_vertex_list):
        self.steps = 30
        self.control_vertex_list = control_vertex_list

    def get_curve_points(self):
        curve_vertex_list = []
        for i in range(self.steps):
            t = i / self.steps
            point = self.get_point(len(self.control_vertex_list) - 1, 0, t)
            curve_vertex_list.append(point)

        return curve_vertex_list

    def get_point(self, r, i, t):
        if r == 0:
            return self.control_vertex_list[i]
        p1 = self.get_point(r - 1, i, t)
        p2 = self.get_point(r - 1, i + 1, t)
        return interpolate(p1, p2, t)
 
gray = (100,100,100)
lightgray = (200,200,200)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
X,Y,Z = 0,1,2

def main():
    pg.init()
    screen = pg.display.set_mode((1024, 768))
 
    ### Control points that are later used to calculate the curve
    control_points = [pg.math.Vector2(100,100), pg.math.Vector2(150,500), pg.math.Vector2(500,150)]
 
    ### The currently selected point
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
            # elif event.type == MOUSEBUTTONDOWN and event.button == 3:
            #     x,y = pg.mouse.get_pos()
            #     control_points.append(vec2d(x,y))
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                selected = None
        
        screen.fill(gray)
                
        if selected is not None:
            selected.x, selected.y = pg.mouse.get_pos()
            pg.draw.circle(screen, green, (selected.x, selected.y), 10)
        
        ### Draw control points
        for p in control_points:
            pg.draw.circle(screen, blue, (int(p.x), int(p.y)), 4)

        ### Draw control "lines"
        pg.draw.lines(screen, lightgray, False, [(x.x, x.y) for x in control_points])

        ### Draw bezier curve
        bezier = QuadBezier([pg.math.Vector2(x.x, x.y) for x in control_points])
        b_points = bezier.get_curve_points()
        pg.draw.lines(screen, pg.Color("red"), False, b_points, 2)

        ### Flip screen
        pg.display.flip()
        clock.tick(100)
        #print clock.get_fps()
    
if __name__ == '__main__':
    main()