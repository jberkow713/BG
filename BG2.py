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
        self.replica_board = copy.deepcopy(self.board)    
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





    def find_off_rail_boards(self,Dice):
        
        # Create a separate set of movable boards when player is stuck on the rail
                        
        if self.color =='red':
            self.rail_count = len(self.board[0])            
            Piece = 0
        elif self.color=='black':
            self.rail_count = len(self.board[25])            
            Piece = 25
        # If pieces on rail >= Number of Dice, force all movable pieces off rail, return the board  
        
        if self.rail_count>=len(Dice):
            
            for die in Dice:
                moves = self.calc_moves(Piece,die)
                if len(moves)>0:                    
                    self.move(self.board,Piece,moves[0])            
            
            return self.temp_boards[0]
        
        if self.rail_count<len(Dice):
                      
            if self.doubles==True:
                die = Dice[0]
                moves = self.calc_moves(Piece,die)
                if len(moves)==0:
                    print('cant move')                    
                    return self.replica_board  
                else:
                    for i in range(self.rail_count):
                        self.move(self.temp_boards[0],Piece,moves[0])
                        Dice[i]=0
                    self.dice = [Dice[0:2], Dice[2:]]
                    self.Find_All_States()                    

                    return self.final_boards[random.randint(0,len(self.final_boards)-1)]

            else:
                print(self.temp_boards[0])
                
                for die in Dice:
                    print(die)
                    moves = self.calc_moves(Piece,die)                    
                    if moves!=[]:                        
                        self.move(self.temp_boards[0],Piece,moves[0])
                        print(self.temp_boards[0]) 
                        for d in Dice:
                            if d != die:
                                                              
                                self.find_board_states([0,d])
                                
                        self.temp_boards.append(self.replica_board)
                        self.dice_index=0                            
                            
                           
                if len(self.final_boards)==0:                                      
                    return self.replica_board
                
                print(len(self.final_boards)) 
                return self.final_boards[random.randint(0,len(self.final_boards)-1)]      
        

    def end_game_board_states(self, Dice):
        # TODO
        # create end game boards based on whether a player has all their pieces in the end section of their respective color
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
        else:
            Pieces = self.Black_Pieces               

        for piece in Pieces:
            print(Pieces)    
            Moves = self.calc_moves(piece,Die)
            for move in Moves:
                Temp_Board = copy.deepcopy(current_board)

                New_Board = self.move(Temp_Board,piece,move)

                if self.dice_index==0:
                    if New_Board not in self.temp_boards:
                        if New_Board != None:
                            self.temp_boards.append(New_Board)

                if self.dice_index==1:
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
            self.dice_index=0
            self.temp_boards.append(self.replica_board)
            self.find_board_states(self.dice[1])
            
        else:
            self.find_board_states(self.dice[0])
            self.find_board_states_doubles()
                  
    def random_move(self):
        # Creating random fair move, more to come
        self.roll()
        self.rail_check()              
        
        self.Find_All_States()
        self.board = self.final_boards[random.randint(0,len(self.final_boards)-1)]
        self.populate_Dict(self.board)
        self.redraw()
        self.dice = []
        return

import time

# Basic game loop idea, original board is used, then players feed in updated boards into 
# Each other's instances, 
# board = None

P1 = Player('red')
P1.roll()
die_1 = P1.dice[0][0]
die_2 = P1.dice[0][1]
print(die_1,die_2)

Original = copy.deepcopy(P1.board)
die_1_boards = P1.find_Board_states(P1.board,die_1)
die_2_boards = P1.find_Board_states(P1.board, die_2)

States = []
for board in die_1_boards:    
    second_boards = P1.find_Board_states(board, die_2)
    for x in second_boards:
        States.append(x)

P1.Red_Pieces = {}
P1.populate_Dict(Original)

for board_2 in die_2_boards:    
    second_boards = P1.find_Board_states(board_2, die_1)
    for x in second_boards:
        if x not in States:
            States.append(x)
        
print(States, len(States))


# die_2_boards = P1.find_Board_states(P1.board,P1.dice[0][1])
# print(die_2_boards)        
         




board = None
running = True
while running:
    
    clock.tick(FPS)
    
    for event in p.event.get():
        if event.type == p.QUIT:
            sys.exit()

    
    P1 = Player('red',board)    
    P1.roll()    
    
    for die in P1.dice[0]:
        
        pieces = [x for x in P1.Red_Pieces.keys()]
        
        random_piece = pieces[random.randint(0,len(pieces)-1)]       
        P1.move(P1.board,random_piece, random_piece+die)
        P1.populate_Dict(P1.board)        

        
    P1.populate_Dict(P1.board)
    P1.redraw()
    board = P1.board

    P2 = Player('black',board)
    P2.roll()
    
    for die in P2.dice[0]:
        
        pieces = [x for x in P2.Black_Pieces.keys()]
        random_piece = pieces[random.randint(0,len(pieces)-1)]                
        P2.move(P2.board,random_piece, random_piece-die)
        P2.populate_Dict(P2.board)      
    
    P2.populate_Dict(P2.board)
    P2.redraw()
    board = P2.board



    # P1 = Player('red',board)
    # P1.move(self.board, 1,4)
    # board = P1.board
     
    # P2 = Player('black', board)
    # P2.random_move()
    # board = P2.board
    
    
    time.sleep(1)       
       
    p.display.flip()