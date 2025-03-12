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

        #If Link runs into a wumpus, the program must respond to that in a dynamic way.
        #For depth-first, the remaining locations on the original path will be forgotten, and depth-first will be called again.
        if self.gameWorld.linkSmelly():
            self.path = self.path[:self.path_index]
            self.path.extend(self.depthFirst())

        self.path_index = self.path_index + 1 #Increment the index + 1. Has to be done before the return
        return self.path[self.path_index - 1] #Returns the next location for Link to move to
        
        # Get the location of the gold.
        #allGold = self.gameWorld.getGoldLocation()
       # if len(allGold) > 0:
          #  nextGold = allGold[0]
       # myPosition = self.gameWorld.getLinkLocation()
        # If not at the same x coordinate, reduce the difference
       # if nextGold.x > myPosition.x:
      #      return Directions.EAST
       # if nextGold.x < myPosition.x:
      #      return Directions.WEST
        # If not at the same y coordinate, reduce the difference
      #  if nextGold.y > myPosition.y:
       #     return Directions.NORTH
      #  if nextGold.y < myPosition.y:
      #      return Directions.SOUTH

    def depthFirst(self):
        # Method to perform depth-first search from the Link object to find the Gold objects.

        start = self.gameWorld.getLinkLocation() #Defines starting location
        allGold = self.gameWorld.getGoldLocation() #Grabs a list of all the gold
        if len(allGold) > 0:
            goal = allGold[0] #Takes the first gold in the list, sets it as the "goal state"
        else:
            print("No gold present?") #This is if the length of allGold is 0 from the very beginning.
            return []                 # This shouldn't happen, so the program ends early
        
        # -Defining all the actions that Link can take-
        #Dictionary tying directions to coordinate changes. (Will probably need to move this and define elsewhere later)
        moveDict = {
            Directions.NORTH: [0, 1],
            Directions.SOUTH: [0, -1],
            Directions.EAST: [1, 0],
            Directions.WEST: [-1, 0]
        }

        #Storing max bound values as temp vars (grabbing them all the time is inefficient)
        maxX = self.gameWorld.maxX
        maxY = self.gameWorld.maxY

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
                newLocation.x = node.location.x + moveDict[direction][0] #Retrieves coord changes from dict; Saves location to 'location'
                newLocation.y = node.location.y + moveDict[direction][1]
                #'node.location' = the current location

                #--Inbound Checker--
                newLocation.x = utils.checkBounds(maxX, newLocation.x) #Sends x to "checkBounds", returns inbound coord if out of bounds
                newLocation.y = utils.checkBounds(maxY, newLocation.y) #Same as above for y
                if newLocation.x == node.location.x and newLocation.y == node.location.y:
                    continue #If either coord is now unchanged, recognises this as an invalid move, and moves on to next move

                #--Wumpus Checker--
                if self.gameWorld.isSmelly(newLocation):
                    continue #If the location is in the path of a 'wumpus', it can't move there, so move to next move
                    #(For the record, if gold is where a wumpus path also is, the earlier placement of wumpus check means it won't
                    #  know the gold is there and will focus on avoiding wumpus. This may cause unexpected behaviour!)

                #--Pit Checker--
                if self.gameWorld.isWindy(newLocation):
                    continue #If the location is a pit, it can't move there, so move to next move

                #If passed all previous checks...
                validMoves.append([newLocation, direction]) #saves location AND direction
            
            #If 'validMoves' is empty
            if len(validMoves) == 0:
                print("Link has no valid moves! It's all over!")

            #For each move Link can take:
            for move in validMoves:
                #Defines a child node in that direction
                #move[0] = new location; move[1] = direction being moved (N/S/E/W)
                child = Node(move[0], node.location, move[1], node.depth + 1)
                #The Node class overrides 'equals': two nodes are equal if location is the same (which means we can use "not in" here).
                if child not in explored and child not in frontiers: 
                    # check for goal
                    if child.location == goal:
                        print("Gold found!")
                        return self.recoverPlan(child) #Calls a method to grab the path to the gold, then returns it

                    
                    frontiers.append(child) #If the node isn't the goal state, add to frontiers
                print(child)

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