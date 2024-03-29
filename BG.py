import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
import itertools
import copy
'''
The purpose of this notebook is to train a computer to play exceptionally advanced Backgammon
This notebook is broken down into 2 classes, one of them 'Board' simply sets the board, 
The other class 'Player', does all of the work. 
The Player class uses the board, and currently is responsible for finding all possible moves which can be made
for a given roll. Each move is linked to an individual board. 
From there, I am currently in the process of working on a brain function that will decide which move to choose
based on a value system I am in the process of creating, for a given roll.

Ultimately, this notebook will also be used for reinforced learning, connected to AWS, or some other cloud, 
and games will be simulated and information stored.

Enjoy!
'''
p.init()
Width, Height = 1024, 1024
Max_FPS=15

def consec_pairs(DICT):
    blocks = []
    for k,v in DICT.items():
        if v>=2:
            blocks.append(k)
    length = len(blocks)-1
    idx = 0

    consec = []

    while length>0:
        consecutive = []
        CONSEC = True
        while CONSEC==True:
            prv = blocks[idx-1]
            curr = blocks[idx]
            next = blocks[idx+1]
            if next == curr+1:
                consecutive.append(curr)                    
            else:                    
                CONSEC = False
                if curr == prv +1:
                    consecutive.append(curr)

            idx+=1
            length-=1
            if idx == len(blocks)-1:
                if blocks[idx]==blocks[idx-1]+1:
                    consecutive.append(blocks[idx])
                CONSEC=False
        consec.append(consecutive)
        
    consecs = [x for x in consec if len(x)>0]
    
    return consecs

class Board:
    '''
    3s represent white pieces, 5s represent black pieces
    Sets the board, once game runs, class is not used as board will be updated in the Player Class
    '''
    def __init__(self):
        self.board = self.create_board()
    def create_board(self):
        # board = [[],0,555,55,55,555,55555,0,0,0,0,0,0,0,0,0,0,0,0,33333,333,33,333,33,0,[]]
        board = [[],33,0, 0,0,0,55555, 0,555,0,0,0,33333,55555,0,0,0,333,0, 33333, 0,0,0,0,55,[]]
        # board = [[],3,0, 55,5,0,555, 0,555,0,3,0,3333,5555,0,3,0,33,0, 333, 5,0,33,0,5,[]]
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
        self.saved_board = None 
        self.done = False
        self.DICT = None
        self.opp_Dict = None
        self.can_remove = None
        self.dice = None
        self.moves = None
        self.board_states = None
        self.forced_move = None
        self.pips = None
        self.opp_pips = None  
    
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

    def consec_blocks(self, board=None):
        if board==None:
            self.find_positions()
        
        else:
            self.find_positions(board)       
        
        return consec_pairs(self.DICT)   
      
    
    def find_single_blocks(self, board=None):
        
        if board==None:
            self.find_positions()
        
        else:
            self.find_positions(board)

        blocks = []
        for k,v in self.DICT.items():
            if v >=2:
                blocks.append(k)
        return blocks         
    # def find_hit_count(self):


    def pip_count(self):
        self.find_positions()
        # {1: 3, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1} {19: 2, 20: 3, 21: 3, 22: 2, 23: 2, 24:2}
        if self.color=='white':
            WHITE = self.DICT
            BLACK = self.opp_Dict
        
        else:
            BLACK=self.DICT
            WHITE=self.opp_Dict
        white_pip = 0
        
        for k,v in WHITE.items():
            diff = 25-k
            white_pip +=diff*v
        black_pip = 0
        
        for k,v in BLACK.items():
            diff = 0+k
            black_pip +=diff*v
        
        if self.color == 'white':
            self.pips = white_pip
            self.opp_pips = black_pip
        if self.color == 'black':
            self.pips = black_pip
            self.opp_pips = white_pip    
    
    def find_furthest_back(self):
        if self.color == 'white':
            curr = 0
            for spot in self.opp_Dict.keys():
                if spot >curr:
                    curr = spot
            return curr

        if self.color == 'black':
            curr = 25
            for spot in self.opp_Dict.keys():
                if spot <curr:
                    curr = spot
            return curr           

    def move_piece(self, FROM, TO, board=None):
        '''
        Function used for moving one piece and altering the board state
        '''        
        # print(FROM, TO)
        if board==None:
            board = self.board
        
        #Can only move to the end rail if you're moving off, will not affect other stuck colors in end zone    
        if isinstance(board[TO], list)==True:
            #33333 
            if len(str(board[FROM]))>1:
                curr = str(board[FROM])[1:]
                board[FROM]= int(curr)
                return
            
            else:
                board[FROM]=0
                return                             

        # All other movement       
        starting= board[FROM]
        
        if isinstance(starting, list)==True:
            starting_val = str(starting[0])
        
        else:
            starting_val = str(starting)    
        
        # the piece being moved
        moving= starting_val[0]
        # setting remaining values for later when moving
        if len(starting_val)>1:

            if isinstance(starting, list)==True:                            
                remaining = [int(starting_val[1:])]
            
            else:
                remaining = int(starting_val[1:])    
        
        elif len(starting_val)==1:
            if isinstance(starting, list)==True:                          
                remaining = []
            
            else:
                remaining = 0

        # if moving to an empty spot
        if board[TO]==0:
            
            board[TO]= int(moving)
            board[FROM] = remaining
        
        # For stacking pieces of same color
        elif moving in str(board[TO]):
            board[TO] = int(moving+str(board[TO]))
            board[FROM] = remaining

        # For hitting
        else:
            # send hit piece to corresponding rail
            if self.color == 'white':
                if board[-1] == []:
                    board[-1] = [5]
                
                else:
                    current_rail = str(board[-1][0])
                    board[-1] = [int(current_rail+str(5))]
            if self.color == 'black':
                if board[0] == []:
                    board[0] = [3]
                
                else:
                    current_rail = str(board[0][0])
                    board[0] = [int(current_rail+str(3))]
                            
            # set value at end after moving hit piece
        
            board[TO] = int(moving)
            board[FROM] = remaining

        return                        
    
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

    def find_positions(self, board=None):
        '''
        Creates player dictionaries of moves and counts
        '''
        if board == None:
            board = self.board
        
        else:
            board = board    
        b = list(enumerate(board))
        positions = []
        positions2 = []
        amounts = []
        amounts2 = []
        
        for idx, val in b:

            if isinstance(val, list)==True and val!=[]:

                VAL = str(val[0])
                amount = len(VAL)
                if str(3) in VAL:
                    amounts.append(amount)
                    positions.append(idx)
                if str(5) in VAL:
                    
                    amounts2.append(amount)
                    positions2.append(idx)                              
            
            else:
                if str(3) in str(val):
                    amounts.append(len(str(val)))
                    positions.append(idx)            
        
                if str(5) in str(val):
                    amounts2.append(len(str(val)))
                    positions2.append(idx)

        white_dict = dict(zip(positions, amounts))  
        black_dict = dict(zip(positions2, amounts2))          
                
        if self.color == 'white':
            self.DICT = white_dict
            self.opp_Dict = black_dict 
            return 
        else:
            self.DICT = black_dict
            self.opp_Dict = white_dict         
            return            
    
    def branch_out(self, key, roll, opp_keys):
        ''' Determines if piece can be moved with a given roll'''

        if self.can_remove == False:
            if self.color == 'white':
                spot = key + roll
            if self.color == 'black':
                spot = key-roll      

            if spot >0 and spot <25:

                if spot not in opp_keys:
                    return spot, True
                elif spot in opp_keys:
                    
                    if self.opp_Dict[spot]==1:
                        return spot, True
        
        if self.can_remove==True:
            
            KEYS = {x[0] for x in self.DICT.items()}
            if self.color == 'white':
                furthest= min(KEYS)
            if self.color == 'black':
                furthest= max(KEYS)                          
            
            if key == furthest:

                if self.color == 'white':
                    if key+roll >25:
                        spot = min(key+roll, 25)
                    else:
                        spot = key+roll     
                if self.color == 'black':
                    if key-roll <0:
                        spot = max(key-roll, 0)
                    else:
                        spot = key-roll

            elif key!=furthest:
                if self.color == 'white':
                    spot = key+roll
                elif self.color == 'black':
                    spot = key -roll

            if spot >=0 and spot <=25:
                if spot not in opp_keys:
                    return spot, True
                elif spot in opp_keys:
                    
                    if self.opp_Dict[spot]==1:
                        return spot, True   
    
    def update_reality(self, DICE=None):
        '''
        Finds all possible board states for a given roll, stores them in self.board_states
        '''
        self.saved_board = copy.deepcopy(self.board)                       
        self.find_positions()
        # print(self.DICT)
        # print(self.opp_Dict)
        self.can_take_off()
        if DICE==None:
            self.roll()
            print(self.dice)
        else:
            self.dice = DICE    
        Rail_Count = self.rail_count(self.board)        
        board_states = []              
        
        # for doubles
        if len(self.dice)==4: 
            Length = len(self.dice)
            while Length >0:           
                
                New_Boards = []

                if Length == len(self.dice):
                    board_states = [self.board]

                for board in board_states:

                    self.find_positions(board)

                    keys = [x for x in self.DICT.keys()]
                    opp_keys = [x for x in self.opp_Dict.keys()]               
                    
                    roll = self.dice[0]
                    LENGTH = len(keys)
                    idx = 0                            

                    while LENGTH >0:
                        CAN_MOVE = False

                        key = keys[idx]
                        evaluate = self.branch_out(key, roll, opp_keys)
                        if evaluate != None:                
                            CAN_MOVE=True
                            spot = evaluate[0]                   
                        
                        current_board = copy.deepcopy(board)
                        
                        if CAN_MOVE == True:                        
                            # recalculate positions based on moved piece for given board
                            self.move_piece(key, spot, board)                            
                                            
                            # Save board 
                            New_Boards.append(board)

                        board = current_board    

                        idx +=1
                        LENGTH -=1

                board_states = New_Boards
                Length -=1 
        
            self.board_states= board_states
            self.board = copy.deepcopy(self.saved_board)   
            return               
                
        # For a non double roll
        if len(self.dice)==2:                            
            
            keys = [x for x in self.DICT.keys()]
            opp_keys = [x for x in self.opp_Dict.keys()]            

            # Check to see if 2 or more on rail
            if Rail_Count >=2:
               
                if self.color == 'white':
                    rail = 0
                if self.color == 'black':
                    rail = 25               
                
                die_1_check = self.branch_out(rail, self.dice[0], opp_keys)
                if die_1_check != None:
                    spot = die_1_check[0]
                    self.move_piece(rail, spot)
                    self.find_positions()
                    opp_keys = [x for x in self.opp_Dict.keys()]
                    
                    # self.board is updated , or not, here  

                die_2_check = self.branch_out(rail, self.dice[1], opp_keys)
                if die_2_check != None:
                    spot = die_2_check[0]
                    self.move_piece(rail, spot)
                    
                # Save the board after possible moves
                self.board_states = [self.board]
                self.forced_move = True
                return 

            LEN = len(self.dice)    
            IDX = 0            

            while LEN>0:                
                
                roll = self.dice[IDX]

                LENGTH = len(keys)
                idx = 0                               

                while LENGTH >0:
                    # each key seeing if it can move using each roll
                    CAN_MOVE = False
                    
                    key = keys[idx]
                    evaluate = self.branch_out(key, roll, opp_keys)
                    if evaluate != None:                
                        CAN_MOVE=True
                        spot = evaluate[0]                   
                        
                    if CAN_MOVE == True:                        
                           
                        self.move_piece(key, spot)                          
                        # recalculate positions based on moved piece 
                        self.find_positions()
                        
                        # Save board state here
                        current_board = copy.deepcopy(self.board)                        

                        keys2 = [x for x in self.DICT.keys()]
                        
                        opp_keys2 = [x for x in self.opp_Dict.keys()]

                        for x in self.dice:
                            if x != roll:
                                remaining = x
                                
                        LENGTH_2 = len(keys2)
                        idx2 = 0                                          

                        while LENGTH_2 >0:
                            # each key seeing if it can move using remaining roll
                            CAN_MOVE_2 = False
                            
                            key2 = keys2[idx2]
                            evaluate = self.branch_out(key2, remaining, opp_keys2)
                            if evaluate != None:                
                                CAN_MOVE_2=True
                                spot2 = evaluate[0] 
                            
                            if CAN_MOVE_2 == True:                                

                                self.move_piece(key2, spot2)                                

                                if self.board not in board_states:
                                    board_states.append(self.board)                                    

                            idx2 +=1
                            LENGTH_2 -=1
                            self.board = copy.deepcopy(current_board)

                    self.board = copy.deepcopy(self.saved_board)    

                    idx +=1
                    LENGTH -=1
                
                IDX+=1
                LEN -=1
        self.board_states = board_states        
        return
    
    
    def rail_count(self, board):
        self.find_positions(board)
        # {0: 2, 1: 1, 12: 5, 17: 3, 19: 5}
        
        if self.color == 'white':
            rail = 0
        if self.color =='black':
            rail = 25    
                
        if rail in self.DICT.keys():
            count = self.DICT[rail]
        
        else:
            count = 0

        return count

    def find_move_off_rail_list(self, list):
        # gets you count of pieces you have on rail, if you have any of your current board
        starting_count = self.rail_count(self.board)
                                
        # If nothing is on the rail, you can choose from entire list
        if starting_count == 0:
            return list 
        
        else:            
            # Smallest possible rail count not knowing the dice, after moving
            best_rail_count = max(0,starting_count - len(self.dice))
            # Best possible rail count after assessing all boards
            current_best = starting_count
            for lst in list:
                if current_best == best_rail_count:
                    return [x for x in list if self.rail_count(x)==best_rail_count]

                COUNT = self.rail_count(lst)
                if current_best > COUNT:
                    current_best = COUNT      
            # if ending best count off rail = starting count on rail, you can not move
            if current_best == starting_count:
                
                return []
            else:               

                return [x for x in list if self.rail_count(x)==current_best]

    def random_comp_move(self):
        '''
        Based on a starting board state, finds all usable board states given all boards, for a given roll
        Returns a random board
        '''       
        # get all possible board states for given roll                  
        self.update_reality()                       
         
        # In the case of pieces stuck on rail, want to find usable board states
        if self.forced_move == True:
            usable_boards = self.board_states[0]
            print(usable_boards)
            return usable_boards
        
        usable_boards = self.find_move_off_rail_list(self.board_states)
        # working here
                
        if usable_boards == []:
            print('Stuck on rail, can not move')
        # Otherwise, return possible move from possible list
        
        else:
            board = self.random_list(usable_boards)
           
            return board

    def opp_rail_count(self):
        
        starting_opp_dict = self.opp_Dict
        
        if self.color == 'white':
            opp_rail_count = 0
            for k,v in starting_opp_dict.items():
                if k == 25:
                    opp_rail_count +=v
        if self.color == 'black':
            opp_rail_count = 0
            for k,v in starting_opp_dict.items():
                if k == 0:
                    opp_rail_count +=v
        return opp_rail_count            
    
    def choose_optimal_board(self):
        
        self.find_positions()
               
        print(self.DICT)
        print(self.opp_Dict)
        print(self.opp_rail_count())                               

        self.update_reality()

        self.pip_count()

        pip_ratio = (self.pips-sum(self.dice)) / self.opp_pips
        pip_differential = self.pips-sum(self.dice) - self.opp_pips
        print(pip_ratio, pip_differential)
        print(self.find_furthest_back())

        if self.forced_move == True:
            usable_boards = self.board_states[0]
        
        usable_boards = self.find_move_off_rail_list(self.board_states)
        if usable_boards == []:
            print('Stuck on rail, can not move')

        # Need to look for board conditions
        for board in usable_boards:
            
            consec_blocks = self.consec_blocks(board)
            all_consecs = [item for sublist in consec_blocks for item in sublist]
            
            all_blocks = self.find_single_blocks(board)
            single_blocks = [x for x in all_blocks if x not in all_consecs]            

            #find consecutive blocks, and single blocks for a given possible board state 
            print(consec_blocks, single_blocks)
            
        # TODO Main Idea:
        
        # Create tasks , based on board states
        # board states can be based on pip count differential, blocks, board position, etc...
        # Initially, little difference, incentives blocks, evening towers, hitting
        # Far behind, incentivizes creating full block, turtling guys in opponent's space
        # far ahead, incentivizes running and stack on your towers, and minimizing risk for what rolls could hit you
        
        # Set up Value system based on type of board state
        # Check which possible move maximizes objective of current value state by checking next moves and finding
        # which percentage of those moves achieve objective

        # Early Game Condition Preferences:
        '''
        White:
        1)Hit and make 18 block
        2)Hit Opponent from 0-12 / 18 block
        3)Hit + 20 block, 21 block, 22 block
        4)20 block, 21 block, 22 block
        5)Hit + Set up 18 block
        6)Set up 18 block
        7)Hit + Set up 16, 15, 14 blocks
        8)Set up 16, 15, 14 blocks
        9)7 block with escaping pieces
        '''
        # Create function that evaluates Stage of Game

        # Create function that takes this Stage input, takes current board pre-roll, post roll boards
        # Evaluates each one based on a structure such as the one above, returns the board with the lowest
        # value. Can make each value relate to an option, better options have lower vals, like a val_dictionary

        # Then the idea is just throw that chosen board into below function to find out which pieces moved where

        print(len(usable_boards))
        return usable_boards         

    def find_moved_pieces(self, board=None):
        '''
        Finds moved piece based on starting and ending locations, for purposes of the visual game
        '''
             
        # starting positions
        self.find_positions()
        starting_dict = self.DICT
        starting_keys = [x for x in self.DICT.keys()]
        
        # for now random comp move moves piece, if board is given, we use that selected board
        if board == None:
            moved_board = self.random_comp_move()
        else:
            moved_board = board    

        # ending position using the random selection board
        self.find_positions(moved_board)
        ending_dict = self.DICT
        ending_keys = [x for x in self.DICT.keys()]
        
        Dice = sorted(self.dice)
        Dice_Sums = []
        if len(Dice)==2:
            Dice_Sums.append(Dice[0])
            Dice_Sums.append(Dice[1])
            Dice_Sums.append(Dice[0]+Dice[1])
        
        if len(Dice)==4:
            for i in range(1,5):
                Dice_Sums.append(i*Dice[0])        
        
        length = len(starting_dict)
        index = 0
        key_vals = []

        while length >0:
            possible_spots = []
            
            key = starting_keys[index]
            count = key

            if self.color == 'white':
                for val in Dice_Sums:
                    count +=val
                    possible_spots.append(count)
                    count = key
            if self.color == 'black':
                for val in Dice_Sums:
                    count -=val
                    possible_spots.append(count)
                    count = key          
            key_vals.append(possible_spots)
            index +=1
            length -=1

        Key_Dict = dict(zip(starting_keys, key_vals))

        Decreased_Keys = []
        for key, val in starting_dict.items():
            for k2, val2 in ending_dict.items():
                if key == k2:
                    if val > val2:
                        for i in range(val-val2):
                            Decreased_Keys.append(key)

        for key in starting_keys:
            if key not in ending_keys:
                for k,v in starting_dict.items():
                    if key == k:
                        for i in range(v):
                            Decreased_Keys.append(k)            
        
        moved_spots = []
        for k,v in starting_dict.items():
            for i,j in ending_dict.items():
                if k == i:
                    if j >v:
                        for i in range(j-v):
                            moved_spots.append(k)
        for key in ending_keys:
            if key not in starting_keys:
                for k,v in ending_dict.items():
                    if k == key:
                        for i in range(v):
                            moved_spots.append(key)
        Decreased_Keys = sorted(Decreased_Keys)
             
        # moved_spots = sorted(moved_spots)
        Moved_List = []
        
        length = len(Decreased_Keys)
        idx = 0
        while length >0:
            curr_key = Decreased_Keys[idx]
            for val in moved_spots:
                for k,v in Key_Dict.items():
                    if curr_key == k:
                        if val in v:
                            moved_spots.remove(val)
                            info = (curr_key,val)
                            break 

            Moved_List.append(info)
            length -=1
            idx+=1            


        return Moved_List

# TODO Make comp select from possible 'random moves' and select based on criteria, 
# Make it Smarter




A = Player()
# making a random possible move and finding pieces that moved
# by feeding in the new board to the find_moved_pieces function
# saving position as new board, running again, to simulate game
print(A.board)
moved_to = A.random_comp_move()
print(moved_to)
print(A.find_moved_pieces(moved_to))

A.board = moved_to

moved_to = A.random_comp_move()
print(moved_to)
print(A.find_moved_pieces(moved_to))






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