from re import L
import pygame as p 
import random
import sys
import math
from pygame.locals import(
    K_UP, K_DOWN, K_LEFT, K_RIGHT,
    K_ESCAPE, KEYDOWN, QUIT, K_RETURN
)
# Screen
WIDTH = 800 #1800
HEIGHT = 800 #1400
FPS = 60
# Colors
GROUND_COLOR = (255, 222, 179)
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)

p.init()
clock = p.time.Clock()

class Game:
    def __init__(self,width,height,buffer):
        self.width = width
        self.height = height
        self.screen = p.display.set_mode((self.width, self.height))
        self.screen.fill(WHITE)
        self.buffer = buffer

    def draw_line(self, color, x1,y1,x2,y2):
        p.draw.line(self.screen, color, (x1, y1), (x2, y2))
    
    def draw_square(self, color,x1,y1,size):
        curr_x = x1
        curr_y = y1
        for i in range(2):
            final_x = curr_x+size
            final_y = curr_y   
            self.draw_line(color,curr_x,curr_y,final_x,final_y)
            curr_y+=size
        curr_x = x1
        curr_y = y1
        for i in range(2):           
            final_y = curr_y+size
            final_x=curr_x   
            self.draw_line(color,curr_x,curr_y,final_x,final_y)
            curr_x+=size
    def draw_grid(self, color, squares, x,y,size):
                
        curr_x = x
        for i in range(squares):
            self.draw_square(color,curr_x,y, size)
            curr_x += size + self.buffer


G = Game(800,800,10)
G.draw_grid(BLUE,5,100,100,100)

while True:    
    
    clock.tick(FPS)    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()
           
    p.display.flip()