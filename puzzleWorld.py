# puzzleWorld.py
#
# A file that represents a puzzle version of the Wumpus World, keeping
# track of the position of the Wumpus and Link.
#
# Written by: Simon Parsons
# Last Modified: 17/12/24

import random
import config
import utils
import copy
from algorithm import Algorithm
from world import World
from utils import Pose
from utils import Directions
from utils import State

class PuzzleWorld(World):

    def __init__(self):

        #Create an algorithm object, and then run the algorithm selector
        self.algo = Algorithm(self, "puzzle")
        
        # Import boundaries of the world. because we index from 0,
        # these are one less than the number of rows and columns.
        self.maxX = config.worldLength - 1
        self.maxY = config.worldBreadth - 1

        # Keep a list of locations that have been used.
        self.locationList = []

        # Wumpus
        self.wLoc = []
        for i in range(config.numberOfWumpus):
            newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
            self.wLoc.append(newLoc)
            self.locationList.append(newLoc)

        # Link
        newLoc = utils.pickUniquePose(self.maxX, self.maxY, self.locationList)
        self.lLoc = newLoc
        self.locationList.append(newLoc)

        # Other elements that we don't use
        self.pLoc = []
        self.gLoc = []
        
        # Game state
        self.status = utils.State.PLAY

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

        # A plan
        self.plan = []

    #
    # Methods
    #
    # These are the functions that are used to update and report on
    # puzzle information.
    def isSolved(self, goal):
        if utils.sameAs(self, goal):
            self.status = utils.State.WON 
            print("Puzzle Over!")
            return True
        else:
            return False

    # A single move is to shift Link or one Wumpus in one direction.
    #
    # This relies on having something in self.plan. Once this has been
    # reduced to [], this code will just print a message each time step.
    #
    # This is where you should start writing your solution to the
    # puzle problem.
    def makeAMove(self):
        if self.plan:
            move = self.plan.pop(0)
            print(move)
            self.takeStep(move)
        else:
            print("Nothing to do!")

    #Formulates a plan 
    def makePlan(self, endState):
        planReturn = []
        planEntry = []
        allPlans = []
        planLengths = []

        #Formulates a plan for Link
        start = self.getLinkLocation()
        goal = endState.getLinkLocation()
        allPlans.append(self.algo.algoRun(start, goal))

        #Formulates plans for all Wumpi
        for wumpi in range(len(self.wLoc)):
            start = self.getWumpusLocation()[wumpi]
            goal = endState.getWumpusLocation()[wumpi]
            allPlans.append(self.algo.algoRun(start, goal))

        #Loop to find the plan with the longest length
        for plan in range(len(allPlans)):
            planLengths.append(len(allPlans[plan])) #Adds plan lengths to a list
        longestLength = max(planLengths)            #Returns the biggest length in that list

        #Loop to add a bunch of zeroes to the end of other lists
        for plan in range(len(allPlans)):
            while True:                         #Loops for each plan until 'break' is called
                if len(allPlans[plan]) < longestLength:
                    allPlans[plan].append(0)    #Adds a zero if the plan's length is smaller than the longest
                else:
                    break                       #If the length is equal to the longest, breaks the while loop

        #Loop to make the plan and return 
        for movement in range(longestLength):

            #Appends planEntry with each plan's action for that movement
            for plan in range(len(allPlans)):
                planEntry.append(allPlans[plan][movement])

            #Appends planEntry to the list
            planReturn.append(planEntry)
            planEntry = [] #Resets it for the next loop

        return planReturn

    # A move is a list of the directions that [Link, Wumpus1, Wumpus2,
    # ...] move in.  takeStep decodes these and makes the relevant
    # change to the state. Basically it looks for the first list
    # element that is non-zero and interprets this as a
    # direction. Movements that exceed the limits of the world have no
    # effect.
    def takeStep(self, move):
        # Move Link
        if move[0] != 0:
            print("Moving Link")
            direction = move[0]
            if direction == Directions.NORTH:
                if self.lLoc.y < self.maxY:
                    self.lLoc.y = self.lLoc.y + 1
            
            if direction == Directions.SOUTH:
                if self.lLoc.y > 0:
                    self.lLoc.y = self.lLoc.y - 1
                
            if direction == Directions.EAST:
                if self.lLoc.x < self.maxX:
                    self.lLoc.x = self.lLoc.x + 1
                
            if direction == Directions.WEST:
                if self.lLoc.x > 0:
                    self.lLoc.x = self.lLoc.x - 1

        # Move the relevant Wumpus
        for i in range(1, len(self.wLoc) + 1):
            if move[i] != 0:
                print("Moving Wumpus", i-1)
                direction = move[i]
                j = i - 1
                if direction == Directions.NORTH:
                    if self.wLoc[j].y < self.maxY:
                        self.wLoc[j].y = self.wLoc[j].y + 1
        
                if direction == Directions.SOUTH:
                    if self.wLoc[j].y > 0:
                        self.wLoc[j].y = self.wLoc[j].y - 1
            
                if direction == Directions.EAST:
                    if self.wLoc[j].x < self.maxX:
                        self.wLoc[j].x = self.wLoc[j].x + 1
            
                if direction == Directions.WEST:
                    if self.wLoc[j].x > 0:
                        self.wLoc[j].x = self.wLoc[j].x - 1