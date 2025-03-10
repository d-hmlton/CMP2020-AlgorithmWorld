# node.py
#
#
# Written by: Helen Harman
# Last Modified: 02/02/24

import utils
        
class Node():
    def __init__(self, location, parent, action, depth):
        self.location = location
        self.parent = parent
        self.action = action 
        self.depth = depth
        
    def isGoal(self, goal):
        return utils.sameLocation(self.location, goal)
    
    
    def __repr__(self):
        return f"<Node location:{self.location} action:{self.action}>"
            
    def __str__(self):
        return f"[location:{self.location} action:{self.action}]"
        
        
    # by just using the location to check if two Nodes are the same, 
    #    checking if the location has been visited/explored or added to frontiers easier.
    #     -- i.e. we can make use of "in" 
    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Node):
            return (self.location == other.location)
        return False    
        
