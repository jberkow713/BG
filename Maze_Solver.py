import random
import copy 

class Matrix:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows
        self.MAP = self.create_map()

    def create_map(self):
        return [list(random.randint(0,4) for _ in range(self.columns)) for x in range(self.rows)]

  # create algorithm so walls of 0s or connecting to the sides of board are not possible

class Navigator:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows 
        self.MAP = Matrix(columns, rows).MAP
        self.prevent_nonsense()
        self.directions = ['N', 'S', 'E', 'W']
        self.all_p_directions = ['N', 'S', 'E', 'W']
        self.row = 0
        self.col = self.generate_starting_column()
        self.position = self.MAP[self.col][self.row]
        self.direction = None
        self.zero_dict = {}
        self.moves = 0
        self.actual_moves = 0
    
    def prevent_nonsense(self):
        self.MAP[self.columns-1][self.rows-1] = 1
        self.MAP[self.columns-2][self.rows-1]=1    
    
    def generate_starting_column(self):
        
        starting_col = 0
        while self.MAP[0][starting_col]==0:
            starting_col +=1 
        return starting_col 

    def board_check(self,col,row):        
        if col>=0 and col<=self.columns-1:
            if row>=0 and row<=self.rows-1:
                if self.MAP[col][row] == 0:
                    self.zero_dict[(col,row)]=0
                if self.MAP[col][row] !=0:
                    self.directions = copy.deepcopy(self.all_p_directions)
                    return True          
                  
    def Move(self):
        
        if self.direction == None:
            random_dir = self.directions[random.randint(0,len(self.directions)-1)]
            dir, self.direction = random_dir, random_dir

        randomized = random.randint(0,25)
        if randomized>=4:
            dir = self.direction
        elif randomized<4:
            dir = self.directions[random.randint(0,len(self.directions)-1)]
        
        row = self.row
        col = self.col
        
        if dir == 'N':
            row -=1
        elif dir == 'S':
            row +=1
        elif dir == 'E':
            col +=1
        elif dir == 'W':
            col -=1

        if (col,row) in self.zero_dict.keys():
            self.directions.remove(dir)
            if len(self.directions)==0:
                self.directions = copy.deepcopy(self.all_p_directions)
            self.direction = None
            return            

        if self.board_check(col,row)==True:
            self.col = col
            self.row = row
            self.position == self.MAP[self.col][self.row]
            self.actual_moves +=1            
            return
        
        self.directions.remove(self.direction)        
        if len(self.directions)==0:
            self.directions = copy.deepcopy(self.all_p_directions)    
        self.direction = None
        return
    
    def Navigate(self):
        Path = []
        MOVES = 0
        end = self.rows-1, self.rows-1
        while (self.row, self.col)!=end :
            if MOVES >50000:
                print("You are too dumb")                
                break

            self.Move()
            MOVES +=1            
            Path.append((self.row, self.col))
        
        self.moves = MOVES
        self.path = Path


N = Navigator(20,20)
N.Navigate()


if N.moves > 50000:
  print(N.path[-20:-1])
print(N.actual_moves) 
print(N.MAP)    