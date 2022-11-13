import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
import itertools
import copy

p.init()
width = 1200
height = 800 
FPS =60
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)
BROWN = (139,131,120)
TAN = (250,235,215)

clock = p.time.Clock()
screen = p.display.set_mode((width, height))
p.display.set_caption("Backgammon")

screen.fill(TAN)

class Board:
    def __init__(self):
        self.board = [[],[1,1],[], [],[],[],[2,2,2,2,2], [],[2,2,2],[],[],[],[1,1,1,1,1],\
            [2,2,2,2,2],[],[],[],[1,1,1],[], [1,1,1,1,1], [],[],[],[],[2,2],[]]
        
class Player:
    # Players will use the same starting board, and as moves are made, the board will be adjusted
    def __init__(self, color,Comp=False):
        self.color = color
        self.temp_boards = []
        self.final_boards = []
        self.board = Board().board
        self.temp_boards.append(self.board)
        self.on_rail = False
        self.can_remove = False
        self.dice = []
        self.dice_index = 0
        self.double_board_tracker = 0
        self.Comp = Comp
        self.Red_Piece_Coords = {k: [] for k in range(26)}
        self.Black_Piece_Coords = {k: [] for k in range(26)}
        self.Red_Pieces = {}
        self.Black_Pieces = {}
        self.populate_Dict(self.board)
        self.moves = []
        self.buffer = 50
        self.draw_board()
        self.draw_pieces() 
    
    def redraw(self):
        # redraws board, for movement updates
        screen.fill(TAN)
        self.draw_board()
        self.draw_pieces()

    def draw_board(self):
        # Draws the board
        start_x, start_y = self.buffer,self.buffer 
        end_x = width-self.buffer
        end_y = height-self.buffer        
        p.draw.line(screen, BLACK, (start_x, start_y), (end_x, start_y))
        p.draw.line(screen, BLACK, (start_x, end_y), (end_x, end_y))
        p.draw.line(screen, BLACK, (start_x, start_y), (start_x, end_y))
        p.draw.line(screen, BLACK, (end_x, start_y), (end_x, end_y))
        x_gap = (end_x-start_x)/15
        for i in range(15):
            p.draw.line(screen, BLACK, (start_x+i*x_gap, start_y), (start_x+i*x_gap, end_y))
        p.draw.rect(screen,BROWN,(start_x,start_y,x_gap,end_y-start_y))
        p.draw.rect(screen,BROWN,(start_x+x_gap*7,start_y,x_gap,end_y-start_y))
        p.draw.rect(screen,BROWN,(start_x+x_gap*14,start_y,x_gap+1,end_y-start_y))                

    def draw_pieces(self):
        # Draws pieces, maps coordinates to color dictionaries for user interactions
        start_x, start_y = self.buffer,self.buffer 
        end_x = width-self.buffer
        end_y = height-self.buffer
        x_gap = (end_x-start_x)/15   
        c_size = (x_gap/2)-8
        print(c_size)
        top_half = self.board[0:13]
        bottom_half = self.board[13:]
        bottom_half = bottom_half[::-1]
        count = 0
        for i in range(len(top_half)):
            val = top_half[i]                                   
            if len(val)>0:
                if i >6:
                    i = i+1
                x_coord = start_x + x_gap*i + .5*x_gap
                current_y = start_y+ c_size
                for _ in range(len(val)):
                    y_coord = current_y
                    if 1 in val:
                        # append the left, right, top, bottom of piece
                        self.Red_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = RED
                    else:
                        self.Black_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = BLACK
                    p.draw.circle(screen, color, (x_coord,y_coord), c_size)
                    current_y+=c_size*2 -2
            count+=1        
        count = 25
        for i in range(len(bottom_half)):
            val = bottom_half[i]
            if len(val)>0:
                if i >6:
                    i = i+1
                x_coord = start_x + x_gap*i + .5*x_gap
                current_y = end_y- c_size
                for _ in range(len(val)):
                    y_coord = current_y
                    if 1 in val:
                        self.Red_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = RED
                    else:
                        self.Black_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = BLACK

                    p.draw.circle(screen, color, (x_coord,y_coord), c_size)
                    current_y-=c_size*2 -2
            count-=1    
    def rail_check(self):
        # Determines if player moving has a piece on the rail
        if self.color == 'red':
            if 0 in self.White_Pieces:
                self.on_rail = True
            else:
                self.on_rail = False
        if self.color =='black':
            if 25 in self.Black_Pieces:
                self.on_rail = True
            else:
                self.on_rail = False

    def roll(self):
        die_1 = random.randint(1,6)
        die_2 = random.randint(1,6)
        if die_1 == die_2:
            for _ in range(2):
                self.dice.append([die_1,die_2])
        else:
            self.dice.append([die_1,die_2])
            self.dice.append([die_2,die_1])
        return
    
    def populate_Dict(self, board):
        # Populates the piece dictionary for white and black
        for slot,val in enumerate(board):
            if 1 in val:
                self.Red_Pieces[slot]=len(val)
            elif 2 in val:
                self.Black_Pieces[slot]=len(val)
    
    def blocked(self,spot):
        # checks if a spot is blocked for a given color
        if self.color == 'red':
            if spot in self.Black_Pieces:
                if self.Black_Pieces[spot]>1:
                    return True
            return False      
        if self.color =='black':
            if spot in self.Red_Pieces:
                if self.Red_Pieces[spot]>1:
                    return True
            return False     
    
    def spot_open(self, spot):
        # Checks if a spot is open
        if self.color =='red':
            if self.blocked(spot)==True:
                return False
            if self.can_remove == False:
                if spot>=25:
                    return False                
            return True
        if self.color =='black':
            if self.blocked(spot)==True:
                return False
            if self.can_remove == False:
                if spot<=0:
                    return False                
            return True

    def calc_moves(self,start,die):
        # individual check from starting position for human player, 
        # to be used for highlighting piece movement
        # adds all movable spots to players self.moves list
        moves = []
        
        if self.color =='red':
            end = start + die                
        elif self.color =='black':
            end = start-die
        if self.spot_open(end)==True:                
            moves.append(end)        
        return moves

    def move(self,board,start,end):
        if self.spot_open(end)==True:
            if board[start]!=[]:
                piece = board[start].pop()
                if self.color=='red':
                    if 2 in board[end]:
                        opp_piece = board[end].pop()
                        board[-1].append(opp_piece)
                if self.color=='black':
                    if 1 in board[end]:
                        opp_piece = board[end].pop()
                        board[0].append(opp_piece)       
                board[end].append(piece)
                # self.redraw()
                return board
        
    def find_board_states(self,Dice):
        # technically solves non double rolls for finding all board states recursively
               
        if len(self.temp_boards)==0:
            return      
        Die = Dice[self.dice_index]
        
        current_board = self.temp_boards[0]        
        self.populate_Dict(current_board)
        if self.color =='red':
            Pieces = self.Red_Pieces
        else:
            Pieces = self.Black_Pieces
        
        for piece in Pieces:
            
            Moves = self.calc_moves(piece,Die)
            for move in Moves:
                Temp_Board = copy.deepcopy(current_board)

                New_Board = self.move(Temp_Board,piece,move)

                if self.dice_index<len(Dice)-1:
                    if New_Board not in self.temp_boards:
                        if New_Board != None:
                            self.temp_boards.append(New_Board)

                if self.dice_index==len(Dice)-1:
                    if New_Board not in self.final_boards:
                        if New_Board!=None:
                            self.final_boards.append(New_Board)        
        
        self.double_board_tracker-=1
    
        if self.dice_index==0:
            if self.double_board_tracker <= 0:
                self.dice_index+=1               
        self.temp_boards.remove(current_board)        
        self.find_board_states(Dice)      
    
    def find_board_states_doubles(self):
        self.temp_boards = copy.deepcopy(self.final_boards)    
        self.final_boards.clear()
        self.double_board_tracker = len(self.temp_boards)
        self.dice_index=0
        self.find_board_states(self.dice[1])

P1 = Player('red')
P1.dice = [[2,2], [2,2]]

print(P1.dice)

for x in P1.dice:
    P1.find_board_states(x)

if P1.dice[0]==P1.dice[1]:
    P1.find_board_states_doubles()
P1.board = P1.final_boards[-56]
P1.redraw()        
    



# print(P1.final_boards,len(P1.final_boards))




running = True
while running:
    
    clock.tick(FPS)
    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()
    # if event.type == p.KEYDOWN:       
    
    
    p.display.flip()


                
