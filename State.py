#Board image used: https://www.ymimports.com/pages/how-to-play-chinesse-checkers 
#Congratulation image used: http://nyaeyc.org/wp-content/uploads/congrats.jpg 
#Wooden background image used: https://images.fineartamerica.com/images-medium-large-5/brown-wooden-table-background-anilakkus.jpg 
# lost image used: https://opengameart.org/sites/default/files/sorryyouloststamp.png 
import math, copy, random, pygame, os, decimal, string
from cmu_112_graphics import *
from tkinter import *
from pygame.locals import *
####################################################################
# Generic generic States Class taken from http://www.cs.cmu.edu/~112/notes/notes-2d-lists.html 
class State(object):
    def __eq__(self, other): 
        return (other != None) and self.__dict__ == other.__dict__
    def __hash__(self): 
        return hash(str(self.__dict__)) # hack but works even with lists
    def __repr__(self): 
        return str(self.__dict__)

class GamePosition(State): 
    def __init__(self,board,playerPlaying): 
        self.board = board #A 2D array containing marbles. 
        self.playerPlaying = playerPlaying #stores the side that's currently playing 
