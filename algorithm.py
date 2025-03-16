#File to store the searching algorithms
#(Originally stored them in link.py - moved them out so puzzleWorld could use them)

import utils
from utils import Directions
from node import Node

class Algorithm():

    def __init__(self, world):
        self.gameWorld = world
        
        #Variables storing the selected algorithm
        self.selectedAlgo = ""
        self.algorithms = {
            "1": "Depth-First Search",
            "2": "Breadth-First Search"
        }

        #Dictionary tying directions to coordinate changes.
        self.moveDict = {
            Directions.NORTH: [0, 1],
            Directions.SOUTH: [0, -1],
            Directions.EAST: [1, 0],
            Directions.WEST: [-1, 0]
        }

        #Values telling algorithms where they start and where they're going
        self.start = None
        self.goal = None

    #
    # Algorithm Selection Methods
    #
    #Prompt the user and asks what searching algorithm they want to run
    def algoPick(self):
        #Method to prompt the user to select a searching algorithm
        while True:
            print("\nPlease select a searching algorithm.")
            for i in self.algorithms:
                print("\'" + i + "\' = " + self.algorithms[i])

            algoInput = input("> ")
            if algoInput in self.algorithms:
                self.selectedAlgo = algoInput; print("")
                return
            else:
                print("ERROR - Valid input not entered. Please enter one of the numbers listed.")

    #Runs the previously selected algorithm
    def algoRun(self, start, goal):
        if self.selectedAlgo == "1":
            return self.depthFirst(start, goal)
        if self.selectedAlgo == "2":
            return self.breadthFirst(start, goal)
        if self.selectedAlgo == "":
            print("No algorithm selected. The algoPick() method must be ran first.")
            return
    
    #
    # Searching Algorithms
    #
    #Method to perform depth-first search from the Link object to find the Gold objects.
    def depthFirst(self, start, goal):
        #Defining starting vars
        node = Node(start, None, None, 0) #Defining initial node (no parent, no action, depth = 0)
        frontiers = [node] #List of possible moves you can make from the present location
        explored = [] #List of locations you've explored / examined
        
        #Loops through every item in frontiers
        while frontiers:
            node = frontiers[-1] #Grab the last item from frontiers
            frontiers = frontiers[:-1] #Removes the last item / only keeps items from index 0 to second-to-last item in list
            explored.append(node) #Puts the removed item at the end of explored

            #Calls the valid moves finder to return the valid moves for that location
            validMoves = self.validMoveFinder(node)

            #For each move Link can take:
            for move in validMoves:
                #Defines a child node in that direction. move[0] = new location; move[1] = direction being moved (N/S/E/W)
                child = Node(move[0], node, move[1], node.depth + 1)

                #Two nodes are equal if location is the same (which means we can use "not in" here).
                if child not in explored and child not in frontiers: 
                    # check for goal
                    if utils.sameLocation(child.location, goal):
                        return self.recoverPlan(child) #Calls a method to grab the path to the gold, then returns it

                    frontiers.append(child) #If the node isn't the goal state, add to frontiers     

        print("Failed to find a path")
        return []
    
    #Method to perform breadth-first search from the Link object to find the Gold objects.
    def breadthFirst(self, start, goal):
        #Defining starting vars
        node = Node(start, None, None, 0) #Defining initial node (no parent, no action, depth = 0)
        frontiers = [node] #List of possible moves you can make from the present location
        explored = [] #List of locations you've explored / examined

        while frontiers:    
            if not frontiers:
                print("Failed to find a path")
                return []

            node = frontiers[0] # gets the first item
            frontiers.pop(0) # removes the first item
            explored.append(node) # adds first item to 'explored'

            #Calls the valid moves finder to return the valid moves for that location
            validMoves = self.validMoveFinder(node)

            #For each move Link can take:
            for move in validMoves:
                #Defines a child node in that direction. move[0] = new location; move[1] = direction being moved (N/S/E/W)
                child = Node(move[0], node, move[1], node.depth + 1)

                if child not in explored and child not in frontiers:
                    if utils.sameLocation(child.location, goal):
                        return self.recoverPlan(child)
                    
                    frontiers.append(child)

        print("Failed to find a path")
        return []

    #
    # Algorithm Sub-Methods
    #
    #Takes a node's location, analyses the squares cardinally next to it, and says where it can move
    def validMoveFinder(self, node):
        validMoves = [] #List to store the valid moves
        maxX = self.gameWorld.maxX; maxY = self.gameWorld.maxY
        
        #For loop runs through N/S/E/W (so, four times)
        for direction in self.moveDict:
            newLocation = utils.Pose() #Int list to store locations to then add to validMoves
            #IMPORTANT - newLocation MUST be assigned a new Pose every time this loops!! Otherwise creates a bug where
            # all entries in validMoves share the same Pose address. This bug is inconsistent - sometimes happens, seemingly
            # dependent on if this method is called from algoRun or makeMove - I assume it's some Python quirk? Be advised

            newLocation.x = node.location.x + self.moveDict[direction][0] #Retrieves coord changes from dict; Saves to 'newlocation'
            newLocation.y = node.location.y + self.moveDict[direction][1]
            #'node.location' = the current location

            #--Inbound Checker--
            newLocation.x = utils.checkBounds(maxX, newLocation.x) #Sends x to "checkBounds", returns inbound coord if out of bounds
            newLocation.y = utils.checkBounds(maxY, newLocation.y) #Same as above for y
            if utils.sameLocation(newLocation, node.location):
                continue #If either coord is now unchanged, recognises this as an invalid move, and moves on to next move

            #--Wumpus Checker--
            if self.customAdjacent(self.gameWorld.getWumpusLocation(), newLocation) == False:
                continue #If the location is in the path of a 'wumpus', it can't move there, so move to next move

            #--Pit Checker--
            wickedEvilContinue = False 
            for pit in self.gameWorld.getPitsLocation():
                if utils.sameLocation(newLocation, pit):
                    wickedEvilContinue = True; break
            #TODO - PLEASE find a better way of doing this!! This is so bad!! I hate this!!
            if wickedEvilContinue == True:
                wickedEvilContinue = False; continue #If the location is a pit, it can't move there, so move to next move

            #If passed all previous checks...
            validMoves.append([newLocation, direction]) #saves location AND direction

        #If 'validMoves' is empty
        if len(validMoves) == 0:
            print("Link has no valid moves! It's all over!")
            quit()
        
        #If there's a possible move
        return validMoves
    
    #My own wumpus checker, because the built in one seems broken?
    #Runs through all the wumpi, checks the squares next to them, and says if the player is in them
    def customAdjacent(self, allLocs, playerLoc):
        tempLoc = utils.Pose() #Makes a temporary pose to mess with

        #For loop that cycles through all locations in provided list of locations (presumed Wumpus)
        for loc in allLocs:
            #If the location is the same as the player location - could happen during a chase?
            if utils.sameLocation(loc, playerLoc):
                return False
            
            #Cycles through the four directions and corresponding grid locations. No inbound check but shouldn't cause issues
            for direction in self.moveDict:
                tempLoc.x = loc.x + self.moveDict[direction][0]
                tempLoc.y = loc.y + self.moveDict[direction][1]
                if utils.sameLocation(tempLoc, playerLoc):
                    #To cover evil edge case where Wumpus is standing next to gold
                    for gold in self.gameWorld.getGoldLocation():
                        if utils.sameLocation(tempLoc, gold):
                            return True
                    return False
        return True
    
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

