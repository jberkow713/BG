import pygame, sys
from pygame.locals import*

pygame.init()

width = 1200
height = 800
origin = 0
margin = 25
top_left = origin+margin, origin+margin
top_right = width-margin, origin+margin
bottom_left = origin+margin, height-margin
bottom_right = width-margin, height-margin

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)

Ballsize =15
FPS =60
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))
screen.fill(WHITE)

def draw_screen():
    pygame.draw.lines(screen, BLACK, False, [(top_left), (top_right), (bottom_right), (bottom_left), (top_left)], 4)
    pygame.display.set_caption("Wallsmash")

Rectangle_Positions = []

class Mover:
    def __init__(self):
        self.x = width/2
        self.y = .9*height
        self.speed = 10
        self.size = 100
        self.current_pos = (self.x, self.x+self.size)
        pygame.draw.rect(screen,BLUE,(self.x,self.y,self.size,5))        
            
    def update(self):
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            pygame.draw.rect(screen,WHITE,(self.x,self.y,100,5)) 
            self.new_x = self.x + self.speed 
            if self.new_x >25 and self.new_x < 1075:
                self.x =self.new_x             

        elif keys[pygame.K_LEFT]:
            pygame.draw.rect(screen,WHITE,(self.x,self.y,100,5)) 
            self.new_x = self.x - self.speed
            if self.new_x >25 and self.new_x < 1075:
                self.x =self.new_x            
        
        self.current_pos=(self.x, self.x+self.size)
        pygame.draw.rect(screen,BLUE,(self.x,self.y,self.size,5))     

MOVER = Mover()

class Ball():
    def __init__(self,x,y,color, xspeed, yspeed):
        self.x = x
        self.y = y
        self.color = color
        self.xspeed = xspeed
        self.yspeed = yspeed
        self.lives = 3
        self.last_wall = None
        self.blocks = 0
        self.mover = MOVER
        self.mult = 1.25
        self.increment = 10

        pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)    
    
    def move(self):
        #This will be the main movement function that takes care of all the physics, collisions, etc with the walls,
        #The mover, the bricks, etc
        #Need to be able to check the direction ball is moving right before it hits a surface, to reverse either x or y
        if self.blocks == self.increment:
            self.xspeed = self.xspeed *self.mult
            self.yspeed = self.yspeed *self.mult
            self.blocks = 0
        #paddle collision
        if self.y >=self.mover.y - Ballsize:
            pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)
            paddle_x = self.mover.current_pos
            if self.x > paddle_x[0] and self.x < paddle_x[1]:
                self.x +=self.xspeed
                self.yspeed = self.yspeed * -1
                self.y +=self.yspeed
                pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)
                self.last_wall = 'bottom'
                return 
            else:
                if self.y >Mover.y+Ballsize:
                    self.lives -=1
                    self.x = width/2
                    self.y = height/2        
        #side walls
        Buffer = origin+margin+Ballsize
        if self.x <Buffer or self.x >=width-Buffer:
            pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)
            self.y +=self.yspeed 
            self.xspeed = self.xspeed *-1
            self.x +=self.xspeed
            pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)              
            return 
        
        #top wall
        if self.y <Buffer:
            pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)
            self.x +=self.xspeed 
            self.yspeed = self.yspeed *-1
            self.y +=self.yspeed
            pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)
            self.last_wall = 'top'
            return 
        
        #Check collisions with blocks
        if self.y >=100 and self.y <226:
            count = 0
            for x in Rectangle_Positions:

                if self.x+Ballsize >= x[1][0] and self.x-Ballsize <= x[1][1]:
                    if self.y+Ballsize >= x[2][0] and self.y-Ballsize <= x[2][1]:
                        self.blocks +=1
                        del Rectangle_Positions[count]
                        pygame.draw.rect(screen,WHITE,(x[0][0],x[0][1],75,25))
                        if self.last_wall == 'bottom':
                            pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)
                            self.x +=self.xspeed
                            self.yspeed = self.yspeed * -1
                            self.y +=self.yspeed
                            pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)
                            self.last_wall = 'top'
                            return
                        elif self.last_wall == 'top':
                            pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)
                            self.x +=self.xspeed
                            self.yspeed = self.yspeed * -1
                            self.y +=self.yspeed
                            pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)
                            self.last_wall = 'bottom'
                            return
                        
                count +=1
        pygame.draw.circle(screen,WHITE,(self.x,self.y),Ballsize)        
        self.x +=self.xspeed
        self.y +=self.yspeed
                
        pygame.draw.circle(screen,self.color,(self.x,self.y),Ballsize)
     

class Rectangles():
    def __init__(self):
        
        self.draw()
    def draw(self):
        
        x = 100
        y = 100
        length = 75
        width = 25
        colors = [RED, GREEN, BLUE, PURPLE]
        index = 0

        while y <=201:
            #tuple of tuples, representing the drawing coordinates, then the xrange, and yrange of rectangles
            #appended to the positions list, to be referenced for when the ball hits the rectangles
            a = round(x,2)
            b = round(y,2)
            c = a+length
            d = b+width
            Rectangle_Positions.append(((a,b),(a,c),(b,d))) 
            pygame.draw.rect(screen,colors[index],(a,b,length,width))

            x +=length+.05
            index +=1
            if index >3:
                index = 0
            if x >=1050:
                y+=width+.2
                x = 100

        

#TODO create ball class, movement of ball, bounce off Mover, hit rectangles, update rectangles, etc
#can now reference the rectangle positions within the ball class to update rectangles
#can now reference the mover position to check how and where ball bounces

Rectangle = Rectangles()

Ball1 = Ball(width/2, height/2, BLACK,2,3)
Ball2 = Ball(width/3, height/3, BLACK,2,3)

running = True
while running:
    draw_screen()
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    if event.type == pygame.KEYDOWN:                        
        MOVER.update()
    
    Ball1.move()
    Ball2.move()
        
    pygame.display.flip()
           
