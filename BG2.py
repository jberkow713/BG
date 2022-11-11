import random

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
        self.dice = None
        self.Comp = Comp
        self.White_Pieces = {}
        self.Black_Pieces = {}
        self.populate_Dict()
        
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
        return
    
    def populate_Dict(self):
        for slot,val in enumerate(self.board):
            if 1 in val:
                self.White_Pieces[slot]=len(val)
            elif 2 in val:
                self.Black_Pieces[slot]=len(val)

P1 = Player('white')
print(P1.White_Pieces, P1.Black_Pieces)                    

                
