# idea for node class and minimax function referenced 
# from https://www.youtube.com/watch?v=fInYh90YMJU 
class Node(object): 
    def __init__(self,depth,state,move1,score): 
        self.depth = depth
        self.state = state
        self.move1 = move1 # list of the orgininal (row,col) of marble moved
                               # and where the marble is moved to in (row,col)
        self.score = score
        self.childrens = []
        
    def addChild(self,child): 
        self.childrens.append(child)
    
    def __repr__(self): 
        return (f'depth: {self.depth} score: {self.score} move1: {self.move1}')