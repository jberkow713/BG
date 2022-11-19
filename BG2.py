import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
import itertools
import copy
import time

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
        self.replica_board = copy.deepcopy(self.board)    
        self.doubles = False        
        self.on_rail = False
        self.can_remove = False
        self.dice = []
        self.count = 0        
        self.Red_Piece_Coords = {k: [] for k in range(26)}
        self.Black_Piece_Coords = {k: [] for k in range(26)}
        self.Red_Pieces = {}
        self.Black_Pieces = {}
        self.populate_Dict(self.board)
        self.stored_boards = []
        self.stored_boards.append(self.board)
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
                inner_count = 0
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
                    if inner_count <5:
                        current_y+=c_size*2 -2
                    inner_count+=1
            count+=1        
        count = 25
        for i in range(len(bottom_half)):
            val = bottom_half[i]
            if len(val)>0:
                if i >6:
                    i = i+1
                x_coord = start_x + x_gap*i + .5*x_gap
                current_y = end_y - c_size
                inner_count = 0
                for _ in range(len(val)):
                    y_coord = current_y
                    if 1 in val:
                        self.Red_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = RED
                    else:
                        self.Black_Piece_Coords[count].append((x_coord-c_size, x_coord+c_size,y_coord-c_size,y_coord+c_size))
                        color = BLACK

                    p.draw.circle(screen, color, (x_coord,y_coord), c_size)
                    if inner_count <5:
                        current_y-=c_size*2 -2
                    inner_count+=1
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
    def clear_dict(self):
        if self.color =='red':
            self.Red_Pieces = {}
        elif self.color=='black':
            self.Black_Pieces = {}
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
            if spot in self.Black_Pieces and self.Black_Pieces[spot]>1:                
                return True
            return False      
        if self.color =='black':
            if spot in self.Red_Pieces and self.Red_Pieces[spot]>1:
                return True
            return False     
    
    def spot_open(self, spot):
        # Checks if a spot is open
        
        if self.color =='red':
            if self.blocked(spot)==False and spot<25:
                return True
        if self.color =='black':
            if self.blocked(spot)==False and spot>0:                         
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
        # if board[start]==[]:
        #     return
        if self.spot_open(end)==True:            
            p = board[start].pop()
            if board[start]==[]:
                if self.color=='red':
                    del self.Red_Pieces[start]
                elif self.color=='black':
                    del self.Black_Pieces[start]    
            if self.color=='red':
                if 2 in board[end]:
                    board[0].append(p)                                      
                else:
                    board[end].append(p)                    

            if self.color=='black':
                if 1 in board[end]:                                       
                    board[25].append(p)                    
                else:
                    board[end].append(p)            
            return board
    
    def find_Board_states(self,board,die):
        # Moves all moves from one Board State using one die
        self.clear_dict()
        self.populate_Dict(board)
        if self.color =='red':
            Pieces = sorted([x for x in self.Red_Pieces.keys()])                      
        else:
            Pieces = sorted([x for x in self.Black_Pieces.keys()])   
        
        Possible_Boards = []
        for piece in Pieces:            
            Moves = self.calc_moves(piece,die)
            if Moves!=[]:
                temp_board = copy.deepcopy(board)   
                self.move(temp_board,piece,Moves[0])
                Possible_Boards.append(temp_board)
        
        return Possible_Boards

    def Non_rail_non_doubles_states(self):
        # Assumes a roll and a board exist
        # For non doubles
        die_1 = self.dice[0][0]
        die_2 = self.dice[0][1]
        
        Original = copy.deepcopy(self.board)
        die_1_boards = self.find_Board_states(self.board,die_1)
        die_2_boards = self.find_Board_states(self.board, die_2)

        States = []
        for board in die_1_boards:    
            second_boards = self.find_Board_states(board, die_2)
            for x in second_boards:
                States.append(x)
        
        self.clear_dict()
        self.populate_Dict(Original)
        

        for board_2 in die_2_boards:    
            second_boards = self.find_Board_states(board_2, die_1)
            for x in second_boards:
                if x not in States:
                    States.append(x)                    
        self.stored_boards=States
        return

    def Non_rail_doubles_states(self,die=None):
        # recurive function to find all board state
        # Assumes no pieces on rail,optional parameter for die input
        if self.count ==4:
            return 
        
        if die==None:
            die = self.dice[0][0]
        Boards = []        
        for board in self.stored_boards:
            self.clear_dict()
            next_boards = self.find_Board_states(board, die)
            for x in next_boards:
                if x not in Boards:
                    Boards.append(x)
        self.stored_boards = Boards
        self.count+=1
        self.Non_rail_doubles_states()
    
    def Rail_Non_Doubles(self):
        #Moves a non double roll with piece(s) starting on rail 
        if self.color =='red':
            Start = 0
            Count = self.Red_Pieces[0]
        elif self.color=='black':
            Start = 25
            Count = self.Black_Pieces[25]
        if Count>=2:
            for die in self.dice[0]:
                moves = self.calc_moves(Start,die)
                if moves!=[]:
                   self.move(self.board,Start,moves[0])
            return        
        
        Temporary_Stored_Boards = []
        
        if Count ==1:
            for die in self.dice[0]:
                
                for x in self.dice[0]:
                    if x!=die:
                        other = x  
                moves = self.calc_moves(Start,die)
                if moves!=[]:
                   self.move(self.board,Start,moves[0])
                   self.stored_boards.clear()
                   self.stored_boards.append(self.board)
                   self.count = 3
                   self.Non_rail_doubles_states(die=other)                   
                   for board in self.stored_boards:
                    if board not in Temporary_Stored_Boards:
                        Temporary_Stored_Boards.append(board)

                self.stored_boards.clear()
                self.board = self.replica_board
                self.populate_Dict(self.board)
                           
            self.stored_boards = Temporary_Stored_Boards
            return

    def Rail_Doubles(self):
        # Run this function with pieces on the rail, if you roll doubles
        Die = self.dice[0][0]
        if self.color =='red':
            Start = 0
            End = Start+Die 
            Count = self.Red_Pieces[0]
        elif self.color=='black':
            Start = 25
            End = Start-Die
            Count = self.Black_Pieces[25]
        if Count >=4:
            if self.calc_moves(Start,Die)!=[]:
                for _ in range(4):
                    self.move(self.board,Start,End)
                return             
        elif Count <4:
            if self.calc_moves(Start,Die)!=[]:
                for _ in range(Count):
                    self.move(self.board,Start,End)
                    self.count+=1
                self.stored_boards.clear()                    
                self.stored_boards.append(self.board)
                self.Non_rail_doubles_states()
    
    def Random_Move(self):
        self.roll()
        self.rail_check()
        if self.on_rail==False:
            if self.doubles==False:
                self.Non_rail_non_doubles_states()
            else:
                self.Non_rail_doubles_states()
        elif self.on_rail==True:
            if self.doubles==False:
                self.Rail_Non_Doubles()
            else:
                self.Rail_Doubles()
        if self.stored_boards == []:
            return         
        self.board = self.stored_boards[random.randint(0,len(self.stored_boards)-1)]
                
        self.redraw()
        return

# Below is just a simulation of movement around the board alternating turns
# With everything except the end game

board = None
running = True
while running:
    
    clock.tick(FPS)
    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()
    
    P1 = Player('red',board)        
    P1.Random_Move()    
    board = P1.board

    P2 = Player('black',board)    
    P2.Random_Move()   
    board = P2.board    
    
    time.sleep(1)       
       
    p.display.flip()