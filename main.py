############################################################################
# 15-112 Term Project: Chinese Checkers 
# Name: Jiatong (Nina) Li 
# Andrew ID: jiatong3
############################################################################

#Board image used: https://www.ymimports.com/pages/how-to-play-chinesse-checkers 
#Congratulation image used: http://nyaeyc.org/wp-content/uploads/congrats.jpg 
#Wooden background image used: https://images.fineartamerica.com/images-medium-large-5/brown-wooden-table-background-anilakkus.jpg 
# lost image used: https://opengameart.org/sites/default/files/sorryyouloststamp.png 
import math, copy, random, pygame, os, decimal, string
# cmu_112_graphics.py taken from http://www.cs.cmu.edu/~112/notes/notes-animations-part1.html 
from cmu_112_graphics import *
from tkinter import *
from pygame.locals import *
from State import State, GamePosition
from Node import Node
from Player import Player
from Marble import marble
####################################################################
#RoundHalfUp taken from 112 homework built-ins 
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

class PlayerVsAiMode(Mode):
    def appStarted(mode):
        #create background 
        backgroundURL = ('background.jpg')
        mode.backgroundImage = mode.loadImage(backgroundURL)

        #create board 
        boardURL = ('board.png')
        boardImage = mode.loadImage(boardURL)
        mode.boardImageScaled = mode.scaleImage(boardImage,4/7)

        #create congrats image 
        congratsURL = ('congrats.png')
        congratsImage = mode.loadImage(congratsURL)
        mode.congratsImageScaled = mode.scaleImage(congratsImage,1/5)

        #create lost image 
        lostURL = ('lost.png')
        lostImage = mode.loadImage(lostURL)
        mode.lostImageScaled = mode.scaleImage(lostImage,1/5)

        #create player playing dot 
        mode.player1_dot = marble(mode.width/2,20,8,'yellowgreen')
        mode.player2_dot = marble(mode.width/2,580,8,'lightcoral')

        #create settings image 
        settingsURL = ('settings.png')
        settingsImage = mode.loadImage(settingsURL)
        mode.settingsImageScaled = mode.scaleImage(settingsImage,1/20)

        #create list of empty board 
        startBoard = [                          ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
        ]

        #load the top triangle with green marbles
        for row in range(4): 
            for col in range(len(startBoard[row])): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of every marble
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'green')
                startBoard[row][col] = newMarble

        #load the bottom triangle with red marbles 
        for row in range(13,17): 
            for col in range(len(startBoard[row])): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[row][col] = newMarble

        #print(startBoard)
        mode.player1 = Player('AI','green',0,(13,16),True)
        mode.player2 = Player('Player 2','red',0,(0,3),False)
        mode.state = GamePosition(startBoard,mode.player1)

        #initially, no marble is selected
        mode.marbleObjectSelected = None 
        mode.originalMarblePosition = None # original x and y coordinate of marble 
        mode.marblePositionSelected = (-1,-1) #original row and col of marble selected 
        mode.legalMoves = None
        mode.inIllegalMove = False 

        #initiate show hint
        mode.showHint = False 
        mode.possibleMoves = None 

        #initiate background on 
        mode.backgroundOn = False

        #set up winner 
        mode.winner = None 

        #set inSettings to false 
        mode.inSettings = False

        #leaderboard Properties 
        mode.askForName = True 
        mode.name = ''
        mode.rank = 1

    def timerFired(mode): 
        if mode.winner == None: 
            #AI's turn
            if mode.state.playerPlaying.isAI: 
                # let AI do its move 
                mode.AImove(mode.state)

                #check for win 
                if mode.isSolutionState(mode.state,mode.player1): 
                    mode.winner = mode.player1

                # change player playing
                mode.state.playerPlaying = mode.player2  

    # retrun True if a given state is a solution state for the given player, 
    # otherwise return False  
    def isSolutionState(mode,state,player): 
        startRowRange, endRowRange = player.homeRange 
        #loop through every spot in the current player's home base 
        for row in range(startRowRange,endRowRange+1): 
            for col in range(len(state.board[row])): 
                # if the spot is empty, return false 
                if state.board[row][col] =='-': 
                    return False
                # if the spot is not filled up with the player's marble, return False
                elif state.board[row][col].c != player.color: 
                    return False
        return True 

    def keyPressed(mode,event): 
        #cheat test case: end case 
        if mode.winner == None: 
            if event.key == 'e':
                print('In end state')
                #clear board 
                startBoard = [                  ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
                ]

                
                #fill in green's home base except 1 (red)
                for row in range(13,17): 
                    for col in range(len(startBoard[row])): 
                        if row == 13 and col == 0: 
                            startBoard[row][col] = '-'
                        else: 
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'green')
                            startBoard[row][col] = newMarble
                
                #move 1 marble off the home base 
                x = mode.width/2 - (len(startBoard[12])-1)*16.5 + 32.9 * 4 #center x of the every marble 
                y = 70 + 12*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'green')
                startBoard[12][4] = newMarble
                
                #fill in red's home base except 1 (green)
                #loop through every spot in the current player's home base 
                for row in range(0,4): 
                    for col in range(len(mode.state.board[row])): 
                        if row == 3 and col== 0: 
                            startBoard[13][0] = '-'
                        else:
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'red')
                            startBoard[row][col] = newMarble
                
                # move 1 marble off the home base
                x = mode.width/2 - (len(startBoard[4])-1)*16.5 + 32.9 * 4 #center x of the every marble 
                y = 70 + 4*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[4][4] = newMarble

                mode.state.board = startBoard 
        else: #game over mode
            if mode.winner == mode.player2: 
                if mode.askForName: 
                    if event.key in string.ascii_letters: 
                        mode.name += event.key
                    elif event.key == 'Delete': 
                        mode.name = mode.name[:-1]
                    elif event.key == 'Enter': 
                        mode.askForName = False 

                        # create updated leaderboard by looping through every line 
                        # in the original leaderboard and inserting new score at right 
                        # position 
                        mode.leaderboard= open("leaderboard.txt","rt")
                        oldContents = mode.leaderboard.read() #get old content 
                        print('old contents',oldContents)

                        newContents = ''
                        scoreStored = False
                        if oldContents == '': 
                            newContents += f'{mode.name}    {mode.winner.moves}\n'
                        else:
                            for line in oldContents.splitlines(): 
                                score = ''
                                for c in line: 
                                    if c.isdigit(): 
                                        score += c 
                                score = int(score)
                                print('score',score)
                                if score < mode.winner.moves: 
                                    newContents += line + '\n'
                                    mode.rank += 1 
                                elif score >= mode.winner.moves and scoreStored == False: 
                                    newContents += f'{mode.name}    {mode.winner.moves}\n'
                                    newContents += line + '\n'
                                    scoreStored = True
                                elif score >= mode.winner.moves and scoreStored: 
                                    newContents += line + '\n'
                            if scoreStored == False: 
                                newContents += f'{mode.name}    {mode.winner.moves}\n'

                        print ('new contents', newContents)
                        #close leaderboard
                        mode.leaderboard.close()

                        # open file for writing 
                        mode.leaderboard= open("leaderboard.txt","wt") 

                        #clear the leaderboard
                        mode.leaderboard.seek(0)
                        mode.leaderboard.truncate()

                        #rewrite the leaderboard
                        (mode.leaderboard).write(newContents)

                        #close leaderboard
                        mode.leaderboard.close()

    def mousePressed(mode,event): 
        if mode.winner == None: # if game is not over yet
            # reset inIllegalMove
            mode.inIllegalMove = False

            #selects a marble given click 
            mode.marbleObjectSelected = mode.getMarbleObject(event.x,event.y)
            mode.marblePositionSelected = mode.getMarblePosition(event.x,event.y)
            
            # if a marble is selected and show hint is turned on, store the legal moves
            # for drawing 
            if mode.marbleObjectSelected != None and mode.showHint: 
                row,col = mode.marblePositionSelected
                mode.possibleMoves = mode.getLegalMoves(mode.state,row,col)

            #if setting is clicked on 
            if (535<=event.x<=600) and (0<= event.y<=60): 
                mode.inSettings = True 
            
            #buttons to click in settings 
            if mode.inSettings: 
                if (160<=event.x<=200) and (140<=event.y<=180): #show hints
                    mode.showHint = not (mode.showHint)
                elif (160<=event.x<=200) and (250<=event.y<= 290): #show background 
                    mode.backgroundOn = not (mode.backgroundOn)
                elif (160 <=event.x<=440) and (360 <= event.y<= 410): #return to game 
                    mode.inSettings = False 
                elif (160 <= event.x <=440) and (470<= event.y<=520):#return to home
                    mode.appStarted()
                    mode.app.setActiveMode(mode.app.openingMode) 

        else: # game over screen
            if (150<event.x<450) and (500<event.y<540): 
                mode.appStarted()
                mode.app.setActiveMode(mode.app.openingMode)
    
    # View to modal: takes in coordinate of mouse pressed and return marble object  
    # if the marble selected belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # return None
    def getMarbleObject(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            mode.originalMarblePosition = (marble.x,marble.y) #store the marble's original position as a tuple
                            return marble
        return None

    # View to modal: takes in coordinate of mouse pressed and return (row,col) of 
    # the marble selected if it belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # (-1,-1) is returned. 
    def getMarblePosition(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            return (row,col)
        return (-1,-1)

    def mouseDragged(mode, event):
        if (mode.marbleObjectSelected != None): 
            mode.marbleObjectSelected.x = event.x 
            mode.marbleObjectSelected.y = event.y 

    #model to view: convert x and y coordinate into row and col 
    # (-1,-1) is returned if not on board
    def getRowCol(mode,x,y): 
        row = roundHalfUp((y - 70)/28.5) 
        col = roundHalfUp((x - mode.width/2 + ((len(mode.state.board[row]))-1)*16.5)/32.9)
        if (0<= row <=16) and (0<= col <= len(mode.state.board[row])-1): 
            return (row,col)
        return (-1,-1)

    # if marble is not released in a new position on board, 
    # then it would return back to its original position 
    # else if the marble is released onto a legal position on board, 
    # its original position would become empty and the new position will 
    # now consist of the marble 
    def mouseReleased(mode,event):
        #clear hint 
        mode.possibleMoves = None 

        #release marble only if one is selected
        if mode.marbleObjectSelected != None:
            oldRow, oldCol = mode.marblePositionSelected 
            newRow, newCol = mode.getRowCol(event.x,event.y)

            #get all the legal moves of the piece 
            legalMoves = mode.getLegalMoves(mode.state,oldRow,oldCol)
            # if marble is released onto a legal and empty position
            if (newRow,newCol) in legalMoves: 
                #compute centre x and y of the empty position 
                x = mode.width/2 - (len(mode.state.board[newRow])-1)*16.5 + 32.9 * newCol 
                y = 70 + newRow*28.5 
                #set the x and y centre of marble to the centre of the empty position 
                mode.marbleObjectSelected.x = x 
                mode.marbleObjectSelected.y = y 

                #empty the original position of marble on board
                mode.state.board[oldRow][oldCol] = '-'
                #place object on new board position 
                mode.state.board[newRow][newCol] = mode.marbleObjectSelected

                #increase current player's move by 1 
                mode.state.playerPlaying.moves += 1 

                #check for win 
                if mode.isSolutionState(mode.state,mode.state.playerPlaying): 
                    mode.winner = mode.state.playerPlaying

                #change player's turn 
                if mode.state.playerPlaying == mode.player1: 
                    mode.state.playerPlaying = mode.player2
                elif mode.state.playerPlaying == mode.player2: 
                    mode.state.playerPlaying = mode.player1 
                return 

            #if not released onto a legal and empty position, return marble to original position
            else: 
                mode.inIllegalMove = True #set inIllegalMove to True
                originalX, originalY = mode.originalMarblePosition
                mode.marbleObjectSelected.x = originalX
                mode.marbleObjectSelected.y = originalY 

            #unselected marble 
            mode.marbleObjectSelected = None 
            mode.originalMarblePosition = None
            mode.marblePositionSelected = (-1,-1)
        
        #print(mode.state.board)

    #returns a set of legal position in format (row, col) that the marble can move to  
    # given the orginal state and marble position in (row,col)
    # 2 cases a move is legal: 1. adjacent and empty 
    #                          2. adjacent is not empty but the one after in the same direction is 
    def getLegalMoves(mode, state, row, col): 
        legalMoves = set()
        #move to left 
        if mode.getLeft(state,row,col) != None:
            newRow, newCol = mode.getLeft(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add((newRow,newCol))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state, newRow,newCol,'left',seenPositions, possibleJumps) != None: 
                    for move in mode.getJump(state,newRow,newCol,'left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
        
        #move to right 
        if mode.getRight(state,row,col) != None: 
            newRow, newCol = mode.getRight(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getRight(state,row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state,newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to upper left
        if mode.getUpperLeft(state,row,col) != None:
            newRow, newCol = mode.getUpperLeft(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperLeft(state,row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state,newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
                
        #move to upper right 
        if mode.getUpperRight(state,row,col) != None:
            newRow, newCol = mode.getUpperRight(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperRight(state,row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state,newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom left
        if mode.getBottomLeft(state,row,col) != None:
            newRow, newCol = mode.getBottomLeft(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomLeft(state,row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state,newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom right
        if mode.getBottomRight(state,row,col) != None:
            newRow, newCol = mode.getBottomRight(state,row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomRight(state,row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(state,newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        return legalMoves 

    #GET LEGAL MOVE HELPERS 
    #returns the position left to given row, col in a tuple of (row,col) if it exists 
    def getLeft(mode,state,row,col): 
        if (col > 0): 
            return (row,col-1)
        else: 
            return None 
        
    #returns the position right to given row, col in a tuple of (row,col) if it exists 
    def getRight(mode,state,row,col): 
        if (col < len(state.board[row])-1): 
            return (row,col+1)
        else: 
            return None 

    def getUpperLeft(mode,state,row,col): 
        #col decreasing case 
        if (1<=row<=3) or (9<=row<=12): 
            if (row-1>= 0) and (col-1>=0):
                return (row-1,col-1)
        #col constant case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col)
        #special cases 
        elif (row == 4): 
            if (5<= col<=8): 
                return (row-1,col-5)
        elif (row == 13): 
            return (row-1,col+4)
        else: 
            return None 

    def getUpperRight(mode,state,row,col): 
        #col constant case 
        if (1<=row<=3) or (9<=row<=12):
            if col <= (len(state.board[row-1])-1): 
                return (row-1,col)
        # col increase case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col+1)
        #special cases 
        elif (row==4): 
            if (4<=col<=7): 
                return (row-1,col-4)
        elif (row==13): 
            return (row-1,col+5)
        else: 
            return None

    def getBottomLeft(mode,state,row,col): 
        #col constant case
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col)
        #col decreasing case 
        elif (4<= row<=7) or (13<=row<=15): 
            if (col-1 >= 0): 
                return (row+1,col-1)
        #special cases 
        elif (row == 3): 
            return (row+1,col+4)
        elif (row == 12) and (5<=col<=8): 
            return (row+1,col-5)
        else: 
            return None

    def getBottomRight(mode,state,row,col): 
        #col increasing case 
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col+1)
        #col constant case 
        elif (4<=row<=7) or (13<=row<=15): 
            if (col+1<=len(state.board[row+1])): 
                return (row+1,col)
        #special cases 
        elif (row == 3): 
            return (row+1,col+5)
        elif (row == 12) and (4<=col<=7): 
            return (row+1,col-4)
        else: 
            return None

    #TO DO: GET JUMP RECURSION 
    # return None if no jump is avaliable, else return a list of possible jumps 
    def getJump(mode, state,marbleRow,marbleCol,direction,seenPositions, possibleJumps): 
        if direction =='left': 
            #if there is an adjacent left 
            if mode.getLeft(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getLeft(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and ((newRow,newCol) not in seenPositions):
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='right': 
            #if there is an adjacent right 
            if mode.getRight(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getRight(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='upper left': 
            #if there is an adjacent upper Left 
            if mode.getUpperLeft(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperLeft(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'upper right': 
            #if there is an adjacent upper right
            if mode.getUpperRight(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperRight(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom left': 
            #if there is an adjacent bottom left
            if mode.getBottomLeft(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomLeft(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom right': 
            #if there is an adjacent bottom right
            if mode.getBottomRight(state,marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomRight(state,marbleRow,marbleCol)
                #if adjacent position is empty 
                if state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(state,newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(state,newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        #print('seen positions in getJump:',seenPositions)
        #print ('possible jumps in getJump:',possibleJumps)
        if (len(possibleJumps) == 0): 
            return None
        else:
            return possibleJumps 

    # given the position of an empty row and col (the new position from a previous jump), 
    # check if there are any marbles adjacent to the new position that the player can jump over 
    # if there is, call on getJump 
    def getNextJump(mode,state,row,col,seenPositions,possibleJumps): 
        #check if adjacent left exists
        if mode.getLeft(state,row,col) != None:
            newRow, newCol = mode.getLeft(state,row,col)
            #if adjacent left contains marble (regardless of color)
            if state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(state,newRow,newCol,'left',seenPositions,possibleJumps) != None: 
                    for move in mode.getJump(state,newRow,newCol,'left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
        
        #check if adjacent right exists 
        if mode.getRight(state,row,col) != None: 
            newRow, newCol = mode.getRight(state,row,col)
            #if adjacent left contains marble (regardless of color)
            if state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(state,newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if upper left exists 
        if mode.getUpperLeft(state,row,col) != None:
            newRow, newCol = mode.getUpperLeft(state,row,col)
            #if adjacent upper left contains marble (regardless of color)
            if state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(state,newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
                
        #check if upper right exists 
        if mode.getUpperRight(state,row,col) != None:
            newRow, newCol = mode.getUpperRight(state,row,col)
            #if adjacent upper right contains marble (regardless of color)
            if state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(state,newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if bottom left exists
        if mode.getBottomLeft(state,row,col) != None:
            newRow, newCol = mode.getBottomLeft(state,row,col)
            #if adjacent bottom left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(state,newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #move to bottom right
        if mode.getBottomRight(state,row,col) != None:
            newRow, newCol = mode.getBottomRight(state,row,col)
            #if adjacent bottom right contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(state,newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(state,newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #print('seen positions in getNextJump:',seenPositions)
        #print ('possible jumps in getNextJump:',possibleJumps)

        if len(possibleJumps) == 0: 
            return None
        else: 
            return possibleJumps

    #VIEW    
    def redrawAll(mode, canvas):
        if mode.winner == None:
            #draw background (if background is on)
            if mode.backgroundOn: 
                canvas.create_image(mode.width/2,mode.height/2, 
                image=ImageTk.PhotoImage(mode.backgroundImage))

            # draw player playing dot 
            if mode.state.playerPlaying == mode.player1:
                mode.player1_dot.draw(canvas) 
            else: # player 2 is playing 
                mode.player2_dot.draw(canvas)

            #draw board
            canvas.create_image(mode.width/2, mode.height/2, 
            image=ImageTk.PhotoImage(mode.boardImageScaled))

            #draw settings 
            canvas.create_image(570, 30, 
            image=ImageTk.PhotoImage(mode.settingsImageScaled))

            # if show hint is on and there are possible moves, draw out possible moves 
            if mode.showHint == True and mode.possibleMoves != None: 
                for row, col in mode.possibleMoves: 
                    x = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + 32.9 * col #center x of every marble
                    y = 70 + row*28.5 #centre y of every marble
                    r = 7
                    canvas.create_oval(x-7,y-7,x+8,y+8,fill='Grey')

            #draw marble  
            for row in range(len(mode.state.board)): 
                for col in range(len(mode.state.board[row])): 
                    if mode.state.board[row][col] != '-': # must be a marble 
                        marble = mode.state.board[row][col]
                        marble.draw(canvas)
            
            # draw illegal move message (when player conducts illegal move)
            if mode.inIllegalMove: 
                canvas.create_text(460,80,text='Opps! That\'s an illegal move!')

            #draw P1 moves 
            canvas.create_rectangle(0,0,90,50,outline = 'LemonChiffon2',fill='LemonChiffon2')
            canvas.create_polygon(91,0,91,50,120,0,fill='LemonChiffon2')
            canvas.create_text(50,25,text=f'Moves: {mode.player1.moves}')

            #draw P2 moves 
            canvas.create_rectangle(510,550,600,600,outline = 'MistyRose2',fill='MistyRose2')
            canvas.create_polygon(511,600,511,550,480,600,fill='MistyRose2')
            canvas.create_text(545,575,text=f'Moves: {mode.player2.moves}')

            #if user clicked on settings, draw settings page 
            if mode.inSettings: 
                canvas.create_rectangle(0,0,600,600,fill='white')
                #Title
                canvas.create_text(mode.width/2,60, 
                fill= 'Grey',font = 'Ayuthaya 40',text='Settings')

                #show hint 
                if mode.showHint: 
                    canvas.create_rectangle(160,140,200,180,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,140,200,180,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 20 ,160, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Show Hints')
                
                #draw background 
                if mode.backgroundOn: 
                    canvas.create_rectangle(160,250,200,290,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,250,200,290,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 40, 275, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Draw Background')

                #return to game button
                canvas.create_rectangle(160,360,440,410,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,385, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Game')

                #return to home screen button
                canvas.create_rectangle(160,470,440,520,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,495, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Home')
        else: 
            #only display congrats and leaderboard if human player wins 
            if mode.winner == mode.player2: 
                # create congrats image
                canvas.create_image(mode.width/2, 80, 
                image=ImageTk.PhotoImage(mode.congratsImageScaled))

                #create winning text
                canvas.create_text(220,180, fill= 'Grey',font = 'Ayuthaya 20',
                    text=f'''
                    {mode.winner.name} won with {mode.winner.moves} moves!
                    ''')

                #ask for name 
                canvas.create_text(220,180, fill= 'Grey',font = 'Ayuthaya 20',
                    text=f'''
                    {mode.winner.name} won with {mode.winner.moves} moves!
                    ''')

                #type out name 
                canvas.create_text(220,210, fill= 'Grey',font = 'Ayuthaya 20',
                    text=f'''
                    {mode.winner.name}\'s name: {mode.name}
                    ''')

                # display leaderboard 
                leaderboard = open("leaderboard.txt","rt")
                contents = leaderboard.read()
                top5 = ''
                lineNum = 0

                for line in contents.splitlines(): 
                    top5 += line + '\n'
                    lineNum += 1
                    if lineNum >=5: 
                        break 
                        
                canvas.create_text(mode.width/2,240,fill='Grey',font='Ayuthaya 20', 
                                    text=f'{mode.name} ranks {mode.rank}!')
                canvas.create_text(mode.width/2-200,300,fill='Grey', font='Ayuthaya 20',
                                    text = '''
                                    Leaderboard 
                                    Name    Ranking
                                    ''')

                canvas.create_text(mode.width/2-40,430,fill= 'Grey',font = 'Ayuthaya 20',
                                    text = top5)
                

                #create return button
                canvas.create_rectangle(150,500,450,540,outline='Grey',width=3)
                canvas.create_text(mode.width/2,520,font = 'Ayuthaya 20',text='Return to Home Page',fill='Grey')

            else: #if computer wins, display loosing statement 
                # create lost image
                canvas.create_image(mode.width/2, 140, 
                image=ImageTk.PhotoImage(mode.lostImageScaled))

                #create return button
                canvas.create_rectangle(150,500,450,540,outline='Grey',width=3)
                canvas.create_text(mode.width/2,520,font = 'Ayuthaya 20',text='Return to Home Page',fill='Grey')

    #AI RELATED FUNCTIONS 

    #return the legal moves the AI is allowed to make with a marble given 
    # the state and the row and col of the marble 
    def getLegalMovesAI(mode, state, marble,row, col): 
        legalMoves = mode.getLegalMoves(state,row,col)
        AIlegalMoves = set()
        # AI legal moves consist of only forward moves for a given marble
        # and assume the player does the same 
        for newRow, newCol in legalMoves: 
            # green marble should jump towards red base
            if marble.c == 'green':  
                #if row == 12: 
                    #print('newRow green', newRow, 'row green', row)
                if newRow >= row:
                    AIlegalMoves.add((newRow,newCol)) 
            # red marble should only jump toward green base 
            elif marble.c == 'red': 
                if newRow <= row: 
                    AIlegalMoves.add((newRow,newCol))
        if marble.c == 'green' and ((13,0) in AIlegalMoves):
            print('AIlegalMoves',AIlegalMoves)
        return AIlegalMoves

    def create_children(mode, root, curDepth, maxDepth, move1): 
        if curDepth == 0: #create depth 1 (special case because move 1 is generated)
            for row in range(len(root.state.board)): 
                for col in range(len(root.state.board[row])): 
                    if root.state.board[row][col] != '-': 
                        marble = root.state.board[row][col]
                        if marble.c == mode.player1.color: 
                            # get the legal moves of the marble that belongs to the AI (depth 1 always belong to AI)
                            moves = mode.getLegalMovesAI(root.state,marble,row,col) 
                            # create a new node from every possible move
                            for newRow, newCol in moves: 
                                    #store move1 
                                    move1 = [(row,col),(newRow,newCol)]
                                    #create a copy of the current state 
                                    boardCopy = copy.deepcopy(root.state.board)
                                    playerPlayingCopy = copy.copy(root.state.playerPlaying)
                                    newState = GamePosition(boardCopy,playerPlayingCopy)

                                    # do the move on the newState copy
                                    move = [(row,col),(newRow,newCol)]
                                    mode.doMove(newState,marble,row,col,newRow,newCol) #destructive modify newState 

                                    # evaluate score only when you have reached the desired depth (maxDepth)
                                    # or reached the end case
                                    if mode.isSolutionState(newState,mode.player1): 
                                        print ('entered desired case')
                                        score = mode.evaluate(root.state, newState, move)
                                    elif curDepth >= maxDepth : 
                                        score = mode.evaluate(root.state, newState, move)
                                    else: 
                                        score = None 
                                    
                                    if score == 1e500: 
                                        print(f'new child at depth {curDepth+1}: {move1},{score}')

                                    newChild = Node(curDepth+1,newState,move1,score)
                                    #add newChild to root 
                                    root.addChild(newChild)

                                    if curDepth < maxDepth: # if the desired depth haven't been reached 
                                        if score!=1e500: 
                                            #create the next depth by recursion
                                            #print("I call create_children with depth", curDepth + 2)
                                            mode.create_children(newChild, curDepth+2, maxDepth, move1)
        else: 
            #print('entered recursion')
            #print(root.state.board)
            for row in range(len(root.state.board)): 
                for col in range(len(root.state.board[row])): 
                    if root.state.board[row][col] != '-': 
                        marble = root.state.board[row][col]
                        #alternate player's turn depending on the depth (depth 1 AI, depth 2 human...so on)
                        if curDepth %2 == 1: # odd depth for AI
                            color = mode.player1.color
                        else: #even depth for human
                            color = mode.player2.color 
                        #if the marble belongs to the player 
                        if marble.c == color: 
                            moves = mode.getLegalMovesAI(root.state,marble,row,col) 
                            # create a new node from every possible move
                            for newRow, newCol in moves: 
                                #create a copy of the current state 
                                boardCopy = copy.deepcopy(root.state.board)
                                playerPlayingCopy = copy.copy(root.state.playerPlaying)
                                newState = GamePosition(boardCopy,playerPlayingCopy)

                                # do the move on the newState copy
                                move = [(row,col),(newRow,newCol)]
                                mode.doMove(newState,marble,row,col,newRow,newCol) #destructive modify newState 

                                # evaluate score only when you have reached the desired depth (maxDepth)
                                # or reached the end case
                                if mode.isSolutionState(newState,mode.player1): 
                                    score = mode.evaluate(root.state, newState, move)
                                elif curDepth >= maxDepth : 
                                    score = mode.evaluate(root.state, newState, move)
                                else: 
                                    score = None 

                                #if score == 1e500: 
                                    #print(f'new child at depth {curDepth}: {move1},{score}') 

                                newChild = Node(curDepth,newState,move1,score)
                                #add newChild to root 
                                #print("I made a child with depth", curDepth, 'and score', score, 'and children', newChild.childrens,"count", mode.count)
                               # if (curDepth == 3 and move1[0] == (2, 0) and move1[1] == (4, 4)): print('SCORE CALCULATED',score)
                                #mode.count += 1
                                root.addChild(newChild)
                                #if (curDepth == 3 and move1[0] == (2, 0) and move1[1] == (4, 4)): print('SCORE STORED IN CHILD',newChild.score)

                                if curDepth < maxDepth: # if the desired depth haven't been reached 
                                    if score != 1e500: 
                                        #create children of the newChild
                                        mode.create_children(newChild, curDepth+1, maxDepth, move1)

    #move the marble object given the state and where to move it 
    #doesn't update object coordinate 
    def doMove(mode,state,marble,oldRow,oldCol,newRow,newCol): 
        #empty the original position of marble on board
        state.board[oldRow][oldCol] = '-'
        #place object on new board position 
        state.board[newRow][newCol] = marble 

        #change the player playing's turn
        if state.playerPlaying == mode.player1: 
            state.playerPlaying = mode.player2
        elif state.playerPlaying == mode.player2: 
            state.playerPlaying = mode.player1 

    # move the marble object given the state and where to move it 
    # update object coordinate 
    def doActualMove(mode,state,marble,oldRow,oldCol,newRow,newCol): 
        #compute centre x and y of the empty position 
        x = mode.width/2 - (len(state.board[newRow])-1)*16.5 + 32.9 * newCol 
        y = 70 + newRow*28.5 
        #set the x and y centre of marble to the centre of the empty position 
        marble.x = x 
        marble.y = y 
 
        #empty the original position of marble on board
        state.board[oldRow][oldCol] = '-'
        #place object on new board position 
        state.board[newRow][newCol] = marble 

        #change the player playing's turn
        if state.playerPlaying == mode.player1: 
            state.playerPlaying = mode.player2
        elif state.playerPlaying == mode.player2: 
            state.playerPlaying = mode.player1 

    def AImove(mode,curState): 
        #1) create root node --> move1 = None, score = None
        root = Node(0,curState,None,None) 
        
        #2) generate children for the root node
        mode.create_children(root,0,2,None)
        
        #3) find the marble to move and the best move for the marble through minimax 
        bestScore, bestMove = mode.minimax(root,0,1,-1e500,1e500)

        #4) do the move 
        oldRow,oldCol = bestMove[0]
        newRow, newCol = bestMove[1]
        marble = root.state.board[oldRow][oldCol]
        mode.doActualMove(curState,marble,oldRow,oldCol,newRow,newCol) # update marble coordinate as well

        #print("\n\nafter first move: \n\n", mode.state.board)

        #5) Increment AI move by 1 
        mode.player1.moves += 1 

    # Minimax function: return the best marble to move and its move (move1)
    # (list of tuples of its from and to positions) 
    # idea refernced https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/ 
    # alpha beta pruning: 
    # alpha is the best value that the maximizer currently can gurantee at that level or above 
    # beta is the best value that the minimizer can currently gurantee at that level or above
    def minimax(mode,node,depth,playerNum,alpha,beta): 
        # reached the last depth or solution state, return the value of the node and the move 
        if depth == 2 or node.score == 1e500:
            #print("CHILD BOARD", node.state.board)
            #print ('move',node.move1)
            return node.score, node.move1
        
        else: # recurse through the tree
            bestValue = 1e500 * -playerNum
            bestMove = None
            for child in node.childrens: 
                #generate value of the bottom most child
                val, move = mode.minimax(child,depth+1,-playerNum,alpha,beta)
                
                #if the value of the child is better (smaller or greater depening on player number)
                # than previous best value, then store it as the best_value 
                if playerNum == 1: #look for max value 
                    if val == 1e500 and depth == 0: 
                        bestValue = val 
                        bestMove = move
                    elif val > bestValue or bestMove == None: 
                        bestValue = val 
                        bestMove = move
                    alpha = max(alpha,bestValue)
                    if beta <= alpha: 
                        break 

                elif playerNum == -1: # look for min value 
                    if val < bestValue or bestMove == None: 
                        bestValue = val 
                        bestMove = move
                    beta = min(beta,bestValue)
                    if beta <= alpha: 
                        break

            return bestValue, bestMove

    # scoring mechanisim and weighting referenced from http://cs229.stanford.edu/proj2016spr/report/003.pdf  
    # evaluate the advantage of a state 
    # Advantage to AI player is positive, advantage to non-AI player is negative
    def evaluate(mode,curState,newState,move): 
        # Edge case: winning state --> don't need to evaluate further 
        if mode.isSolutionState(newState,mode.player1): 
            #major advantage to AI player 
            return 1e500
        if mode.isSolutionState(newState,mode.player2): 
            #major advantage to human player 
            return -1e500
        
        # 1) Get progress of the current state 
        progress = mode.getProgress(curState) # a string of 'opening', 'middle', or 'ending'
 
        # 2) Initiate A1, A2, B1, B2, C1, C2
        A1, A2, B1, B2, C1, C2, D1, D2 = 0, 0, 0, 0, 0, 0, 0, 0

        # 3) Loop through every marble on board to calculate their respective scores 
        for row in range(len(curState.board)): 
            for col in range(len(curState.board[row])): 
                if curState.board[row][col] != '-': # must be a marble 
                    marble = curState.board[row][col]

                    #if marble belongs to player1 (AI)
                    if marble.c == mode.player1.color: 
                        A1 += mode.getDistanceToDestination(marble, row) #returns the distance from marble to destination corner 
                        B1 += mode.getDistanceToCentre(marble,curState,row,col) # returns the  distance from marble to verticle central line
                        C1 += mode.getMaximumVerticleAdvancement(marble,curState,row,col) # returns the maximum verticle advance of the marble
                        # if marble is isolated 
                        #if mode.isTrailing(curState,marble,row,col,progress): 
                            #D1 += 1 
                    else: #marble belongs to player2 (human)
                        A2 += mode.getDistanceToDestination(marble,row) #returns the squared sum distance from marble to destination corner 
                        B2 += mode.getDistanceToCentre(marble,curState,row,col) # returns the squared sum distance from marble to verticle central line
                        C2 += mode.getMaximumVerticleAdvancement(marble,curState,row,col) # returns the maximum verticle advance of the marble

        boardScore = (A2**2 - A1**2) + 4*(B2**2-B1**2) + (C1**2 - C2**2) 

        #4) Move score 
        moveScore = mode.getMoveScore(move,marble,newState,curState,progress)

        #5) compute total score 
        totalScore = moveScore*10 + boardScore
        return totalScore

    #HELPER FUNCTIONS FOR EVALUATE
    def getMoveScore(mode,move,marble,newState,curState,progress): 
        moveScore = 0
        startRow,startCol = move[0]
        endRow,endCol = move[1]

        #1) Bounds the moves that the AI can make to relatively centre of the 
        # board (prevent moving to the side)
        if marble.c == 'green': 
            if (endRow == 4) or (endRow == 12): 
                if (endCol < 4) or (endCol >8): 
                    moveScore -= 1e500
            elif (endRow == 5) or (endRow == 6) or (endRow == 10) or (endRow == 11): 
                if (endCol < 3) or (endCol >8): 
                    moveScore -= 1e500
            elif (endRow == 7) or (endRow == 9):
                if (endCol < 2) or (endCol > 7): 
                    moveScore -= 1e500
            elif (endRow == 8): 
                if (endCol < 2) or (endCol > 6): 
                    moveScore -= 1e500

        #2) add score for moving forward 
        rowsForward = abs(endRow - startRow) 
        moveScore += 70 * rowsForward 

        #3) add score for getting rid of trailing piece 
        isTrailingBefore = mode.isTrailing(curState,marble,startRow,startCol,progress)
        isTrailingAfter = mode.isTrailing(newState,marble,endRow,endCol,progress)
        if isTrailingBefore and (not isTrailingAfter): 
            moveScore += 40

        return moveScore 

    #return a string of the state progress: 
    # if no marble overlaps and haven't been through progress state --> in opening state
    # if row of any marble of opposite over lap --> in middle state 
    # if any marble go into the opposite base  --> in ending state 
    def getProgress(mode,state): 
            maxP1Row = 3
            minP2Row = 13 
            for row in range(len(state.board)): 
                for col in range(len(state.board[row])): 
                    if state.board[row][col] != '-': # must be a marble 
                        marble = state.board[row][col]
                        # if marble belongs to P1, check to update maxP1Row 
                        if marble.c == mode.player1.color: 
                            if row > maxP1Row: 
                                maxP1Row = row 
                        # marble belongs to P2, check to update minP2Row 
                        else: 
                            if row < minP2Row: 
                                minP2Row = row 

            if maxP1Row < minP2Row: 
                return 'opening'
            else: # can be in middle or ending 
                P1startBaseRange, P1endBaseRange = mode.player1.homeRange  
                P2startBaseRange, P2endBaseRange = mode.player2.homeRange 
                # if any marble lands in their home base 
                if (P1startBaseRange <= maxP1Row <= P1endBaseRange) or (P2startBaseRange <= minP2Row<=P2endBaseRange): 
                    return 'ending'
                else: 
                    return 'middle'

    def getDistanceToDestination(mode,marble,row): 
        if marble.c == 'green': #marble belongs to AI, try to get as close to row 16 as possible
            return abs(row - 16)
        elif marble.c == 'red': #marble belongs to human, try to get as close to row 0 as possible
            return abs(row - 0)

    def getDistanceToCentre(mode,marble,curState,row,col): 
        centreCol = (len(curState.board[row]))//2 
        return abs(col - centreCol)

    def getMaximumVerticleAdvancement(mode,marble,curState,row,col): 
        legalMoves = mode.getLegalMovesAI(curState,marble,row,col) 
        maxAdvancement = 0 
        for newRow, newCol in legalMoves: 
            advancement = abs(newRow - row)
            if advancement > maxAdvancement: 
                maxAdvancement = advancement 
        return maxAdvancement 

    # returns True if a piece is trailing behind, false if not 
    # (i.e. cannot jump because it is greater than 2 rows apart other pieces)
    def isTrailing(mode,state,marble, marbleRow,marbleCol,progress): 
        legalMoves = mode.getLegalMovesAI(state, marble, marbleRow,marbleCol)
        canJump = False
        # if a marble cannot jump forward, it is isolated
        for newRow, newCol in legalMoves: 
            if abs(newRow - marbleRow) >= 2: 
                canJump = True 
        #TO DO: divide cannot jump into 2 case: can jump after 1 move, 
        #                                       cannot jump after 1 move 
        if canJump == False and (progress != 'opening' or progress !='ending'): 
            return True 
        else: 
            return False

class PlayerVsPlayerMode(Mode):
    #MODEL 
    def appStarted(mode):
        #create background 
        backgroundURL = ('background.jpg')
        mode.backgroundImage = mode.loadImage(backgroundURL)

        #create board 
        boardURL = ('board.png')
        boardImage = mode.loadImage(boardURL)
        mode.boardImageScaled = mode.scaleImage(boardImage,4/7)

        #create game over image 
        congratsURL = ('congrats.png')
        congratsImage = mode.loadImage(congratsURL)
        mode.congratsImageScaled = mode.scaleImage(congratsImage,1/5)

        #create congrats image 
        congratsURL = ('congrats.png')
        congratsImage = mode.loadImage(congratsURL)
        mode.congratsImageScaled = mode.scaleImage(congratsImage,1/5)

        #create settings image 
        settingsURL = ('settings.png')
        settingsImage = mode.loadImage(settingsURL)
        mode.settingsImageScaled = mode.scaleImage(settingsImage,1/20)

        #create player playing dot 
        mode.player1_dot = marble(mode.width/2,20,8,'yellowgreen')
        mode.player2_dot = marble(mode.width/2,580,8,'lightcoral')

        #create list of empty board where 
        # 'g' = green, 'b' = blue, 'y' = yellow, 'p' = purple, 'r' = red,
        # 'o' = orange, and '-' = empty 
        startBoard = [                          ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
        ]

        #load the top triangle with green marbles
        for row in range(4): 
            for col in range(len(startBoard[row])): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of every marble
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'green')
                startBoard[row][col] = newMarble

        #load the bottom triangle with red marbles 
        for row in range(13,17): 
            for col in range(len(startBoard[row])): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[row][col] = newMarble

        mode.player1 = Player('Player 1','green',0,(13,16),False)
        mode.player2 = Player('Player 2','red',0,(0,3),False)
        mode.state = GamePosition(startBoard,mode.player1)

        #initially, no marble is selected
        mode.marbleObjectSelected = None 
        mode.originalMarblePosition = None # original x and y coordinate of marble 
        mode.marblePositionSelected = (-1,-1) #original row and col of marble selected 
        mode.legalMoves = None
        mode.inIllegalMove = False 

        #initiate show hint
        mode.showHint = False 
        mode.possibleMoves = None 

        #initiate background on 
        mode.backgroundOn = False

        #set up winner 
        mode.winner = None 

        #set inSettings to false 
        mode.inSettings = False

        #leaderboard Properties 
        mode.askForName = True 
        mode.name = ''
        mode.rank = 1

    #CONTROLLER 
    def timerFired(mode): 
        if mode.winner == None: 
            if mode.isSolutionState(mode.state,mode.state.playerPlaying): 
                mode.winner = mode.state.playerPlaying 

    #isSolutionState helper function: retrun True if a given state is a solution state
    # for the given player, otherwise return False  
    def isSolutionState(mode,state,player): 
        startRowRange, endRowRange = player.homeRange 
        #loop through every spot in the current player's home base 
        for row in range(startRowRange,endRowRange+1): 
            for col in range(len(state.board[row])): 
                # if the spot is empty, return false 
                if state.board[row][col] =='-': 
                    return False
                # if the spot is not filled up with the player's marble, return False
                elif state.board[row][col].c != player.color: 
                    return False 
        return True 

    def keyPressed(mode,event): 
        #cheat test case: end case 
        if mode.winner == None: 
            if event.key == 'e':
                #clear board 
                startBoard = [                  ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
                ]

                
                #fill in green's home base except 1 (red)
                for row in range(13,17): 
                    for col in range(len(startBoard[row])): 
                        if row == 13 and col == 0: 
                            startBoard[row][col] = '-'
                        else: 
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'green')
                            startBoard[row][col] = newMarble
                
                #move 1 marble off the home base 
                x = mode.width/2 - (len(startBoard[12])-1)*16.5 + 32.9 * 4 #center x of the every marble 
                y = 70 + 12*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'green')
                startBoard[12][4] = newMarble

                
                #fill in red's home base except 1 (green)
                #loop through every spot in the current player's home base 
                for row in range(0,4): 
                    for col in range(len(mode.state.board[row])): 
                        if row == 3 and col== 0: 
                            startBoard[13][0] = '-'
                        else:
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'red')
                            startBoard[row][col] = newMarble
                
                # move 1 marble off the home base
                x = mode.width/2 - (len(startBoard[4])-1)*16.5 + 32.9 * 4 #center x of the every marble 
                y = 70 + 4*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[4][4] = newMarble

                mode.state.board = startBoard 
        else: #game over mode
            if mode.askForName: 
                if event.key in string.ascii_letters: 
                    mode.name += event.key
                elif event.key == 'Delete': 
                    mode.name = mode.name[:-1]
                elif event.key == 'Enter': 
                    mode.askForName = False 

                    # create updated leaderboard by looping through every line 
                    # in the original leaderboard and inserting new score at right 
                    # position 
                    mode.leaderboard= open("leaderboard.txt","rt")
                    oldContents = mode.leaderboard.read() #get old content 
                    print('old contents',oldContents)

                    newContents = ''
                    scoreStored = False
                    if oldContents == '': 
                        newContents += f'{mode.name}    {mode.winner.moves}\n'
                    else:
                        for line in oldContents.splitlines(): 
                            score = ''
                            for c in line: 
                                if c.isdigit(): 
                                    score += c 
                            score = int(score)
                            print('score',score)
                            if score < mode.winner.moves: 
                                newContents += line + '\n'
                                mode.rank += 1 
                            elif score >= mode.winner.moves and scoreStored == False: 
                                newContents += f'{mode.name}    {mode.winner.moves}\n'
                                newContents += line + '\n'
                                scoreStored = True
                            elif score >= mode.winner.moves and scoreStored: 
                                newContents += line + '\n'
                        if scoreStored == False: 
                            newContents += f'{mode.name}    {mode.winner.moves}\n'

                    print ('new contents', newContents)
                    #close leaderboard
                    mode.leaderboard.close()

                    # open file for writing 
                    mode.leaderboard= open("leaderboard.txt","wt") 

                    #clear the leaderboard
                    mode.leaderboard.seek(0)
                    mode.leaderboard.truncate()

                    #rewrite the leaderboard
                    (mode.leaderboard).write(newContents)

                    #close leaderboard
                    mode.leaderboard.close()
        
    def mousePressed(mode,event): 
        if mode.winner == None: #game not over 
            #selects a marble given click 
            mode.marbleObjectSelected = mode.getMarbleObject(event.x,event.y)
            mode.marblePositionSelected = mode.getMarblePosition(event.x,event.y)

            # reset inIllegalMove
            mode.inIllegalMove = False

            # if a marble is selected and show hint is turned on, store the legal moves
            # for drawing 
            if mode.marbleObjectSelected != None and mode.showHint: 
                row,col = mode.marblePositionSelected
                mode.possibleMoves = mode.getLegalMoves(row,col)

            #if setting is clicked on 
            if (535<=event.x<=600) and (0<= event.y<=60): 
                mode.inSettings = True 
            
            #buttons to click in settings 
            if mode.inSettings: 
                if (160<=event.x<=200) and (140<=event.y<=180): #show hints
                    mode.showHint = not (mode.showHint)
                elif (160<=event.x<=200) and (250<=event.y<= 290): #show background 
                    mode.backgroundOn = not (mode.backgroundOn)
                elif (160 <=event.x<=440) and (360 <= event.y<= 410): #return to game 
                    mode.inSettings = False 
                elif (160 <= event.x <=440) and (470<= event.y<=520):#return to home
                    mode.appStarted()
                    mode.app.setActiveMode(mode.app.openingMode) 

        else: #game over 
            if (150<event.x<450) and (500<event.y<540): #clicked on return button
                mode.name = ''
                mode.appStarted()
                mode.app.setActiveMode(mode.app.openingMode)
    
    # View to modal: takes in coordinate of mouse pressed and return marble object  
    # if the marble selected belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # return None
    def getMarbleObject(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            mode.originalMarblePosition = (marble.x,marble.y) #store the marble's original position as a tuple
                            return marble
        return None

    # View to modal: takes in coordinate of mouse pressed and return (row,col) of 
    # the marble selected if it belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # (-1,-1) is returned. 
    def getMarblePosition(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            return (row,col)
        return (-1,-1)

    def mouseDragged(mode, event):
        if (mode.marbleObjectSelected != None): 
            mode.marbleObjectSelected.x = event.x 
            mode.marbleObjectSelected.y = event.y 

    #model to view: convert x and y coordinate into row and col 
    # (-1,-1) is returned if not on board
    def getRowCol(mode,x,y): 
        row = roundHalfUp((y - 70)/28.5) 
        col = roundHalfUp((x - mode.width/2 + ((len(mode.state.board[row]))-1)*16.5)/32.9)
        if (0<= row <=16) and (0<= col <= len(mode.state.board[row])-1): 
            return (row,col)
        return (-1,-1)

    # if marble is not released in a new position on board, 
    # then it would return back to its original position 
    # else if the marble is released onto a legal position on board, 
    # its original position would become empty and the new position will 
    # now consist of the marble 
    def mouseReleased(mode, event):
        #clear hint 
        mode.possibleMoves = None 

        #release marble only if one is selected
        if mode.marbleObjectSelected != None:
            oldRow, oldCol = mode.marblePositionSelected 
            newRow, newCol = mode.getRowCol(event.x,event.y)

            #get all the legal moves of the piece 
            legalMoves = mode.getLegalMoves(oldRow,oldCol)
            # if marble is released onto a legal and empty position
            if (newRow,newCol) in legalMoves: 
                #compute centre x and y of the empty position 
                x = mode.width/2 - (len(mode.state.board[newRow])-1)*16.5 + 32.9 * newCol 
                y = 70 + newRow*28.5 
                #set the x and y centre of marble to the centre of the empty position 
                mode.marbleObjectSelected.x = x 
                mode.marbleObjectSelected.y = y 

                #empty the original position of marble on board
                mode.state.board[oldRow][oldCol] = '-'
                #place object on new board position 
                mode.state.board[newRow][newCol] = mode.marbleObjectSelected

                #increase current player's move by 1 
                mode.state.playerPlaying.moves += 1 

                #check for win 
                if mode.isSolutionState(mode.state,mode.state.playerPlaying): 
                    mode.winner = mode.state.playerPlaying

                #change player's turn 
                if mode.state.playerPlaying == mode.player1: 
                    mode.state.playerPlaying = mode.player2
                elif mode.state.playerPlaying == mode.player2: 
                    mode.state.playerPlaying = mode.player1 
                return 

            #if not released onto a legal and empty position, return marble to original position
            else: 
                mode.inIllegalMove = True #set inIllegalMove to True
                originalX, originalY = mode.originalMarblePosition
                mode.marbleObjectSelected.x = originalX
                mode.marbleObjectSelected.y = originalY 

            #unselected marble 
            mode.marbleObjectSelected = None 
            mode.originalMarblePosition = None
            mode.marblePositionSelected = (-1,-1)
        
    #returns a set of legal position in format (row, col) that the marble can move to  
    # given the orginal marble position in (row,col)
    # 2 cases a move is legal: 1. adjacent and empty 
    #                          2. adjacent is not empty but the one after in the same direction is 
    def getLegalMoves(mode,row,col): 
        legalMoves = set()
        #move to left 
        if mode.getLeft(row,col) != None:
            newRow, newCol = mode.getLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add((newRow,newCol))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'left',seenPositions, possibleJumps) != None: 
                    for move in mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
        
        #move to right 
        if mode.getRight(row,col) != None: 
            newRow, newCol = mode.getRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to upper left
        if mode.getUpperLeft(row,col) != None:
            newRow, newCol = mode.getUpperLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperLeft(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
                
        #move to upper right 
        if mode.getUpperRight(row,col) != None:
            newRow, newCol = mode.getUpperRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom left
        if mode.getBottomLeft(row,col) != None:
            newRow, newCol = mode.getBottomLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomLeft(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom right
        if mode.getBottomRight(row,col) != None:
            newRow, newCol = mode.getBottomRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        legalMoves.add(move)
    
        return legalMoves 

    #GET LEGAL MOVE HELPERS 
    #returns the position left to given row, col in a tuple of (row,col) if it exists 
    def getLeft(mode,row,col): 
        if (col > 0): 
            return (row,col-1)
        else: 
            return None 
        
    #returns the position right to given row, col in a tuple of (row,col) if it exists 
    def getRight(mode,row,col): 
        if (col < len(mode.state.board[row])-1): 
            return (row,col+1)
        else: 
            return None 

    def getUpperLeft(mode,row,col): 
        #col decreasing case 
        if (1<=row<=3) or (9<=row<=12): 
            if (row-1>= 0) and (col-1>=0):
                return (row-1,col-1)
        #col constant case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col)
        #special cases 
        elif (row == 4): 
            if (5<= col<=8): 
                return (row-1,col-5)
        elif (row == 13): 
            return (row-1,col+4)
        else: 
            return None 

    def getUpperRight(mode,row,col): 
        #col constant case 
        if (1<=row<=3) or (9<=row<=12):
            if col <= (len(mode.state.board[row-1])-1): 
                return (row-1,col)
        # col increase case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col+1)
        #special cases 
        elif (row==4): 
            if (4<=col<=7): 
                return (row-1,col-4)
        elif (row==13): 
            return (row-1,col+5)
        else: 
            return None

    def getBottomLeft(mode,row,col): 
        #col constant case
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col)
        #col decreasing case 
        elif (4<= row<=7) or (13<=row<=15): 
            if (col-1 >= 0): 
                return (row+1,col-1)
        #special cases 
        elif (row == 3): 
            return (row+1,col+4)
        elif (row == 12) and (5<=col<=8): 
            return (row+1,col-5)
        else: 
            return None

    def getBottomRight(mode,row,col): 
        #col increasing case 
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col+1)
        #col constant case 
        elif (4<=row<=7) or (13<=row<=15): 
            if (col+1<=len(mode.state.board[row+1])): 
                return (row+1,col)
        #special cases 
        elif (row == 3): 
            return (row+1,col+5)
        elif (row == 12) and (4<=col<=7): 
            return (row+1,col-4)
        else: 
            return None

    #TO DO: GET JUMP RECURSION 
    # return None if no jump is avaliable, else return a list of possible jumps 
    def getJump(mode, marbleRow,marbleCol,direction,seenPositions, possibleJumps): 
        if direction =='left': 
            #if there is an adjacent left 
            if mode.getLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and ((newRow,newCol) not in seenPositions):
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='right': 
            #if there is an adjacent right 
            if mode.getRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='upper left': 
            #if there is an adjacent upper Left 
            if mode.getUpperLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'upper right': 
            #if there is an adjacent upper right
            if mode.getUpperRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom left': 
            #if there is an adjacent bottom left
            if mode.getBottomLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom right': 
            #if there is an adjacent bottom right
            if mode.getBottomRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        print('seen positions in getJump:',seenPositions)
        print ('possible jumps in getJump:',possibleJumps)
        if (len(possibleJumps) == 0): 
            return None
        else:
            return possibleJumps 

    # given the position of an empty row and col (the new position from a previous jump), 
    # check if there are any marbles adjacent to the new position that the player can jump over 
    # if there is, call on getJump 
    def getNextJump(mode,row,col,seenPositions,possibleJumps): 
        #check if adjacent left exists
        if mode.getLeft(row,col) != None:
            newRow, newCol = mode.getLeft(row,col)
            #if adjacent left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps) != None: 
                    for move in mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
        
        #check if adjacent right exists 
        if mode.getRight(row,col) != None: 
            newRow, newCol = mode.getRight(row,col)
            #if adjacent left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if upper left exists 
        if mode.getUpperLeft(row,col) != None:
            newRow, newCol = mode.getUpperLeft(row,col)
            #if adjacent upper left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
                
        #check if upper right exists 
        if mode.getUpperRight(row,col) != None:
            newRow, newCol = mode.getUpperRight(row,col)
            #if adjacent upper right contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if bottom left exists
        if mode.getBottomLeft(row,col) != None:
            newRow, newCol = mode.getBottomLeft(row,col)
            #if adjacent bottom left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)


        #move to bottom right
        if mode.getBottomRight(row,col) != None:
            newRow, newCol = mode.getBottomRight(row,col)
            #if adjacent bottom right contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        
        print('seen positions in getNextJump:',seenPositions)
        print ('possible jumps in getNextJump:',possibleJumps)

        if len(possibleJumps) == 0: 
            return None
        else: 
            return possibleJumps

    #VIEW    
    def redrawAll(mode, canvas):
        if mode.winner == None: #draw game screen
            #draw background (if background is on)
            if mode.backgroundOn: 
                canvas.create_image(mode.width/2,mode.height/2, 
                image=ImageTk.PhotoImage(mode.backgroundImage))

            # draw player playing dot 
            if mode.state.playerPlaying == mode.player1: # player 1 is playing
                mode.player1_dot.draw(canvas) 
            else: # player 2 is playing 
                mode.player2_dot.draw(canvas)

            #draw board background
            canvas.create_image(mode.width/2, mode.height/2, 
            image=ImageTk.PhotoImage(mode.boardImageScaled))

            # if show hint is on and there are possible moves, draw out possible moves 
            if mode.showHint == True and mode.possibleMoves != None: 
                for row, col in mode.possibleMoves: 
                    x = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + 32.9 * col #center x of every marble
                    y = 70 + row*28.5 #centre y of every marble
                    r = 7
                    canvas.create_oval(x-7,y-7,x+8,y+8,fill='Grey')

            #draw marble  
            for row in range(len(mode.state.board)): 
                for col in range(len(mode.state.board[row])): 
                    if mode.state.board[row][col] != '-': # must be a marble 
                        marble = mode.state.board[row][col]
                        marble.draw(canvas)

            # draw illegal move message (when player conducts illegal move)
            if mode.inIllegalMove: 
                canvas.create_text(460,100,text='Opps! That\'s an illegal move!')

            #draw P1 moves 
            canvas.create_rectangle(0,0,90,50,outline = 'LemonChiffon2',fill='LemonChiffon2')
            canvas.create_polygon(91,0,91,50,120,0,fill='LemonChiffon2')
            canvas.create_text(50,25,text=f'Moves: {mode.player1.moves}')

            #draw P2 moves 
            canvas.create_rectangle(510,550,600,600,outline = 'MistyRose2',fill='MistyRose2')
            canvas.create_polygon(511,600,511,550,480,600,fill='MistyRose2')
            canvas.create_text(545,575,text=f'Moves: {mode.player2.moves}')

            #draw settings 
            canvas.create_image(570, 30, 
            image=ImageTk.PhotoImage(mode.settingsImageScaled))

            #if user clicked on settings, draw settings page 
            if mode.inSettings: 
                canvas.create_rectangle(0,0,600,600,fill='white')
                #Title
                canvas.create_text(mode.width/2,60, 
                fill= 'Grey',font = 'Ayuthaya 40',text='Settings')

                #show hint 
                if mode.showHint: 
                    canvas.create_rectangle(160,140,200,180,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,140,200,180,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 20 ,160, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Show Hints')
                
                #draw background 
                if mode.backgroundOn: 
                    canvas.create_rectangle(160,250,200,290,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,250,200,290,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 40, 275, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Draw Background')

                #return to game button
                canvas.create_rectangle(160,360,440,410,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,385, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Game')

                #return to home screen button
                canvas.create_rectangle(160,470,440,520,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,495, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Home')

        else: #game over
            # create congrats image
            canvas.create_image(mode.width/2, 80, 
            image=ImageTk.PhotoImage(mode.congratsImageScaled))

            #create winning text
            canvas.create_text(220,180, fill= 'Grey',font = 'Ayuthaya 20',
                text=f'''
                {mode.winner.name} won with {mode.winner.moves} moves!
                ''')

            #ask for name 
            canvas.create_text(220,180, fill= 'Grey',font = 'Ayuthaya 20',
                text=f'''
                {mode.winner.name} won with {mode.winner.moves} moves!
                ''')

            #type out name 
            canvas.create_text(220,210, fill= 'Grey',font = 'Ayuthaya 20',
                text=f'''
                {mode.winner.name}\'s name: {mode.name}
                ''')

            # display leaderboard 
            leaderboard = open("leaderboard.txt","rt")
            contents = leaderboard.read()
            top5 = ''
            lineNum = 0

            for line in contents.splitlines(): 
                top5 += line + '\n'
                lineNum += 1
                if lineNum >=5: 
                    break 
                    
            canvas.create_text(mode.width/2,240,fill='Grey',font='Ayuthaya 20', 
                                text=f'{mode.name} ranks {mode.rank}!')
            canvas.create_text(mode.width/2-200,300,fill='Grey', font='Ayuthaya 20',
                                text = '''
                                  Leaderboard 
                                Name    Ranking
                                ''')

            canvas.create_text(mode.width/2-40,430,fill= 'Grey',font = 'Ayuthaya 20',
                                text = top5)
            

            #create return button
            canvas.create_rectangle(150,500,450,540,outline='Grey',width=3)
            canvas.create_text(mode.width/2,520,font = 'Ayuthaya 20',text='Return to Home Page',fill='Grey')

class ThreePlayersMode(Mode):
    #MODEL 
    def appStarted(mode):
        #create background 
        backgroundURL = ('background.jpg')
        mode.backgroundImage = mode.loadImage(backgroundURL)

        #create board background 
        boardURL = ('board.png')
        boardImage = mode.loadImage(boardURL)
        mode.boardImageScaled = mode.scaleImage(boardImage,4/7)
        
        #create settings image 
        settingsURL = ('settings.png')
        settingsImage = mode.loadImage(settingsURL)
        mode.settingsImageScaled = mode.scaleImage(settingsImage,1/20)

        #import congrats image 
        congratsURL = ('congrats.png')
        congratsImage = mode.loadImage(congratsURL)
        mode.congratsImageScaled = mode.scaleImage(congratsImage,1/5)

        #create player playing dot 
        mode.player1_dot = marble(40,150,8,'CadetBlue')
        mode.player2_dot = marble(560,150,8,'Khaki')
        mode.player3_dot = marble(mode.width/2,580,8,'lightcoral') 

        #create list of empty board where 
        startBoard = [                          ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
        ]

        #load the top left triangle with blue marbles
        blueEnd = 4
        for row in range(4,8): 
            blueEnd -= 1
            for col in range(0,blueEnd+1): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of every marble
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'blue')
                startBoard[row][col] = newMarble

        #load the top left triangle with yellow marbles 
        yellowEnd = 13
        for row in range(4,8): 
            yellowEnd -= 1 
            for col in range(9,yellowEnd+1): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'yellow')
                startBoard[row][col] = newMarble
        
        #load the bottom triangle with red marbles 
        for row in range(13,17): 
            for col in range(len(startBoard[row])): 
                x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                y = 70 + row*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[row][col] = newMarble

        print(startBoard)
        mode.player1 = Player('Player 1','blue',0,(9,12),False)
        mode.player2 = Player('Player 2','yellow',0,(9,12),False)
        mode.player3 = Player('Player 3','red',0,(0,3),False)
        mode.state = GamePosition(startBoard,mode.player1)

        #initially, no marble is selected
        mode.marbleObjectSelected = None 
        mode.originalMarblePosition = None # original x and y coordinate of marble 
        mode.marblePositionSelected = (-1,-1) #original row and col of marble selected 
        mode.legalMoves = None
        mode.inIllegalMove = False 

        #initiate show hint
        mode.showHint = False 
        mode.possibleMoves = None 

        #initiate background on 
        mode.backgroundOn = False

        #set up winner 
        mode.winner = None 

        #set inSettings to false 
        mode.inSettings = False

    #CONTROLLER 
    def timerFired(mode): 
        if mode.winner == None: 
            if mode.isSolutionState(mode.state,mode.state.playerPlaying): 
                mode.winner = mode.state.playerPlaying 

    #isSolutionState helper function: retrun True if a given state is a solution state
    # for the given player, otherwise return False  
    def isSolutionState(mode,state,player): 
        startRowRange, endRowRange = player.homeRange 
        if player.color == 'red': 
            #loop through every spot in the current player's home base 
            for row in range(startRowRange,endRowRange): 
                for col in range(len(state.board[row])): 
                    # if the spot is empty, return false 
                    if state.board[row][col] =='-': 
                        return False
                    # if the spot is not filled up with the player's marble, return False
                    elif state.board[row][col].c != player.color: 
                        return False 
            return True 

        elif player.color == 'yellow': 
            #loop through every spot in the current player's home base 
            purpleEnd = -1
            for row in range(startRowRange,endRowRange+1): 
                purpleEnd += 1
                for col in range(purpleEnd+1): 
                    # if the spot is empty, return false 
                    if state.board[row][col] =='-': 
                        return False
                    # if the spot is not filled up with the player's marble, return False
                    elif state.board[row][col].c != player.color: 
                        return False 
            return True 

        elif player.color == 'blue':
            orangeEnd = 9
            for row in range(startRowRange,endRowRange+1):
                orangeEnd += 1 
                for col in range(9,orangeEnd): 
                    # if the spot is empty, return false 
                    if state.board[row][col] =='-': 
                        return False
                    # if the spot is not filled up with the player's marble, return False
                    elif state.board[row][col].c != player.color: 
                        return False 
            return True 

    def keyPressed(mode,event): 
        #cheat test case: end case 
            if event.key == 'e':
                #clear board 
                startBoard = [                  ['-'],
                                              ['-','-'],
                                            ['-','-','-'],
                                         ['-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'], 
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                              ['-','-','-','-','-','-','-','-','-'],
                            ['-','-','-','-','-','-','-','-','-','-'],
                          ['-','-','-','-','-','-','-','-','-','-','-'],
                        ['-','-','-','-','-','-','-','-','-','-','-','-'],
                       ['-','-','-','-','-','-','-','-','-','-','-','-','-'],
                                         ['-','-','-','-'],
                                           ['-','-','-',],
                                             ['-','-'],
                                                ['-']
                ]

                
                #fill in blue's home base (orange)
                orangeEnd = 9
                for row in range(9,13):
                    orangeEnd += 1 
                    for col in range(9,orangeEnd): 
                        if row == 9 and col ==9: 
                            startBoard[row][col] = '-'
                        else:
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of every marble
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'blue')
                            print(row,col)
                            startBoard[row][col] = newMarble
                
                # move 1 marble off the home base
                x = mode.width/2 - (len(startBoard[8])-1)*16.5 + 32.9 * 8#center x of the every marble 
                y = 70 + 8*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'blue')
                startBoard[8][8] = newMarble

                #fill in yellow's home base (purple)
                #loop through every spot in the current player's home base 
                purpleEnd = -1
                for row in range(9,13): 
                    purpleEnd += 1
                    for col in range(purpleEnd+1): 
                        if row == 9 and col ==0: 
                            startBoard[row][col] = '-'
                        else:
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'yellow')
                            startBoard[row][col] = newMarble

                # move 1 marble off the home base
                x = mode.width/2 - (len(startBoard[8])-1)*16.5 + 32.9 * 0#center x of the every marble 
                y = 70 + 8*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'yellow')
                startBoard[8][0] = newMarble

                #fill in red's home base except 1 (green)
                #loop through every spot in the current player's home base 
                for row in range(0,4): 
                    for col in range(len(mode.state.board[row])): 
                        if row == 3 and col== 0: 
                            startBoard[13][0] = '-'
                        else:
                            x = mode.width/2 - (len(startBoard[row])-1)*16.5 + 32.9 * col #center x of the every marble 
                            y = 70 + row*28.5 #centre y of every marble
                            newMarble = marble(x,y,8,'red')
                            startBoard[row][col] = newMarble
                
                # move 1 marble off the home base
                x = mode.width/2 - (len(startBoard[4])-1)*16.5 + 32.9 * 4 #center x of the every marble 
                y = 70 + 4*28.5 #centre y of every marble
                newMarble = marble(x,y,8,'red')
                startBoard[4][4] = newMarble

                mode.state.board = startBoard 
        
    def mousePressed(mode,event): 
        if mode.winner == None: #game not over
            # reset inIllegalMove
            mode.inIllegalMove = False

            #selects a marble given click 
            mode.marbleObjectSelected = mode.getMarbleObject(event.x,event.y)
            mode.marblePositionSelected = mode.getMarblePosition(event.x,event.y)
            
            # if a marble is selected and show hint is turned on, store the legal moves
            # for drawing 
            if mode.marbleObjectSelected != None and mode.showHint: 
                row,col = mode.marblePositionSelected
                mode.possibleMoves = mode.getLegalMoves(row,col)
            
            #if setting is clicked on 
            if (0<=event.x<=60) and (540<= event.y<=600): 
                mode.inSettings = True 
            
            #buttons to click in settings 
            if mode.inSettings: 
                if (160<=event.x<=200) and (140<=event.y<=180): #show hints
                    mode.showHint = not (mode.showHint)
                elif (160<=event.x<=200) and (250<=event.y<= 290): #show background 
                    mode.backgroundOn = not (mode.backgroundOn)
                elif (160 <=event.x<=440) and (360 <= event.y<= 410): #return to game 
                    mode.inSettings = False 
                elif (160 <= event.x <=440) and (470<= event.y<=520):#return to home
                    mode.appStarted()
                    mode.app.setActiveMode(mode.app.openingMode) 

        else: #game over 
            if (150<event.x<450) and (500<event.y<540): 
                mode.appStarted()
                mode.app.setActiveMode(mode.app.openingMode)
    
    # View to modal: takes in coordinate of mouse pressed and return marble object  
    # if the marble selected belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # return None
    def getMarbleObject(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            mode.originalMarblePosition = (marble.x,marble.y) #store the marble's original position as a tuple
                            return marble
        return None

    # View to modal: takes in coordinate of mouse pressed and return (row,col) of 
    # the marble selected if it belongs to the player. 
    # If no marble is clicked on or the marble doesn't belong to the player, 
    # (-1,-1) is returned. 
    def getMarblePosition(mode,x,y):
        for row in range(len(mode.state.board)): 
            for col in range(len(mode.state.board[row])): 
                #if the position has an marble 
                if mode.state.board[row][col] != '-':
                    marble = mode.state.board[row][col] 
                    #if marble belongs to the player
                    if marble.c == mode.state.playerPlaying.color: 
                        r = 8 
                        x0 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 - r + 32.9 * col
                        x1 = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + r + 32.9*col 
                        y0 = 70 - r + row*28.5
                        y1 = 70 + r + row*28.5 
                        #if player clicked within the marble
                        if x0<x<x1 and y0<y<y1: 
                            return (row,col)
        return (-1,-1)

    def mouseDragged(mode, event):
        if (mode.marbleObjectSelected != None): 
            mode.marbleObjectSelected.x = event.x 
            mode.marbleObjectSelected.y = event.y 

    #model to view: convert x and y coordinate into row and col 
    # (-1,-1) is returned if not on board
    def getRowCol(mode,x,y): 
        row = roundHalfUp((y - 70)/28.5) 
        col = roundHalfUp((x - mode.width/2 + ((len(mode.state.board[row]))-1)*16.5)/32.9)
        if (0<= row <=16) and (0<= col <= len(mode.state.board[row])-1): 
            return (row,col)
        return (-1,-1)

    # if marble is not released in a new position on board, 
    # then it would return back to its original position 
    # else if the marble is released onto a legal position on board, 
    # its original position would become empty and the new position will 
    # now consist of the marble 
    def mouseReleased(mode, event):
        #clear hint 
        mode.possibleMoves = None 

        #release marble only if one is selected
        if mode.marbleObjectSelected != None:
            oldRow, oldCol = mode.marblePositionSelected 
            newRow, newCol = mode.getRowCol(event.x,event.y)
            print('new released on:', newRow, newCol)

            #get all the legal moves of the piece 
            legalMoves = mode.getLegalMoves(oldRow,oldCol)
            # if marble is released onto a legal and empty position
            if (newRow,newCol) in legalMoves: 
                print('passed legal check')
                #compute centre x and y of the empty position 
                x = mode.width/2 - (len(mode.state.board[newRow])-1)*16.5 + 32.9 * newCol 
                y = 70 + newRow*28.5 
                #set the x and y centre of marble to the centre of the empty position 
                mode.marbleObjectSelected.x = x 
                mode.marbleObjectSelected.y = y 

                #empty the original position of marble on board
                mode.state.board[oldRow][oldCol] = '-'
                #place object on new board position 
                mode.state.board[newRow][newCol] = mode.marbleObjectSelected

                #increase current player's move by 1 
                mode.state.playerPlaying.moves += 1 

                #check for win 
                if mode.isSolutionState(mode.state,mode.state.playerPlaying): 
                    mode.winner = mode.state.playerPlaying

                #change player's turn 
                if mode.state.playerPlaying == mode.player1: 
                    mode.state.playerPlaying = mode.player2
                elif mode.state.playerPlaying == mode.player2: 
                    mode.state.playerPlaying = mode.player3
                elif mode.state.playerPlaying == mode.player3: 
                    mode.state.playerPlaying = mode.player1
                return 

            #if not released onto a legal and empty position, return marble to original position
            else: 
                originalX, originalY = mode.originalMarblePosition
                mode.marbleObjectSelected.x = originalX
                mode.marbleObjectSelected.y = originalY 

            #unselected marble 
            mode.inIllegalMove = True #set inIllegalMove to True
            mode.marbleObjectSelected = None 
            mode.originalMarblePosition = None
            mode.marblePositionSelected = (-1,-1)
        
        print(mode.state.board)

    #returns a set of legal position in format (row, col) that the marble can move to  
    # given the orginal marble position in (row,col)
    # 2 cases a move is legal: 1. adjacent and empty 
    #                          2. adjacent is not empty but the one after in the same direction is 
    def getLegalMoves(mode,row,col): 
        legalMoves = set()
        #move to left 
        if mode.getLeft(row,col) != None:
            newRow, newCol = mode.getLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add((newRow,newCol))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'left',seenPositions, possibleJumps) != None: 
                    for move in mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
        
        #move to right 
        if mode.getRight(row,col) != None: 
            newRow, newCol = mode.getRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to upper left
        if mode.getUpperLeft(row,col) != None:
            newRow, newCol = mode.getUpperLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperLeft(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        legalMoves.add(move)
                
        #move to upper right 
        if mode.getUpperRight(row,col) != None:
            newRow, newCol = mode.getUpperRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getUpperRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom left
        if mode.getBottomLeft(row,col) != None:
            newRow, newCol = mode.getBottomLeft(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomLeft(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        legalMoves.add(move)

        #move to bottom right
        if mode.getBottomRight(row,col) != None:
            newRow, newCol = mode.getBottomRight(row,col)
            #case 1: adjacent position is empty --> can move directly in 
            if mode.state.board[newRow][newCol] == '-':
                legalMoves.add(mode.getBottomRight(row,col))
            #case 2: adjacent position is not empty --> enter jump case 
            else: 
                seenPositions = set()
                possibleJumps = set()
                if mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        legalMoves.add(move)
    
        return legalMoves 

    #GET LEGAL MOVE HELPERS 
    #returns the position left to given row, col in a tuple of (row,col) if it exists 
    def getLeft(mode,row,col): 
        if (col > 0): 
            return (row,col-1)
        else: 
            return None 
        
    #returns the position right to given row, col in a tuple of (row,col) if it exists 
    def getRight(mode,row,col): 
        if (col < len(mode.state.board[row])-1): 
            return (row,col+1)
        else: 
            return None 

    def getUpperLeft(mode,row,col): 
        #col decreasing case 
        if (1<=row<=3) or (9<=row<=12): 
            if (row-1>= 0) and (col-1>=0):
                return (row-1,col-1)
        #col constant case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col)
        #special cases 
        elif (row == 4): 
            if (5<= col<=8): 
                return (row-1,col-5)
        elif (row == 13): 
            return (row-1,col+4)
        else: 
            return None 

    def getUpperRight(mode,row,col): 
        #col constant case 
        if (1<=row<=3) or (9<=row<=12):
            if col <= (len(mode.state.board[row-1])-1): 
                return (row-1,col)
        # col increase case 
        elif (5<=row<=8) or (14<=row<=16):
            return (row-1,col+1)
        #special cases 
        elif (row==4): 
            if (4<=col<=7): 
                return (row-1,col-4)
        elif (row==13): 
            return (row-1,col+5)
        else: 
            return None

    def getBottomLeft(mode,row,col): 
        #col constant case
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col)
        #col decreasing case 
        elif (4<= row<=7) or (13<=row<=15): 
            if (col-1 >= 0): 
                return (row+1,col-1)
        #special cases 
        elif (row == 3): 
            return (row+1,col+4)
        elif (row == 12) and (5<=col<=8): 
            return (row+1,col-5)
        else: 
            return None

    def getBottomRight(mode,row,col): 
        #col increasing case 
        if (0<=row<=2) or (8<=row<=11): 
            return (row+1,col+1)
        #col constant case 
        elif (4<=row<=7) or (13<=row<=15): 
            if (col+1<=len(mode.state.board[row+1])): 
                return (row+1,col)
        #special cases 
        elif (row == 3): 
            return (row+1,col+5)
        elif (row == 12) and (4<=col<=7): 
            return (row+1,col-4)
        else: 
            return None

    #TO DO: GET JUMP RECURSION 
    # return None if no jump is avaliable, else return a list of possible jumps 
    def getJump(mode, marbleRow,marbleCol,direction,seenPositions, possibleJumps): 
        if direction =='left': 
            #if there is an adjacent left 
            if mode.getLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and ((newRow,newCol) not in seenPositions):
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='right': 
            #if there is an adjacent right 
            if mode.getRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction =='upper left': 
            #if there is an adjacent upper Left 
            if mode.getUpperLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'upper right': 
            #if there is an adjacent upper right
            if mode.getUpperRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getUpperRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom left': 
            #if there is an adjacent bottom left
            if mode.getBottomLeft(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomLeft(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        elif direction == 'bottom right': 
            #if there is an adjacent bottom right
            if mode.getBottomRight(marbleRow,marbleCol) != None:
                newRow, newCol = mode.getBottomRight(marbleRow,marbleCol)
                #if adjacent position is empty 
                if mode.state.board[newRow][newCol] == '-' and (newRow,newCol) not in seenPositions:
                    # add the empty spot into possible jumps
                    possibleJumps.add((newRow,newCol))
                    # add the empty spot into seen positions (to prevent from continuously jumping back and forth)
                    seenPositions.add((newRow,newCol))
                    # If allow continuous jump is on: continue checking if more jumps can be made from the spot 
                    if mode.getNextJump(newRow,newCol,seenPositions,possibleJumps) != None: 
                        for move in (mode.getNextJump(newRow,newCol,seenPositions, possibleJumps)): 
                            possibleJumps.add(move)

        print('seen positions in getJump:',seenPositions)
        print ('possible jumps in getJump:',possibleJumps)
        if (len(possibleJumps) == 0): 
            return None
        else:
            return possibleJumps 

    # given the position of an empty row and col (the new position from a previous jump), 
    # check if there are any marbles adjacent to the new position that the player can jump over 
    # if there is, call on getJump 
    def getNextJump(mode,row,col,seenPositions,possibleJumps): 
        #check if adjacent left exists
        if mode.getLeft(row,col) != None:
            newRow, newCol = mode.getLeft(row,col)
            #if adjacent left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps) != None: 
                    for move in mode.getJump(newRow,newCol,'left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
        
        #check if adjacent right exists 
        if mode.getRight(row,col) != None: 
            newRow, newCol = mode.getRight(row,col)
            #if adjacent left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from 
                if mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if upper left exists 
        if mode.getUpperLeft(row,col) != None:
            newRow, newCol = mode.getUpperLeft(row,col)
            #if adjacent upper left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)
                
        #check if upper right exists 
        if mode.getUpperRight(row,col) != None:
            newRow, newCol = mode.getUpperRight(row,col)
            #if adjacent upper right contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'upper right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        #check if bottom left exists
        if mode.getBottomLeft(row,col) != None:
            newRow, newCol = mode.getBottomLeft(row,col)
            #if adjacent bottom left contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom left',seenPositions,possibleJumps): 
                        possibleJumps.add(move)


        #move to bottom right
        if mode.getBottomRight(row,col) != None:
            newRow, newCol = mode.getBottomRight(row,col)
            #if adjacent bottom right contains marble (regardless of color)
            if mode.state.board[newRow][newCol] != '-':
                #enter jump case --> newRol, newCol becomes position of new marble to jump from
                if mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps)!= None: 
                    for move in mode.getJump(newRow,newCol,'bottom right',seenPositions,possibleJumps): 
                        possibleJumps.add(move)

        
        print('seen positions in getNextJump:',seenPositions)
        print ('possible jumps in getNextJump:',possibleJumps)

        if len(possibleJumps) == 0: 
            return None
        else: 
            return possibleJumps

    #VIEW    
    def redrawAll(mode, canvas):
        if mode.winner == None: 
            #draw background (if background is on)
            if mode.backgroundOn: 
                canvas.create_image(mode.width/2,mode.height/2, 
                image=ImageTk.PhotoImage(mode.backgroundImage))

            #draw board 
            canvas.create_image(mode.width/2, mode.height/2, 
            image=ImageTk.PhotoImage(mode.boardImageScaled))

            # if show hint is on and there are possible moves, draw out possible moves 
            if mode.showHint == True and mode.possibleMoves != None: 
                for row, col in mode.possibleMoves: 
                    x = mode.width/2 - (len(mode.state.board[row])-1)*16.5 + 32.9 * col #center x of every marble
                    y = 70 + row*28.5 #centre y of every marble
                    r = 7
                    canvas.create_oval(x-7,y-7,x+8,y+8,fill='Grey')

            # draw player playing dot 
            if mode.state.playerPlaying == mode.player1: # player 1 is playing
                mode.player1_dot.draw(canvas) 
            elif mode.state.playerPlaying == mode.player2: # player 2 is playing 
                mode.player2_dot.draw(canvas)
            else: # player 3 is playing 
                mode.player3_dot.draw(canvas)

            #draw marble  
            for row in range(len(mode.state.board)): 
                for col in range(len(mode.state.board[row])): 
                    if mode.state.board[row][col] != '-': # must be a marble 
                        marble = mode.state.board[row][col]
                        marble.draw(canvas)

            #draw settings 
            canvas.create_image(30, 570, 
            image=ImageTk.PhotoImage(mode.settingsImageScaled))
            
            # draw illegal move message (when player conducts illegal move)
            if mode.inIllegalMove: 
                canvas.create_text(460,80,text='Opps! That\'s an illegal move!')

            #draw P1 moves 
            canvas.create_rectangle(0,0,90,50,outline = 'powderBlue',fill='powderBlue')
            canvas.create_polygon(91,0,91,50,120,0,fill='powderBlue')
            canvas.create_text(50,25,text=f'Moves: {mode.player1.moves}')

            #draw P2 moves 
            canvas.create_rectangle(510,0,600,50,outline = 'lemonchiffon',fill='lemonchiffon')
            canvas.create_polygon(460,0,510,0,510,50,outline='lemonchiffon',fill='lemonchiffon')
            canvas.create_text(550,25,text=f'Moves: {mode.player2.moves}')

            #draw P3 moves 
            canvas.create_rectangle(510,550,600,600,outline = 'MistyRose2',fill='MistyRose2')
            canvas.create_polygon(511,600,511,550,480,600,fill='MistyRose2')
            canvas.create_text(545,575,text=f'Moves: {mode.player3.moves}')

            #if user clicked on settings, draw settings page 
            if mode.inSettings: 
                canvas.create_rectangle(0,0,600,600,fill='white')
                #Title
                canvas.create_text(mode.width/2,60, 
                fill= 'Grey',font = 'Ayuthaya 40',text='Settings')

                #show hint 
                if mode.showHint: 
                    canvas.create_rectangle(160,140,200,180,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,140,200,180,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 20 ,160, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Show Hints')
                
                #draw background 
                if mode.backgroundOn: 
                    canvas.create_rectangle(160,250,200,290,fill='Grey',outline = 'Grey')
                else: 
                    canvas.create_rectangle(160,250,200,290,width = 4, outline='Grey')
                
                canvas.create_text(mode.width/2 + 40, 275, 
                fill= 'Grey',font = 'Ayuthaya 25',text='Draw Background')

                #return to game button
                canvas.create_rectangle(160,360,440,410,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,385, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Game')

                #return to home screen button
                canvas.create_rectangle(160,470,440,520,width= 4,outline = 'Grey')
                canvas.create_text(mode.width/2,495, fill= 'Grey',font = 'Ayuthaya 25',text='Return to Home')

        else: 
            # create congrats image
            canvas.create_image(mode.width/2, 80, 
            image=ImageTk.PhotoImage(mode.congratsImageScaled))

            #create winning text
            canvas.create_text(220,180, fill= 'Grey',font = 'Ayuthaya 20',
                text=f'''
                {mode.winner.name} won with {mode.winner.moves} moves!
                '''
                )

            #create return button
            canvas.create_rectangle(150,500,450,540,outline='Grey',width=3)
            canvas.create_text(mode.width/2,520,font = 'Ayuthaya 20',text='Return to Home Page',fill='Grey')

# modal app taken from http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#subclassingModalApp 
class OpeningMode(Mode): 
    def mousePressed(mode,event): 
        #selected "Modes"
        if (mode.width/2-150<event.x<mode.width/2+150) and (200<event.y<280): 
            mode.app.setActiveMode(mode.app.modesMode)
        #selected "How To Play"
        elif (mode.width/2-150<event.x<mode.width/2+150) and (390<event.y<470): 
            mode.app.setActiveMode(mode.app.helpMode)

    def redrawAll(mode,canvas): 
        #Title
        canvas.create_text(mode.width/2,100, fill= 'Grey',font = 'Ayuthaya 40',text='Chinese Checkers')
        #Modes
        canvas.create_rectangle(mode.width/2-150,200,mode.width/2+150,280,outline='Grey',width=5)
        canvas.create_text(mode.width/2,240,fill='Grey',font = 'Ayuthaya 32',text='Modes')
        #How to Play 
        canvas.create_rectangle(mode.width/2-150,390,mode.width/2+150,470,outline='Grey',width=5)
        canvas.create_text(mode.width/2,430,fill='Grey',font='Ayuthaya 32',text='How To Play')

class ModesMode(Mode): 
    def mousePressed(mode,event): 
        if (mode.width/2-150<event.x<mode.width/2+150) and (200<event.y<280): 
            mode.app.setActiveMode(mode.app.friendsMode)
        
        if (mode.width/2-150<event.x<mode.width/2+150) and (390<event.y<470): 
            mode.app.setActiveMode(mode.app.playerVsAiMode)

    def redrawAll(mode,canvas): 
        #Title
        canvas.create_text(mode.width/2,100, fill= 'Grey',font = 'Ayuthaya 40',text='Select a Mode to Play:')
        #Play with a Friend 
        canvas.create_rectangle(mode.width/2-150,200,mode.width/2+150,280,outline='Grey',width=5)
        canvas.create_text(mode.width/2,240,fill='Grey',font = 'Ayuthaya 25',text='Play with Friends')
        #Play with an AI 
        canvas.create_rectangle(mode.width/2-150,390,mode.width/2+150,470,outline='Grey',width=5)
        canvas.create_text(mode.width/2,430,fill='Grey',font = 'Ayuthaya 25',text='Play with an AI')

class FriendsMode(Mode): 
    def mousePressed(mode,event): 
        if (mode.width/2-150<event.x<mode.width/2+150) and (200<event.y<280): 
            mode.app.setActiveMode(mode.app.playerVsPlayerMode)
        
        if (mode.width/2-150<event.x<mode.width/2+150) and (390<event.y<470): 
            mode.app.setActiveMode(mode.app.threePlayersMode)

    def redrawAll(mode,canvas): 
        #Title
        canvas.create_text(mode.width/2,100, fill= 'Grey',font = 'Ayuthaya 40',text='Select a Mode to Play:')
        #Play with a Friend 
        canvas.create_rectangle(mode.width/2-170,200,mode.width/2+170,280,outline='Grey',width=5)
        canvas.create_text(mode.width/2,240,fill='Grey',font = 'Ayuthaya 25',text='Play with one Friend')
        #Play with an AI 
        canvas.create_rectangle(mode.width/2-170,390,mode.width/2+170,470,outline='Grey',width=5)
        canvas.create_text(mode.width/2,430,fill='Grey',font = 'Ayuthaya 25',text='Play with two Friends')

class HelpMode(Mode): 
    def appStarted(mode): 
        #create help1 image 
        help1URL = ('help1.png')
        help1Image = mode.loadImage(help1URL)
        mode.help1Scaled = mode.scaleImage(help1Image,1/2)

        #create help3 image 
        help2URL = ('help2.png')
        help2Image = mode.loadImage(help2URL)
        mode.help2Scaled = mode.scaleImage(help2Image,1/2)

    def mousePressed(mode,event): 
        if (30<=event.x<=170) and (530<=event.y<=570): 
            mode.app.setActiveMode(mode.app.openingMode)

    def redrawAll(mode,canvas): 
        #Title
        canvas.create_text(mode.width/2,50, fill= 'Grey',font = 'Ayuthaya 40',text='How to Play')
        # 1) Game set up
        canvas.create_text(160,130, fill= 'Grey',font = 'Ayuthaya 12',
        text=
        '''
        Game set up: The board takes the form of a 
        6 pointstar. Each point of the star is a 10 
        hole triangle that corresponds to a player’s 
        starting point. 
        ''')

        #2) Goal of the game
        canvas.create_text(170,260, fill= 'Grey',font = 'Ayuthaya 12',
        text=
        '''
        Goal of the game: The objective for each player
        is to move all the marbles from the starting 
        triangle to the opposite triangle by: 

        1) Moving each marble to any adjacent empty 
           holes 
        ''')

        # help 1 Image 
        canvas.create_image(480, 190, 
        image=ImageTk.PhotoImage(mode.help1Scaled))

        canvas.create_text(170,430, fill= 'Grey',font = 'Ayuthaya 12',
        text=
        '''
        2) Jumping each marble over any adjacent marble
        to an empty hole. 
        * The adjacent marble can belong to you or your 
        opponents. 
        * You can also continually hop over subsequent 
        pieces during your turn, and in any direction,
        as long as there are empty holes on the other 
        side.
        ''')

        #help 2 Image 
        canvas.create_image(480, 450, 
        image=ImageTk.PhotoImage(mode.help2Scaled))

        #create return button
        canvas.create_rectangle(30,530,170,570,outline='Grey',width=3)
        canvas.create_text(100,550,font = 'Ayuthaya 20',text='Return',fill='Grey')

# ModalApp taken from 
# http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#subclassingModalApp
class ChineseCheckers(ModalApp):
    def appStarted(app):
        pygame.mixer.init()
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        app.openingMode = OpeningMode()
        app.modesMode = ModesMode()
        app.friendsMode = FriendsMode()
        app.playerVsPlayerMode = PlayerVsPlayerMode()
        app.threePlayersMode = ThreePlayersMode()
        app.playerVsAiMode = PlayerVsAiMode()
        app.helpMode = HelpMode()
        app.setActiveMode(app.openingMode)
        
ChineseCheckers(width=600, height=600) 