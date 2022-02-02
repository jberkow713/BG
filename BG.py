import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
p.init()
Width, Height = 1024, 1024
Max_FPS=15

class Board:
    def __init__(self):
        self.board = self.create_board()
    def create_board(self):
        board = [[],33,0, 0,0,0,5, 0,555,0,0,0,33333,55555,0,0,0,333,0, 33333, 0,0,0,0,55,[]]
        return board

class Player:
    def __init__(self):
        self.color = self.create_color()
        self.board = Board().board
        self.DICT = None
        self.opp_Dict = None
        self.can_take_off = False
        self.dice = None 

    def move_piece(self, FROM, TO):
        '''
        Function used for moving one piece and altering the board state
        '''        
        print(FROM, TO)
        starting= self.board[FROM]
        if len(str(starting)[1:])>0:
            
            remaining= int(str(starting)[1:])
        else:
            remaining = 0    
        moved = int(str(starting)[0])
                
        self.board[FROM]=remaining

        ending = self.board[TO]
        # For a hit
        if moved !=int(str(self.board[TO])[0]):
            if self.color =='white':
                if self.board[TO]!=0:
                    self.board[-1].append(ending)
                self.board[TO] = moved
                return  
            elif self.color =='black':
                if self.board[TO]!=0:
                    self.board[0].append(ending)
                self.board[TO]= moved
                return 
        # For Stacking pieces
        if moved == int(str(self.board[TO])[0]):
            curr = str(ending)
            mov = str(moved)
            self.board[TO]= int(curr+mov)

    def create_color(self):
        rand = random.randint(0,1)
        if rand ==0:
            print('You are white')
            return 'white'
        else:
            print('You are black')
            return 'black'        
    def roll(self):
        '''
        Rolls, returns rolls
        '''        
        dice = []
        dice2 = []
        for i in range(2):
            a = random.randint(1,6)
            dice.append(a)
        
        if dice[0]==dice[1]:
            for i in range(4):
                dice2.append(dice[0])
            self.dice = dice2
            return dice2
           
        self.dice = dice                       
        return dice             

    def find_positions(self):
        '''
        Creates player dictionaries of moves and counts
        '''
        b = list(enumerate(self.board))
        positions = []
        positions2 = []
        amounts = []
        amounts2 = []
        
        for idx, val in b:
            if str(3) in str(val):
                amounts.append(len(str(val)))
                positions.append(idx)
        white_dict = dict(zip(positions, amounts))               
                
        for idx, val in b:
            if str(5) in str(val):
                amounts2.append(len(str(val)))
                positions2.append(idx)
        black_dict = dict(zip(positions2, amounts2))          
                
        if self.color == 'white':
            self.DICT = white_dict
            self.opp_Dict = black_dict 
            return 
        else:
            self.DICT = black_dict
            self.opp_Dict = white_dict         
            return            
    
    def find_moves(self, DICE=None):
        '''
        Finds moves player rolling can move to on board
        '''                
        self.find_positions()
        
        Possible_Moves = []
        Possible_Hits = []
        # for random dice, let it roll
        
        if DICE==None:
            dice =self.roll()
        # if one die has been used, we want to manually feed in the remaining dice
        else:
            dice=DICE

        for die in dice:
            possible_spots = []
            possible_hits = []
            if self.can_take_off ==False:
                for key in self.DICT.keys():
                    if self.color == 'white':
                        spot = key+die
                        if spot <= 24:
                            if self.board[spot]==0:
                                possible_spots.append(spot)
                                
                            if spot in self.DICT:
                                possible_spots.append(spot)
                                    
                            else:
                                for idx, count in self.opp_Dict.items():
                                    if spot == idx:
                                        if count <2:
                                            possible_hits.append(spot)
                                            possible_spots.append(spot)
                                            
                    if self.color == 'black':
                        spot = key-die
                        if spot >= 1:
                            if self.board[spot]==0:
                                possible_spots.append(spot)
                                
                            if spot in self.DICT:
                                possible_spots.append(spot)
                                     
                            else:
                                for idx, count in self.opp_Dict.items():
                                    if spot == idx:
                                        if count <2:
                                            possible_hits.append(spot)
                                            possible_spots.append(spot)
            Possible_Moves.append(possible_spots)                             
            Possible_Hits.append(possible_hits)
        
        Move_Dict = dict(zip(dice, Possible_Moves))
        Hit_Dict = dict(zip(dice, Possible_Hits))

        return Move_Dict, Hit_Dict                                   

    def random_comp_move(self, DICE=None):        
        
        if self.dice !=None:
            if len(self.dice)==0:
                print('hi')
                return 
        if DICE==None:
            MOVES = self.find_moves()
        else:
            MOVES = self.find_moves(DICE)    
        possible_spots = MOVES[0]
        possible_hits = MOVES[1]
        print(possible_spots, possible_hits)
        
        # Example of possible_spots {3, 4, 14, 15, 19, 20, 21, 22}, ex possible_hits {6}
        HIT_DICE = []
        for roll, hit_list in possible_hits.items():
            if len(hit_list)>0:
                HIT_DICE.append(roll)
                hit_die = HIT_DICE[random.randint(0,len(HIT_DICE)-1)]
                for roll, hit_list in possible_hits.items():
                    if roll == hit_die:
                        VAL = hit_list[random.randint(0,len(hit_list)-1)]
                        if self.color == 'black':
                            FROM = VAL+hit_die
                        elif self.color =='white':
                            FROM = VAL-hit_die    
                        
                        self.dice.remove(hit_die)
                        self.move_piece(FROM, VAL)
                        # Check to see if all dice are used
                        
                        # otherwise, continue the move
                        self.random_comp_move(self.dice)
        MOVE_DICE = []
        
        for roll, move_list in possible_spots.items():
            
            if len(move_list)>0:
                MOVE_DICE.append(roll)
                moved_die = MOVE_DICE[random.randint(0,len(MOVE_DICE)-1)]
                for roll, move_list in possible_spots.items():
                    if roll == moved_die:
                        VAL = move_list[random.randint(0, len(move_list)-1)]
                        if self.color =='black':
                            FROM = VAL+moved_die
                        elif self.color =='white':
                            FROM = VAL-moved_die  

                        print(self.dice)
                        self.dice.remove(moved_die)
                        self.move_piece(FROM, VAL)           
                        print(self.dice)
                        # if all dice have been used
                        self.random_comp_move(self.dice)

            
# TODO 
# Hitting is working, now we need to work on recalculating moves, after one die is moved

 
        

a = Player()
# print(a.find_moves())
# print(a.DICT, a.opp_Dict)
# print(a.board)

print(a.random_comp_move())
print(a.dice)
print(a.board)



# def main():
#     screen = p.display.set_mode((Width, Height))
#     clock = p.time.Clock()
#     screen.fill(p.Color('white'))
   
#     running = True
#     while running:
#         for e in p.event.get():
#             if e.type == p.QUIT:
#                 running = False
#         clock.tick(Max_FPS)
#         p.display.flip()

# main()                