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
        board = [1,33,0, 0,0,0,55555, 0,555,0,0,0,33333,55555,0,0,0,333,0, 33333, 0,0,0,0,55,9]
        return board

class Player:
    def __init__(self):
        self.color = self.create_color()
        self.board = Board().board
        self.DICT = None
        self.opp_Dict = None
        self.can_take_off = False
        

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
            return dice2
           
                               
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
        # creates two dictionaries, self and opponent
        # array of moves
        

                
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

    def random_comp_move(self):
        MOVES = self.find_moves()
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
                        return hit_die, (FROM, VAL)


        # if len(possible_hits)>0:
        #     lst = list(possible_hits)
        #     spot = lst[random.randint(0,len(lst)-1)]
            
# TODO 
# Hitting is working, now we need to work on recalculating moves, after one die is moved

 
        

a = Player()
# print(a.find_moves())
# print(a.DICT, a.opp_Dict)
# print(a.board)
print(a.random_comp_move())



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