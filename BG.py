import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
p.init()
Width, Height = 1024, 1024
Max_FPS=15

class Board:
    def __init__(self):
        self.board = self.create_board()
    def create_board(self):
        board = [[],555,555,555,555,55,5,0,0,0,0,0,0,0,0,0,0,0,0,33,333,333,33,33,33,[]]
        # board = [[],33,0, 0,0,0,55555, 0,555,0,0,0,33333,55555,0,0,0,333,0, 33333, 0,0,0,0,55,[]]
        return board

class Player:
    def __init__(self, color=None,board=None):
        if color==None:
            self.color = self.create_color()
        else:
            self.color=color
        if board==None:
            self.board = Board().board
        else:
            self.board=board

        self.done = False
        self.DICT = None
        self.opp_Dict = None
        self.can_remove = None
        self.dice = None
    
    def can_take_off(self):
        if self.color == 'black':
            other = self.board[7:]
            for x in other:
                if str(5) in str(x):
                    self.can_remove = False
                    return False
            self.can_remove=True
            return True 
        if self.color == 'white':
            other = self.board[:19]
            for x in other:
                if str(3) in str(x):
                    self.can_remove = False
                    return False
            self.can_remove=True
            
            return True

    def move_piece(self, FROM, TO):
        '''
        Function used for moving one piece and altering the board state
        '''        
        print(FROM, TO)
        if isinstance(self.board[TO], list)==True:
            print('taking off')
            
            if len(str(self.board[FROM]))>1:
                curr = str(self.board[FROM])[1:]
                self.board[FROM]= int(curr)
                return
            else:
                self.board[FROM]=0
                return      
                            
        print(FROM, TO)
        starting= self.board[FROM]
        
        if isinstance(starting, list)==True:
            starting = int(starting[0])

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
    def random_list(self, lst):
        return  lst[random.randint(0,len(lst)-1)]
    def random_index(self, lst):
        return random.randint(0, len(lst)-1)               

    def create_color(self):
        if random.randint(0,1)==0:
            print('You are white')
            return 'white'
        else:
            print('You are black')
            return 'black'        
    def roll(self):
        '''
        Rolls, returns rolls
        '''        
        dice = [random.randint(1,6) for x in range(2)]
        if dice[0]==dice[1]:
            doubles = [dice[0]]*4
            self.dice=doubles
            return doubles
                  
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
        self.can_take_off()
        
        Possible_Moves = []
        Possible_Hits = []
        # for random dice, let it roll
        
        if DICE==None:
            dice =self.roll()
        # if one die has been used, we want to manually feed in the remaining dice
        else:
            dice=DICE
        
        # # TODO
        # if self.can_remove==True:
        #     pass           
        # # Track furthest back spot, allow that spot to take off if roll +spot>=25 if white
        # # and <=0 if black
        # #  Make sure opponent not behind pieces, because if they are, want to force them out
        # # or continue to take off smartest choices, like keeping blocks, minimizing risk
                  

        for die in dice:
            possible_spots = []
            possible_hits = []

            if self.can_remove==False:           

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
                                            # possible_spots.append(spot)
                                                
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
                                            # possible_spots.append(spot)            
            
                Possible_Moves.append(possible_spots)                             
                Possible_Hits.append(possible_hits)        
    
            if self.can_remove==True:
                keys = {x[0] for x in self.DICT.items()}
                if self.color == 'white':
                    furthest= min(keys)
                if self.color == 'black':
                    furthest= max(keys)

                for key in self.DICT.keys():    
                    if self.color == 'white':
                        spot = key+die
                        Finished= False
                        if key == furthest:
                            if spot >=25:
                                possible_spots.append(25)
                                Finished=True                       
                        if Finished==False:

                            if spot <= 25:
                                possible_spots.append(spot)
                                # 
                                if self.board[spot]==0:
                                    possible_spots.append(spot)
                                #If the key exists, for stacking 
                                if spot in self.DICT:
                                    if spot not in possible_spots:
                                        possible_spots.append(spot)
                                        
                                else:
                                    for idx, count in self.opp_Dict.items():
                                        if spot == idx:
                                            if count <2:
                                                possible_hits.append(spot)                                               
                    
                    if self.color == 'black':
                        
                        spot = key-die
                        Finished = False
                        if key == furthest:
                            if spot <=0:
                                possible_spots.append(0)
                                Finished=True                       
                        if Finished==False:

                            if spot >= 0:
                                if spot ==0:
                                    possible_spots.append(spot)

                                if self.board[spot]==0:
                                    possible_spots.append(spot)
                                        
                                if spot in self.DICT:
                                    possible_spots.append(spot)
                                        
                                else:
                                    for idx, count in self.opp_Dict.items():
                                        if spot == idx:
                                            if count <2:
                                                possible_hits.append(spot)
                                                    # possible_spots.append(spot)                            
                Possible_Moves.append(possible_spots)                             
                Possible_Hits.append(possible_hits)
                
        Move_Dict = dict(zip(dice, Possible_Moves))
        Hit_Dict = dict(zip(dice, Possible_Hits))        
        
        return Move_Dict, Hit_Dict

    def random_comp_move(self, DICE=None):
        
        print(self.board)
        if self.dice !=None and len(self.dice)==0:            
            return                      
        
        if DICE==None:
            MOVES = self.find_moves()
        else:
            MOVES = self.find_moves(DICE)
        
        possible_spots = MOVES[0]
        possible_hits = MOVES[1]
        print(possible_spots, possible_hits)            
        # if on rail
        Rail_Dice = []
        Hits = []

        #Moving Off Rail    
        if self.can_remove==False:

            if len(self.dice)>0:                
                
                if self.color == 'white':
                    if len(self.board[0])>0:
                        rail = 0
                        # If you can hit coming off rail
                        for roll, hit_list in possible_hits.items():
                            if len(hit_list)>0:
                                for val in hit_list:
                                    if val == rail + roll:
                                        Rail_Dice.append(roll)
                                        Hits.append(val)

                            if len(Rail_Dice)>0:

                                index = self.random_index(Rail_Dice)
                                die = Rail_Dice[index]
                                move_to = Hits[index]
                                FROM = move_to-die
                                if self.dice == []:
                                    break
                                self.dice.remove(die)
                                self.move_piece(FROM, move_to)
                                self.random_comp_move(self.dice)      

                        #For other moves off rail 
                        for roll, hit_list in possible_spots.items():

                            if len(hit_list)>0:
                                for val in hit_list:
                                    if val == rail + roll:
                                        Rail_Dice.append(roll)
                                        Hits.append(val)

                            if len(Rail_Dice)>0:
                                index = self.random_index(Rail_Dice)
                                die = Rail_Dice[index]
                                move_to = Hits[index]
                                FROM = move_to-die
                                
                                if self.dice == []:
                                    break
                                self.dice.remove(die)
                                self.move_piece(FROM, move_to)
                                self.random_comp_move(self.dice)                                    
                        
                        self.dice = []
                        return

                if self.color=='black':
                    if len(self.board[-1])>0:
                        rail = len(self.board)-1
                        # If you can hit coming off rail
                        for roll, hit_list in possible_hits.items():
                            if len(hit_list)>0:
                                for val in hit_list:
                                    if val == rail - roll:
                                        Rail_Dice.append(roll)
                                        Hits.append(val)

                                if len(Rail_Dice)>0:

                                    index = self.random_index(Rail_Dice)
                                    die = Rail_Dice[index]
                                    move_to = Hits[index]
                                    FROM = move_to+die
                                    if self.dice == []:
                                        break
                                    self.dice.remove(die)
                                    self.move_piece(FROM, move_to)
                                    self.random_comp_move(self.dice)
                            
                        for roll, hit_list in possible_spots.items():

                            if len(hit_list)>0:
                                for val in hit_list:
                                    if val == rail - roll:
                                        Rail_Dice.append(roll)
                                        Hits.append(val)

                                if len(Rail_Dice)>0:
                                    index = self.random_index(Rail_Dice)
                                    die = Rail_Dice[index]
                                    move_to = Hits[index]
                                    FROM = move_to+die
                                    
                                    if self.dice == []:
                                        break
                                    self.dice.remove(die)
                                    self.move_piece(FROM, move_to)
                                    self.random_comp_move(self.dice)                                    
                        
                        self.dice = []
                        return
        if len(self.dice)>0:

            # if can hit, must hit
            HIT_DICE = []
            for roll, hit_list in possible_hits.items():
                if len(hit_list)>0:
                    HIT_DICE.append(roll)
                    hit_die = self.random_list(HIT_DICE)
                    
                    for roll, hit_list in possible_hits.items():
                        if roll == hit_die:
                            VAL = self.random_list(hit_list)
                            if self.color == 'black':
                                FROM = VAL+hit_die
                            elif self.color =='white':
                                FROM = VAL-hit_die    
                            print(self.dice)
                            self.dice.remove(hit_die)
                            self.move_piece(FROM, VAL)
                                                    
                            self.random_comp_move(self.dice)        
            # otherwise, roll
            if len(self.dice)==0:
                return
            roll = self.random_list(self.dice)
            
            for ROLL, move_list in possible_spots.items():
                
                if ROLL==roll:
                    moved_to= self.random_list(move_list)                                   
                            
            if self.color =='black':
                FROM = moved_to+roll
            elif self.color =='white':
                FROM = moved_to-roll  

            # Figure out here, if the FROM is a 0, and if so, move it to the furthest 
            # value from the rail, for that color
            if self.board[FROM]==0:
                keys = {x[0] for x in self.DICT.items()}
                if self.color == 'white':
                    furthest= min(keys)
                if self.color == 'black':
                    furthest= max(keys)
                FROM=furthest

            print(roll)
            print(self.dice)
            print(moved_to)
            self.move_piece(FROM, moved_to)  
            self.dice.remove(roll)                
        
            self.random_comp_move(self.dice)  

# a.find_positions()
# print(a.DICT)
# print(a.find_moves())

# print(a.DICT, a.opp_Dict)

# print(a.can_take_off())

# looping, using same board
a = Player('black')
a.random_comp_move()
BRD = a.board
b = Player('white', BRD)
b.random_comp_move()
print(b.board)



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