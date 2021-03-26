# featureExtractors.py
# --------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


"Feature extractors for Pacman game states"

from game import Directions, Actions, Grid
import util

class FeatureExtractor:
    def getFeatures(self, state, action):
        """
          Returns a dict from features to counts
          Usually, the count will just be 1.0 for
          indicator functions.
        """
        util.raiseNotDefined()

class IdentityExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[(state,action)] = 1.0
        return feats

class CoordinateExtractor(FeatureExtractor):
    def getFeatures(self, state, action):
        feats = util.Counter()
        feats[state] = 1.0
        feats['x=%d' % state[0]] = 1.0
        feats['y=%d' % state[0]] = 1.0
        feats['action=%s' % action] = 1.0
        return feats

def closestFood(pos, food, walls):
    """
    closestFood -- this is similar to the function that we have
    worked on in the search project; here its all in one place
    """
    fringe = [(pos[0], pos[1], 0)]
    expanded = set()
    while fringe:
        pos_x, pos_y, dist = fringe.pop(0)
        if (pos_x, pos_y) in expanded:
            continue
        expanded.add((pos_x, pos_y))
        # if we find a food at this location then exit
        if food[pos_x][pos_y]:
            return dist
        # otherwise spread out from the location to its neighbours
        nbrs = Actions.getLegalNeighbors((pos_x, pos_y), walls)
        for nbr_x, nbr_y in nbrs:
            fringe.append((nbr_x, nbr_y, dist+1))
    # no food found
    return None

class SimpleExtractor(FeatureExtractor):
    """
    Returns simple features for a basic reflex Pacman:
    - whether food will be eaten
    - how far away the next food is
    - whether a ghost collision is imminent
    - whether a ghost is one step away
    """

    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood()
        walls = state.getWalls()
        ghosts = state.getGhostPositions()

        features = util.Counter()

        features["bias"] = 1.0

        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        # count the number of ghosts 1-step away
        features["#-of-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in ghosts)

        # if there is no danger of ghosts then add the food feature
        if not features["#-of-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 1.0

        dist = closestFood((next_x, next_y), food, walls)
        if dist is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist) / (walls.width * walls.height)
        features.divideAll(10.0)
        return features

class NewExtractor(FeatureExtractor):
    """
    Design you own feature extractor here. You may define other helper functions you find necessary.
    """
    def getFeatures(self, state, action):
        # extract the grid of food and wall locations and get the ghost locations
        food = state.getFood() # Returns a Grid of boolean food indicator variables.
        walls = state.getWalls()
        ghosts = state.getGhostPositions()
        ghost_states = state.getGhostStates()
        capsules = state.getCapsules() # Returns a list of positions (x,y) of the remaining capsules.
        
        features = util.Counter()

        features["bias"] = 1.0


        # compute the location of pacman after he takes the action
        x, y = state.getPacmanPosition()
        dx, dy = Actions.directionToVector(action)
        next_x, next_y = int(x + dx), int(y + dy)

        """ Split between active and scared ghosts """
        active_lst = []
        scared_lst = []
        active_grid = Grid(food.width, food.height)
        scared_grid = Grid(food.width, food.height)
        
        counter = 0
        for ghost in ghosts:
            if ghost_states[counter].scaredTimer: # If scared
                scared_lst.append(ghost)
                scared_grid[int(ghost[0])][int(ghost[1])] = True
            else:
                active_lst.append(ghost)
                active_grid[int(ghost[0])][int(ghost[1])] = True
            counter += 1

        """ Capsule Grid """
        capsule_grid = Grid(food.width, food.height)
        for i in range(len(capsules)):
            cap_x, cap_y = capsules[i]
            capsule_grid[cap_x][cap_y] = True


        """ Closest food """
        dist_food = closestFood((next_x, next_y), food, walls)
        if dist_food is not None:
            # make the distance a number less than one otherwise the update
            # will diverge wildly
            features["closest-food"] = float(dist_food) / (walls.width * walls.height) * 10

        """ Active Ghost 1 step away """
        features["#-of-active-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in active_lst)

        """ Scared Ghost 1 step away """
        features["#-of-scared-ghosts-1-step-away"] = sum((next_x, next_y) in Actions.getLegalNeighbors(g, walls) for g in scared_lst)

        """ Scared Ghost 2 steps away """
        if scared_lst:
            features["#-of-scared-ghosts-2-step-away"] = 0
        for g in scared_lst:
            one_away = Actions.getLegalNeighbors(g, walls)
            features["#-of-scared-ghosts-2-step-away"] += sum((next_x, next_y) in Actions.getLegalNeighbors(h, walls) for h in one_away)
        
        """ Closest Active Ghost + Inverse """
        dist_active = closestFood((next_x, next_y), active_grid, walls)
        if dist_active is not None:
            features["closest-active-inverse"] = 1 / (float(dist_active) + 1) 
            features["closest-active"] = float(dist_active) / (walls.width * walls.height) * 10

            if float(dist_active) > 10:
                features["aggro-food"] = 5
            
        """ Closest Scared Ghost """
        dist_scared = closestFood((next_x, next_y), scared_grid, walls)
        if dist_scared is not None:
            features["closest-scared"] = float(dist_scared) / (walls.width * walls.height) * 10
            
        """ Food is safe """
        # if there is no danger of ghosts then add the food feature
        if not features["#-of-active-ghosts-1-step-away"] and food[next_x][next_y]:
            features["eats-food"] = 5.0

        """ Capsule is safe """
        if not features["#-of-active-ghosts-1-step-away"] and capsule_grid[next_x][next_y]:
            features["eats-capsule"] = 5.0
        

        """ Closest capsule """    
        dist_capsule = closestFood((next_x, next_y), capsule_grid, walls)
        if dist_capsule is not None:                
            features["closest-capsule"] = float(dist_capsule) / (walls.width * walls.height) * 10
            if active_lst and float(dist_active) < 4:
                features["desperate-capsule"] = features["closest-capsule"]

        """ Good stuff """
        if features["eats-capsule"] or features["eats-food"] or features["#-of-scared-ghosts-1-step-away"]:
            features["good-stuff"] = 5.0
        
        features.divideAll(10.0)
        
        return features


        
