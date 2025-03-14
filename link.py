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

        #Variables storing the path Link takes to find gold
        self.path = []
        self.path_index = 0

        #Variable storing length of gold list initially. Used in makeMove to tell when the list has changed.
        self.goldNum = len(self.gameWorld.getGoldLocation())

        #Dictionary tying directions to coordinate changes.
        self.moveDict = {
            Directions.NORTH: [0, 1],
            Directions.SOUTH: [0, -1],
            Directions.EAST: [1, 0],
            Directions.WEST: [-1, 0]
        }
        
    def makeMove(self):
        #Method to return the next action that Link should take.
        #Asks searching algorithm(s) to return a path, and saves it to "self.path". Then returns the location in that path that
        # corresponds to "self.path_index".

        #If a path doesn't already exist, it will be created here.
        if not self.path:
            self.path = self.depthFirst()
            if len(self.path) == 0:
                quit()
            print(len(self.path))

        #Makes a new path if makeMove is called after gold is already found.
        #If Link is standing on gold, but makeMove has been called again.
        #This means there are a number of gold present
        #If Link is standing on gold, removes the gold from the list of gold, then asks the searching algorithm for
        # a path to the next gold.
        if self.goldNum > len(self.gameWorld.getGoldLocation()):
            self.goldNum -= 1
            self.path = self.path[:self.path_index]
            self.path += self.depthFirst()
            if len(self.path) == self.path_index:
                quit()

        #If Link runs into a wumpus, the program must respond to that in a dynamic way.
        #For depth-first, the remaining locations on the original path will be forgotten, and depth-first will be called again.
        if self.customAdjacent(self.gameWorld.getWumpusLocation(), self.gameWorld.getLinkLocation()) == False:
            print("In path of wumpus. Forming new path")

            self.path = self.path[:self.path_index]
            self.path += self.depthFirst()
            if len(self.path) == self.path_index:
                quit()

        self.path_index = self.path_index + 1 #Increment the index + 1. Has to be done before the return
        return self.path[self.path_index - 1] #Returns the next location for Link to move to


    def depthFirst(self):
        # Method to perform depth-first search from the Link object to find the Gold objects.

        #Defining starting vars
        start = self.gameWorld.getLinkLocation() #Defines starting location
        goal = self.gameWorld.getGoldLocation()[0] #Takes the first gold in the list, sets it as the "goal state"
        maxX = self.gameWorld.maxX; maxY = self.gameWorld.maxY
        node = Node(start, None, None, 0) #Defining initial node (no parent, no action, depth = 0)
        frontiers = [node] #List of possible moves you can make from the present location
        explored = [] #List of locations you've explored / examined
        
        #Loops through every item in frontiers
        while frontiers:
            node = frontiers[-1] #Grab the last item from frontiers
            frontiers = frontiers[:-1] #Removes the last item / only keeps items from index 0 to second-to-last item in list

            explored.append(node) #Puts the removed item at the end of explored

            validMoves = [] #List to store the valid moves
            newLocation = utils.Pose() #Int list to store locations to then add to validMoves

            #For loop runs through N/S/E/W (so, four times)
            for direction in self.moves:
                newLocation = utils.Pose() #Int list to store locations to then add to validMoves
                newLocation.x = node.location.x + self.moveDict[direction][0] #Retrieves coord changes from dict; Saves location to 'location'
                newLocation.y = node.location.y + self.moveDict[direction][1]
                #'node.location' = the current location

                #--Inbound Checker--
                newLocation.x = utils.checkBounds(maxX, newLocation.x) #Sends x to "checkBounds", returns inbound coord if out of bounds
                newLocation.y = utils.checkBounds(maxY, newLocation.y) #Same as above for y
                if utils.sameLocation(newLocation, node.location):
                    continue #If either coord is now unchanged, recognises this as an invalid move, and moves on to next move

                #--Wumpus Checker--
                if self.customAdjacent(self.gameWorld.getWumpusLocation(), newLocation) == False:
                    print("wumpus")
                    continue #If the location is in the path of a 'wumpus', it can't move there, so move to next move

                #--Pit Checker--
                wickedEvilContinue = False 
                for pit in self.gameWorld.getPitsLocation():
                    if utils.sameLocation(newLocation, pit):
                        wickedEvilContinue = True
                        break
                #TODO - PLEASE find a better way of doing this!! This is so bad!! I hate this!!
                if wickedEvilContinue == True:
                    continue #If the location is a pit, it can't move there, so move to next move

                #If passed all previous checks...
                validMoves.append([newLocation, direction]) #saves location AND direction
            
            #If 'validMoves' is empty
            if len(validMoves) == 0:
                print("Link has no valid moves! It's all over!")
                return []

            #For each move Link can take:
            for move in validMoves:
                #Defines a child node in that direction
                #move[0] = new location; move[1] = direction being moved (N/S/E/W)
                child = Node(move[0], node, move[1], node.depth + 1)
                #The Node class overrides 'equals': two nodes are equal if location is the same (which means we can use "not in" here).
                
                if child not in explored and child not in frontiers: 
                    # check for goal
                    if utils.sameLocation(child.location, goal):
                        return self.recoverPlan(child) #Calls a method to grab the path to the gold, then returns it

                    frontiers.append(child) #If the node isn't the goal state, add to frontiers     

        print("Failed to find a path")
        return []
    
    #
    # Methods to retrieve the path taken to the gold once gold is found
    # 
    def recoverPlan(self, child):
        plan = []
        self.recoverPlanRecursive(child, plan)
        return plan
        
    def recoverPlanRecursive(self, node, plan):
        if node.parent:            
            self.recoverPlanRecursive(node.parent, plan)
            plan.append(node.action)

    #My own wumpus checker, because the built in one seems broken
    def customAdjacent(self, allLocs, playerLoc):
        tempLoc = utils.Pose() #Makes a temporary pose to mess with

        #For loop that cycles through all locations in provided list of locations (presumed Wumpus)
        for loc in allLocs:

            #If the location is the same as the player location (this should never happen)
            if utils.sameLocation(loc, playerLoc):
                return False
            
            #
            for direction in self.moves:
                tempLoc.x = loc.x + self.moveDict[direction][0]
                tempLoc.y = loc.y + self.moveDict[direction][1]

                if utils.sameLocation(tempLoc, playerLoc):

                    #To cover evil edge case where Wumpus is standing next to gold
                    for gold in self.gameWorld.getGoldLocation():
                        if utils.sameLocation(tempLoc, gold):
                            return True

                    return False
            
        return True
