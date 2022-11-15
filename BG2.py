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
    # Initial board fed into players
    # 1s represent red, 2s represent black
    def __init__(self):
        self.board = [[],[1,1],[], [],[],[],[2,2,2,2,2], [],[2,2,2],[],[],[],[1,1,1,1,1],\
            [2,2,2,2,2],[],[],[],[1,1,1],[], [1,1,1,1,1], [],[],[],[],[2,2],[]]
        
class Player:
    # Player class, computer/human built into one
    def __init__(self, color, board=None):
        self.color = color
        self.temp_boards = []
        self.final_boards = []
        if board == None:
            self.board = Board().board
        else:
            self.board = board
        self.doubles = False    
        self.temp_boards.append(self.board)
        self.on_rail = False
        self.can_remove = False
        self.dice = []
        self.dice_index = 0
        self.double_board_tracker = 0
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
        # redraws board, for movement updates based on update board and piece positions
        screen.fill(TAN)
        self.draw_board()
        self.populate_Dict(self.board)
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
        # To be used to force players to take off rail before moving elsewhere
        if self.color == 'red':
            
            if 0 in self.Red_Pieces:
                self.on_rail = True
                return self.Red_Pieces[0]
            else:
                self.on_rail = False
                return 0
        if self.color =='black':
            if 25 in self.Black_Pieces:
                self.on_rail = True
                return self.Black_Pieces[25]
            else:
                self.on_rail = False
                return 0
    def max_off_rail(self):
        # If player has a piece on rail, determines ending board rail state for viable move
        if self.rail_check()!=0:
            if self.doubles==True:
                return max(self.rail_check()-4,0)
            if self.doubles==False:
                return max(self.rail_check()-2,0)
        else:
            return 0            
    def roll(self):
        # For doubles, 2 sets of the same value will be used , for recursive roll function
        # If not doubles, 2 combinations of same roll will be used for all board possibilities
        die_1 = random.randint(1,6)
        die_2 = random.randint(1,6)
        if die_1 == die_2:
            for _ in range(2):
                self.doubles = True
                self.dice.append([die_1,die_2])
        else:
            self.doubles = False
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
        # Moves a piece for a given board from start to end position
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
    def find_off_rail_boards(self,Dice):
        #TODO
        # Create a separate set of movable boards when player is stuck on the rail
        pass 
    def find_board_states(self,Dice):
        # solves all board states for a given double or non double roll
               
        if len(self.temp_boards)==0:
            return      
        Die = Dice[self.dice_index]
        
        current_board = self.temp_boards[0]        
        self.populate_Dict(current_board)
        if self.color =='red':
            Pieces = self.Red_Pieces
            self.rail_count = len(self.board[0])
        else:
            Pieces = self.Black_Pieces
            self.rail_count = len(self.board[25])        

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
        # In the case of doubles, second recursive call is made
        self.temp_boards = copy.deepcopy(self.final_boards)    
        self.final_boards.clear()
        self.double_board_tracker = len(self.temp_boards)
        self.dice_index=0
        self.find_board_states(self.dice[1])

    def Find_All_States(self):
        # Finds all board states using nested functionality created above
        if self.dice[0]!=self.dice[1]:
            self.find_board_states(self.dice[0])
        else:
            self.find_board_states(self.dice[0])
            self.find_board_states_doubles()    
    def random_move(self):
        # Creating random fair move, more to come
        self.roll()
        self.Find_All_States()
        # Temp fix
        self.rail_check()
        if self.on_rail==True:

            off_rail = self.max_off_rail()
            usable_boards = []
            if self.color == 'red':
                for b in self.final_boards:
                    if len(b[0])<=off_rail:
                        usable_boards.append(b)
            else:
                for b in self.final_boards:
                    if len(b[25])<=off_rail:
                        usable_boards.append(b)
            if len(usable_boards)==0:
                print('can not move')
                return

            self.board = usable_boards[random.randint(0,len(usable_boards)-1)]
        else:
            if len(self.final_boards)==0:
                print('can not move')
                return
            self.board = self.final_boards[random.randint(0,len(self.final_boards)-1)]
                    
        self.populate_Dict(self.board)
        self.redraw()
        self.dice = []

import time

# Basic game loop idea, original board is used, then players feed in updated boards into 
# Each other's instances, 
board = None
running = True
while running:
    
    clock.tick(FPS)
    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()

    P1 = Player('red',board)
    P1.random_move()
    board = P1.board
    P2 = Player('black', board)
    P2.random_move()
    board = P2.board
    time.sleep(1)       
       
    p.display.flip()


                