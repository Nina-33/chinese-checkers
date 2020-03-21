class Player(object): 
    def __init__(self,name,color,moves,homeRange,isAI): 
        self.name = name
        self.color = color
        self.moves = moves #number of moves taken
        self.win = False 
        self.homeRange = homeRange# tuple of homebase row range
        self.isAI = isAI

class marble(object): 
    def __init__(self,x,y,r,c): 
        self.x = x 
        self.y = y 
        self.r = r #radius
        self.c = c #color 

    def __repr__(self): 
        return f'{self.c} marble'

    def draw(self,canvas): 
        x0 = self.x - self.r 
        x1 = self.x + self.r
        y0 = self.y - self.r 
        y1 = self.y + self.r  
        canvas.create_oval(x0, y0,x1,y1,fill=self.c)
