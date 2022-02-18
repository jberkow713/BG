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
            print('taking off')
            
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
        #TODO 
        # Going to find all possible moves using this function, and store it in self.moves
        # {1: 2, 12: 5, 17: 3, 19: 5} {6: 5, 8: 3, 13: 5, 24: 2} [6, 3]
        
        # copy board to reference back to 
        self.saved_board = copy.deepcopy(self.board)
                       
        self.find_positions()
        self.can_take_off()
        self.roll()
        print(self.dice)
        board_states = []
        
        
        # TODO Make this work for doubles 
        # ------------------------------------------------------------
        print(self.board)
        
        if len(self.dice)==4:            
            
            # LEN = len(self.dice)
            
            # while LEN >0:
            Current_Boards = []
            keys = [x for x in self.DICT.keys()]
            opp_keys = [x for x in self.opp_Dict.keys()]
            
            # [[],3 , 0 ,0 , 0,0 , 55555, 0, 555, 0, 0, 0, 33333, 55555, , 0, 0, 333, 0, 33333, 0, 0, 0, 0, 55, []]
            
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
                
                if CAN_MOVE == True:                        
                            
                    self.move_piece(key, spot)                          
                    # recalculate positions based on moved piece
                                       
                    # Save board state here
                    current_board = copy.deepcopy(self.board)
                    Current_Boards.append(current_board)
                    self.board = copy.deepcopy(self.saved_board) 
                    
                idx +=1
                LENGTH -=1

            print(Current_Boards)
            Roll_2_Boards = []

            for board in Current_Boards:
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
                        
                        self.move_piece(key, spot, board)                          
                        # recalculate positions based on moved piece
                                        
                        # Save board state here
                        Roll_2_Boards.append(board)


                    board = current_board    

                    idx +=1
                    LENGTH -=1
            print(Roll_2_Boards)    
        
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
                    
                        print(key,spot)
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
                                    # print(self.board)

                            idx2 +=1
                            LENGTH_2 -=1
                            self.board = copy.deepcopy(current_board)

                    self.board = copy.deepcopy(self.saved_board)    

                    idx +=1
                    LENGTH -=1
                
                IDX+=1
                LEN -=1
        return board_states   

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
    def Terminator_Move(self):
        pass
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

# TODO add pip_count component for each color
# improve brain, make computer look for specific blocks to make,
# make computer look for consecutive blocks, and blocks certain distance from opponent 
# prioritize blocks in its own space, etc...
# learning how to switch gears, based on pip count vs opponent pip count, whether to be 
# aggressive or not
# end game, intelligent taking off of pieces, depending on where opponent is

a = Player()

spots = a.update_reality()

print(spots)

# b = Player('white', BRD)
# b.random_comp_move()
# print(b.board)

# print(a.pip_count())
# print(a.consec_blocks())
# print(a.find_single_blocks())
# print(a.find_furthest_back())

# print(a.find_all_moves())



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