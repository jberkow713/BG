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
    def __init__(self,width,height,color):
        self.width = width
        self.height = height
        self.screen = p.display.set_mode((self.width, self.height))
        self.color = color
        self.screen.fill(WHITE)
        
    def draw_line(self, color, x1,y1,x2,y2):
        p.draw.line(self.screen, color, (x1, y1), (x2, y2))
    
    def draw_square(self, color,x1,y1,size):
        curr_x = x1
        curr_y = y1
        for _ in range(2):
            final_x = curr_x+size
            final_y = curr_y   
            self.draw_line(color,curr_x,curr_y,final_x,final_y)
            curr_y+=size
        curr_x = x1
        curr_y = y1
        for _ in range(2):           
            final_y = curr_y+size
            final_x=curr_x   
            self.draw_line(color,curr_x,curr_y,final_x,final_y)
            curr_x+=size

    def draw_horizontal_squares(self, color, squares, x,y,size):                
        curr_x = x
        for _ in range(squares):
            self.draw_square(color,curr_x,y, size)
            curr_x += size 
    
    def draw_vertical_squares(self, color, squares, x,y,size):
        curr_y = y
        for _ in range(squares):
            self.draw_square(color,x,curr_y, size)
            curr_y += size 
    
    def draw_grid(self,squares,size):

        start_x = (self.width - squares*size)/2
        start_y = (self.height- squares*size)/2
        for _ in range(2):
            self.draw_horizontal_squares(self.color,squares,start_x,start_y,size)
            start_y += (squares-1)*size
        start_x = (self.width - squares*size)/2       
        start_y = (self.height- squares*size)/2
        for _ in range(2):
            self.draw_vertical_squares(self.color,squares,start_x,start_y,size)
            start_x += (squares-1)*size

G = Game(800,800,BLUE)
G.draw_grid(8,80)

while True:    
    clock.tick(FPS)    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()
           
    p.display.flip()