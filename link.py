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
from utils import Directions
from node import Node

class Link():

    def __init__(self, dungeon):

        # Make a copy of the world an attribute, so that Link can
        # query the state of the world
        self.gameWorld = dungeon

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
        
    def makeMove(self):
        # This is the function you need to define
        #
        # For now we have a placeholder, which always moves Link
        # directly towards the gold.
        
        # Get the location of the gold.
        allGold = self.gameWorld.getGoldLocation()
        if len(allGold) > 0:
            nextGold = allGold[0]
        myPosition = self.gameWorld.getLinkLocation()
        # If not at the same x coordinate, reduce the difference
        if nextGold.x > myPosition.x:
            return Directions.EAST
        if nextGold.x < myPosition.x:
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if nextGold.y > myPosition.y:
            return Directions.NORTH
        if nextGold.y < myPosition.y:
            return Directions.SOUTH

    def depthFirst(self):
        # Method to perform depth-first search from the Link object to find the Gold objects.

        start = self.gameWorld.getLinkLocation() #Defines starting location
        goal = self.gameWorld.getGoldLocation() #Defines location of (first) gold

        node = Node(start, None, None, 0) #Defining initial node (no parent, no action, depth = 0)

        frontiers = [node] #List of possible moves you can make from the present location
        explored = [] #List of locations you've explored / examined
        
        #Loops through every item in frontiers
        while frontiers:
            node = frontiers[-1] #Grab the last item from frontiers
            frontiers = frontiers[:-1] #Remove the last item from frontiers

            explored.append(node) #Puts the removed item at the end of explored

            # -Defining all the actions that Link can take-
            #Dictionary tying directions to coordinate changes. (Will probably need to move this and define elsewhere later)
            moveDict = {
                Directions.NORTH: [0, 1],
                Directions.SOUTH: [0, -1],
                Directions.EAST: [1, 0],
                Directions.WEST: [-1, 0]
            }

            validMoves = [] #List to store the valid moves
            newLocation = [] #Int list to store locations to then add to validMoves

            #Storing max bound values as temp vars (grabbing them all the time is inefficient)
            maxX = self.gameWorld.maxX
            maxY = self.gameWorld.maxY

            #For loop runs through N/S/E/W (so, four times)
            for direction in self.moves:
                newLocation = node.location + moveDict[direction] #Retrieves coord changes from dict; Saves location to 'location'
                #'node.location' = the current location

                #--Inbound Checker--
                newLocation.x = utils.checkBounds(maxX, newLocation.x) #Sends x to "checkBounds", returns inbound coord if out of bounds
                newLocation.y = utils.checkBounds(maxY, newLocation.y) #Same as above for y
                if newLocation.x == node.location.x or newLocation.y == node.location.y:
                    continue #If either coord is now unchanged, recognises this as an invalid move, and moves on to next move

                #--Wumpus Checker--
                if self.gameWorld.isSmelly(newLocation):
                    continue #If the location is in the path of a 'wumpus', it can't move there, so move to next move

                #--Pit Checker--
                if self.gameWorld.isWindy(newLocation):
                    continue #If the location is a pit, it can't move there, so move to next move

                #--Gold Checker--
                if self.gameWorld.isGlitter(newLocation):
                    validMoves = [direction] #If location is gold, moving there takes priority
                    #(For the record, if gold is where a wumpus path also is, the earlier placement of wumpus check means it won't
                    #  know the gold is there and will focus on avoiding wumpus. This may cause unexpected behaviour!)
                    break #No need to look for other valid moves

                #If passed all previous checks...
                validMoves.append(direction)

            #For each move Link can take:
            for move in validMoves:
                child = Node((node.location + moveDict[move]), node.location, move, node.depth + 1)
                #The Node class overrides 'equals': two nodes are equal if location is the same (which means we can use "not in" here).
                if child not in explored and child not in frontiers: 
                    # check for goal
                    if child.isGoal(goal):
                        print("Found goal")
                        #return self.recoverPlan(child) #NOT WORKING
                    frontiers.append(child) 

            #add list of valid actions