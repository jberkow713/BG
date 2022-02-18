from curses import A_HORIZONTAL
import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
import itertools
import copy

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
    def __init__(self):
        self.board = self.create_board()
    def create_board(self):
        # board = [[],0,555,55,55,555,55555,0,0,0,0,0,0,0,0,0,0,0,0,33333,333,33,333,33,0,[]]
        board = [[],33,0, 0,0,0,55555, 0,555,0,0,0,33333,55555,0,0,0,333,0, 33333, 0,0,0,0,55,[]]
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
    def consec_blocks(self, colors=None):
        
        self.find_positions()
        
        if self.color=='white':
            WHITE = self.DICT
            BLACK = self.opp_Dict
        else:
            BLACK=self.DICT
            WHITE=self.opp_Dict
        if colors==None:
            return consec_pairs(WHITE), consec_pairs(BLACK)   
        else:
            if colors=='white':
                return consec_pairs(WHITE)
            elif colors=='black':
                return consec_pairs(BLACK)         
    
    def find_single_blocks(self):
        multiple = self.consec_blocks()
        multiple_white = multiple[0]
        multiple_black = multiple[1]
        if self.color == 'white':
            WHITE = self.DICT
            BLACK = self.opp_Dict
        else:
            BLACK=self.DICT
            WHITE = self.opp_Dict

        single_white = []
        single_black = []
        for k,v in WHITE.items():
            if v >1:
                for x in multiple_white:
                    if k not in x:
                        single_white.append(k)
        for k,v in BLACK.items():
            if v >1:
                for x in multiple_black:
                    if k not in x:
                        single_black.append(k)

        return single_white, single_black

    def pip_count(self):
        self.find_positions()
        # {1: 3, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1} {19: 2, 20: 3, 21: 3, 22: 2, 23: 2, 24:2}
        if self.color=='white':
            WHITE = self.DICT
            BLACK = self.opp_Dict
        else:
            BLACK=self.DICT
            WHITE=self.opp_Dict
        white_pip = [0, 'white_pips']
        for k,v in WHITE.items():
            diff = 25-k
            white_pip[0] +=diff*v
        black_pip = [0, 'black_pips']
        for k,v in BLACK.items():
            diff = 0+k
            black_pip[0] +=diff*v
        return white_pip, black_pip
    
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
        
        if isinstance(board[TO], list)==True:
                        
            if len(str(board[FROM]))>1:
                curr = str(board[FROM])[1:]
                board[FROM]= int(curr)
                return
            else:
                board[FROM]=0
                return                             
        
        starting= board[FROM]
        
        if isinstance(starting, list)==True:
            starting = int(starting[0])

        if len(str(starting)[1:])>0:            
            remaining= int(str(starting)[1:])
        
        else:
            remaining = 0    
        moved = int(str(starting)[0])
                
        board[FROM]=remaining

        ending = board[TO]
        # For a hit
        if moved !=int(str(board[TO])[0]):
            if self.color =='white':
                if board[TO]!=0:
                    board[-1].append(ending)
                board[TO] = moved
                
                return  
            elif self.color =='black':
                if board[TO]!=0:
                    board[0].append(ending)
                board[TO]= moved
                return 
        # For Stacking pieces
        if moved == int(str(board[TO])[0]):
            curr = str(ending)
            mov = str(moved)
            board[TO]= int(curr+mov)
    
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
    
    def update_reality(self):
        '''
        Finds all possible board states for a given roll, stores them in self.board_states
        '''
        self.saved_board = copy.deepcopy(self.board)                       
        self.find_positions()
        self.can_take_off()
        self.roll()
        print(self.dice)        
        board_states = []              
        
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
            print(len(self.board_states))
            return               
                
        # TODO finish for rolls 3 and 4, and rolls 4 is ALL board states for doubles!
        if len(self.dice)==2:                            
            
            keys = [x for x in self.DICT.keys()]
            opp_keys = [x for x in self.opp_Dict.keys()]            
                    
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
    def find_optimal_board(self):
        # Finding all possible moves
        self.update_reality()
        Possible_Boards = self.board_states
        # TODO evaluating all possible board states for optimal value
        # want to return that board as output
        return Possible_Boards
    
    def random_comp_move(self):
        self.update_reality()
        random_board = self.board_states[random.randint(0,len(self.board_states)-1)]
        self.board = random_board
        return

A = Player()

A.random_comp_move()
print(A.board)



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