# link.py
#
# The code that defines the behaviour of Link.
#
# You should be able to write the code for a simple solution to the
# game version of the Wumpus World here, getting information about the
# game state from self.gameWorld, and using makeMove() to generate the
# next move.
#
# Written by: Simon Parsons
# Last Modified: 25/08/20

import world
import random
import utils
from algorithm import Algorithm
from utils import Directions
from node import Node

class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        #Create an algorithm object, and then run the algorithm selector
        self.algo = Algorithm(self.gameWorld)
        self.algo.algoPick()

        self.start = self.gameWorld.getLinkLocation() #Defines starting location
        self.goal = self.gameWorld.getGoldLocation()[0] #Takes the first gold in the list, sets it as the "goal state"

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

        #Variables storing the path Link takes to find gold
        self.path = []
        self.path_index = 0

        #Variable storing length of gold list initially. Used in makeMove to tell when the list has changed.
        self.goldNum = len(self.gameWorld.getGoldLocation())

    def makeMove(self):
        #Method to return the next action that Link should take.
        #Asks searching algorithm(s) to return a path, and saves it to "self.path". Then returns the location in that path that
        # corresponds to "self.path_index".

        #If a path doesn't already exist, it will be created here.
        if not self.path:
            self.pathAlter()

        #Makes a new path if makeMove is called after gold is already found - there's more gold to get
        if self.goldNum > len(self.gameWorld.getGoldLocation()):
            self.goal = self.gameWorld.getGoldLocation()[0] #Changes the goal to the new gold location
            self.goldNum -= 1
            self.pathAlter()

        #If Link runs into a wumpus, the program must respond to that in a dynamic way.
        #For depth-first, the remaining locations on the original path will be forgotten, and depth-first will be called again.
        if self.algo.customAdjacent(self.gameWorld.getWumpusLocation(), self.gameWorld.getLinkLocation()) == False:
            self.pathAlter()

        self.path_index = self.path_index + 1 #Increment the index + 1. Has to be done before the return
        return self.path[self.path_index - 1] #Returns the next location for Link to move to
    
    #Method that calls the algorithm to generate a path. Separated from makeMove() to remove duplication.
    def pathAlter(self):
        self.start = self.gameWorld.getLinkLocation()

        if not self.path:   #If no path exists yet (first time being run)
            self.path = self.algo.algoRun(self.start, self.goal)
        else:           #If path already exists (subsequent runs)
            self.path = self.path[:self.path_index]
            self.path += self.algo.algoRun(self.start, self.goal)
        
        #If the path is equal to the path index (starts at 0, and where path is cut later, so would mean no path found)
        if len(self.path) == self.path_index: 
            quit()