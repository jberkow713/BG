import numpy as np
import random 
import pygame as p
from pygame.constants import MOUSEBUTTONDOWN
import sys
import itertools
import copy

class Board:
    def __init__(self):
        self.board = [[],[1,1],[], [],[],[],[2,2,2,2,2], [],[2,2,2],[],[],[],[1,1,1,1,1],\
            [2,2,2,2,2],[],[],[],[1,1,1],[], [1,1,1,1,1], [],[],[],[],[2,2],[]]

class Player:
    # Players will use the same starting board, and as moves are made, the board will be adjusted
    def __init__(self, color,Comp=False):
        self.color = color
        self.board = Board().board
        self.on_rail = False
        self.can_remove = False
        self.dice = None
        self.Comp = Comp
        self.White_Pieces = {}
        self.Black_Pieces = {}
        self.populate_Dict()
        self.moves = []
        
    def rail_check(self):
        # Determines if player moving has a piece on the rail
        if self.color == 'white':
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
            self.dice= [die_1] * 4
        else:
            self.dice= [die_1,die_2]
        return
    
    def populate_Dict(self):
        # Populates the piece dictionary for white and black
        for slot,val in enumerate(self.board):
            if 1 in val:
                self.White_Pieces[slot]=len(val)
            elif 2 in val:
                self.Black_Pieces[slot]=len(val)
    
    def blocked(self,spot):
        # checks if a spot is blocked for a given color
        if self.color == 'white':
            if spot in self.Black_Pieces:
                if self.Black_Pieces[spot]>1:
                    return True
            return False      
        if self.color =='black':
            if spot in self.White_Pieces:
                if self.White_Pieces[spot]>1:
                    return True
            return False     
    
    def spot_open(self, spot):
        # Checks if a spot is open
        if self.color =='white':
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

    def calc_moves(self,start):
        # individual check from starting position
        # adds all movable spots to players self.moves list
        for die in self.dice:
            if self.color =='white':
                end = start + die                
            elif self.color =='black':
                end = start-die
            if self.spot_open(end)==True:
                self.moves.append(end)
        print(self.dice)
        print(self.moves)
        return

P1 = Player('white')
print(P1.White_Pieces, P1.Black_Pieces)
P1.roll()
P1.calc_moves(1)
P1.rail_check()
print(P1.on_rail)




                
