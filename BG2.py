import random

class Board:
    def __init__(self):
        self.board = [[],11,0, 0,0,0,22222, 0,222,0,0,0,11111,22222,0,0,0,111,0, 11111, 0,0,0,0,22,[]]

class Player:
    # Players will use the same starting board, and as moves are made, the board will be adjusted
    def __init__(self, color):
        self.color = color
        self.board = Board().board
        self.on_rail = False
        self.dice = None 
    def on_rail(self):
        if self.color == 'white':
            if len(self.board[0])>0:
                self.on_rail=True 
            else:
                self.on_rail=False         
        if self.color == 'black':
            if len(self.board[-1])>0:
                self.on_rail =True
            else:
                self.on_rail=False
    def roll(self):
        die_1 = random.randint(1,6)
        die_2 = random.randint(1,6)
        if die_1 == die_2:
            self.dice= [die_1] * 4
        else:
            self.dice= [die_1,die_2]
P = Player('white')
P.roll()
print(P.dice)                
