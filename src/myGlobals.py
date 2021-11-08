##############################
# File :: myGlobals.py
# Written on Sunday,  5 September 2021.
# Author: Henrik Peteri
##############################
from renderer import *
from assetHandler import *
from entityManager import *
from renderer import *

#global objects
window = None
shouldQuit = False
assetHandler = AssetHandler()
entityManager = EntityManager()
renderer = Renderer()
levelRenderTarget = None

#constants
GAME_MODE_MENU = 0
GAME_MODE_GAME = 1

GRAVITY = 9

MIN_ANGLE = 25
MAX_ANGLE = 75
MAX_FORCE = 15
MIN_FORCE = 1
SHOT_START_X = 100
SHOT_START_Y = 100
TILE_SIZE = 64
HALF_TILE = TILE_SIZE / 2
SHOT_TRANSITION_TIME = 1

#timing variables
startTime = 0
elapsed = 0
fps = 0
frameCounter = 0
runningTimer = 0

max_dt = 1 / 10 
sim_dt_step = 1 / 120 #Update Frequency
sim_dt_excess = 0 #prev frame sim time, which will be added to current frames dt

#Game variables
gameMode = GAME_MODE_MENU
currentLevel = None
inFlight = False
applyingForce = False
shotsLeft = 0
currentAngle = 0
currentForce = 0


currentMenu = 0 #MENU_TYPE_MAIN_MENU
selectedMenuItem = 3 #MainMenu has 3 line header which can't be selected
