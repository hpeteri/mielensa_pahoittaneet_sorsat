##############################
# File :: levelGen.py
# Written on Saturday, 11 September 2021.
# Author: Henrik Peteri
##############################

import random
import math
import noise

import myGlobals as g
from entityManager import EntityManager, Entity, SerializeEntityTransform, DeSerializeEntityTransform
from level import *
import vector
from entityUpdate import *

LEVEL_WIDTH = 16 * 3
LEVEL_HEIGHT = 9 * 3

MIN_SCALE = 0.5
MAX_SCALE = 2.5

MIN_SHOTS = 5
MAX_SHOTS = 15

wantedBounces = 2 #How many times should shot bounce until we place a target

MIN_CEILING_SECTIONS = 5
MAX_CEILING_SECTIONS = 10

MIN_GROUND_SECTIONS = 5
MAX_GROUND_SECTIONS = 10

MIN_BOXES = math.ceil(MIN_GROUND_SECTIONS / 2)
MAX_BOXES = MAX_GROUND_SECTIONS
MIN_BOX_SCALE = 1
MAX_BOX_SCALE = 3
MIN_BOX_TOWER_HEIGHT = 3
MAX_BOX_TOWER_HEIGHT = 10

def GenerateTargets(dt, bsp, numShots):
    target = g.assetHandler.GetAsset("target")
    
    targets = []
    tries = 0
    while True:
        if len(targets) >= round(numShots / 2):
            break

        tries += 1
        if tries > 100:
            break
        
        angle = (g.MAX_ANGLE - g.MIN_ANGLE) * random.random() + g.MIN_ANGLE
        force = (g.MAX_FORCE - g.MIN_FORCE) * random.random() + g.MIN_FORCE
        rad = math.radians(angle)

        bounces = 0
        
        
        
        e = Entity(g.SHOT_START_X,
                   g.SHOT_START_Y,
                   g.TILE_SIZE,
                   g.TILE_SIZE,
                   0,
                   math.cos(rad) * force,
                   math.sin(rad) * force,
                   0)
        
        while True:
            UpdateEntitiesAndHandleCollisions(dt, [e], bsp)

            if not e.collidedThisFrame:
                continue

            bounces += 1
            if bounces >= wantedBounces or ShouldShotBeRemoved(e):
                if vector.Length([e.x - g.SHOT_START_X, e.y - g.SHOT_START_Y]) > g.TILE_SIZE * 5:
                    targets.append(Entity(e.x, e.y, g.TILE_SIZE, g.TILE_SIZE, 0, 0, 0, target.handle))
                break
            
    return targets

def GenerateBoxBetween2Points(x0, y0, x1, y1):
    width = g.TILE_SIZE
    wall = g.assetHandler.GetAsset("wall")
    dir_x = x1 - x0
    dir_y = y1 - y0
    
    middle_x = x0 + dir_x / 2
    middle_y = y0 + dir_y / 2
    
    rot = math.atan2(dir_y, dir_x)

    return [Entity(middle_x, middle_y,
                       vector.Length([dir_x, dir_y]) ,
                       width,
                       rot, 0, 0,
                       wall.handle)]


GROUND_GENERATORS = [GenerateBoxBetween2Points]

def CreateGroundDeviation(min_x, min_y, max_x, max_y, minCount, maxCount, forcePoints=False,
                          start_x=0, start_y=0, end_x=0, end_y=0):
    wall = g.assetHandler.GetAsset("wall")
        
    count = random.randint(minCount, maxCount)
    entities = []
    yPoints = []
    xPoints = []
    if forcePoints:
        xPoints.append(start_x)
        yPoints.append(start_y)
        
    distanceBetweenPoints = 1 / (count ) 
    xOffset = random.random() * g.TILE_SIZE
    yScale = (max_y - min_y) / 2
    yOffset = yScale + min_y
    
    for i in range(count + 1):
        
        x = distanceBetweenPoints * i
        if i % count:
            x += (random.random() * distanceBetweenPoints / 4)

        xPoints.append(x * (max_x - min_x) + min_x)
        y = noise.pnoise1(xOffset + x) * yScale + yOffset
        yPoints.append(y)
        
    if forcePoints:
        xPoints.append(end_x)
        yPoints.append(end_y)

    for i in range(0, len(xPoints) - 1):
        x0 = xPoints[i]
        y0 = yPoints[i]
        x1 = xPoints[i + 1]
        y1 = yPoints[i + 1]

        generatorIndex = random.randint(0, len(GROUND_GENERATORS) - 1)
        if not i % (len(xPoints) - 2):
            generatorIndex = 0

        entities.extend(GROUND_GENERATORS[generatorIndex](x0, y0, x1, y1))

    return entities
    
def CreateRandomLevel(seed=None):
    random.seed(seed)
    sling  = g.assetHandler.GetAsset("sling")
    box = g.assetHandler.GetAsset("box")
    wall = g.assetHandler.GetAsset("wall")
        
    numShots = random.randint(MIN_SHOTS, MAX_SHOTS)
        
    ######################################################################
    walls = []
    #Generate Ceiling
    walls.extend(CreateGroundDeviation(g.HALF_TILE + 100, 
                                       LEVEL_HEIGHT / 2 * g.TILE_SIZE + g.HALF_TILE,
                                       LEVEL_WIDTH * g.TILE_SIZE - g.HALF_TILE - 100,
                                       (LEVEL_HEIGHT - 1) * g.TILE_SIZE - g.HALF_TILE,
                                       MIN_CEILING_SECTIONS, MAX_CEILING_SECTIONS,
                                       True,
                                       g.HALF_TILE, 
                                       LEVEL_HEIGHT / 2 * g.TILE_SIZE + g.HALF_TILE,
                                       LEVEL_WIDTH * g.TILE_SIZE - g.HALF_TILE,
                                       LEVEL_HEIGHT * g.TILE_SIZE - g.HALF_TILE,
                                       ))

    #Generate Ground 
    groundStartIndex = len(walls) #Used for generating boxes on ground 
    walls.extend(CreateGroundDeviation(g.HALF_TILE + g.SHOT_START_X * 6, 
                                       -g.TILE_SIZE,
                                       (LEVEL_WIDTH - 2) * g.TILE_SIZE - g.HALF_TILE,
                                       LEVEL_HEIGHT / 2 * g.TILE_SIZE,
                                       MIN_GROUND_SECTIONS, MAX_GROUND_SECTIONS,
                                       True,
                                       g.HALF_TILE + g.SHOT_START_X * 4, 
                                       g.HALF_TILE,
                                       LEVEL_WIDTH * g.TILE_SIZE - g.HALF_TILE,
                                       LEVEL_HEIGHT / 3 * g.TILE_SIZE
                                       ))
        
    ######################################################################
    boxes = []
    # Boxes
    indices = []
    for i in range(random.randint(MIN_BOXES, MAX_BOXES)):
        index  = random.randint(groundStartIndex + 2, len(walls) - 1)
        if index in indices:
            continue

        indices.append(index)

    for index in indices:
        e = walls[index]
        y = e.y
        x = e.x

        max_scale = MAX_BOX_SCALE #Next box in tower should be smaller than the lower one
        for i in range(random.randint(MIN_BOX_TOWER_HEIGHT, MAX_BOX_TOWER_HEIGHT)):
            scale = (random.random() * (max_scale - MIN_BOX_SCALE) + MIN_BOX_SCALE)
            max_scale = scale
            scale *= g.TILE_SIZE

            x += math.sin(random.random() * 2 * math.pi) * scale / 4
            boxes.append(Entity(x, 
                                y + scale / 2,
                                scale,
                                scale,
                                0,
                                0, 0,                              
                                box.handle))
            y += scale
            if y > LEVEL_HEIGHT / 3 * g.TILE_SIZE:
                break
    ######################################################################
    #boundaries
    #bottom
    walls.append(Entity(LEVEL_WIDTH * g.TILE_SIZE / 2,
                                      g.TILE_SIZE / 2 ,
                                      LEVEL_WIDTH * g.TILE_SIZE,
                                      g.TILE_SIZE,
                                      0, 0, 0, wall.handle))

    #top
    walls.append(Entity(LEVEL_WIDTH * g.TILE_SIZE / 2,
                                      LEVEL_HEIGHT * g.TILE_SIZE - g.TILE_SIZE / 2,
                                      LEVEL_WIDTH * g.TILE_SIZE,
                                      g.TILE_SIZE,
                                      0, 0, 0, wall.handle))
    #left
    walls.append(Entity(g.TILE_SIZE / 2,
                                      LEVEL_HEIGHT * g.TILE_SIZE / 2,
                                      g.TILE_SIZE,
                                      LEVEL_HEIGHT * g.TILE_SIZE,
                                      0, 0, 0, wall.handle))
    #right
    walls.append(Entity(LEVEL_WIDTH * g.TILE_SIZE - g.TILE_SIZE / 2,
                                      LEVEL_HEIGHT * g.TILE_SIZE / 2 ,
                                      g.TILE_SIZE,
                                      LEVEL_HEIGHT * g.TILE_SIZE,
                                      0, 0, 0, wall.handle))

    ######################################################################
    
    # Targets
    currentLevel = g.currentLevel
    g.currentLevel = Level("", "",
                           LEVEL_WIDTH * g.TILE_SIZE,
                           LEVEL_HEIGHT * g.TILE_SIZE,
                           0,
                           [], [], [])
    entityManager = EntityManager()
    entityManager.static = walls + boxes
    entityManager.BuildBSP(LEVEL_WIDTH * g.TILE_SIZE, LEVEL_HEIGHT * g.TILE_SIZE)

    targets = GenerateTargets(g.sim_dt_step, entityManager.bsp, numShots)
    ######################################################################
    level = Level("", "",
                  LEVEL_WIDTH * g.TILE_SIZE,
                  LEVEL_HEIGHT * g.TILE_SIZE,
                  numShots,
                  walls,
                  boxes,
                  targets)
    return level
    
def CreateRandomLevelSet(string):
    levels = []
    usedNames = []

    for levelName in string.split(" "):
        levelName = levelName.lower().capitalize()
        originalName = levelName
        tries = 0
        while True:
            if not (levelName in usedNames):
                break
            tries += 1
            levelName = "{}({})".format(originalName, tries)
            
        levelName = levelName.replace("*", "'")
        level = CreateRandomLevel(levelName)
        print("Created level {}".format(levelName))
        level.name = levelName
        usedNames.append(levelName)
        levels.append(level)
    for i in range(len(levels) - 1):
        levels[i].nextLevel = levels[i + 1].name
    for i in range(len(levels)):
        levels[i].Serialize()
        
    try:
        with open("{}{}".format(LEVEL_DIR, "levels.txt"), "w") as file:
            for name in usedNames:
                file.write("{}\n".format(name))
            file.close()
    except Exception as e:
        print("Failed to write level order file ", e)
        
    
