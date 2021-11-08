# -*- coding: utf-8 -*-
##############################
# File :: menu.py
# Written on Sunday,  5 September 2021.
# Author: Henrik Peteri
##############################
import pyglet
import random
import math

import myGlobals as g
from inputHandler import *
from entityManager import Entity
from texture import BindTexture
import levelGen
from level import Level

HOVER_MULTIPLIER = 1.5
TRANSITION_IN_SEC = 0.2

#Used for scaling menu based on window size
UI_DEFAULT_WINDOW_WIDTH = 640
UI_DEFAULT_WINDOW_HEIGHT = 640

MENU_TYPE_MAIN_MENU = 0
MENU_TYPE_CONFIRM = 1
MENU_TYPE_LEVEL_SELECT = 2
MENU_TYPE_WIN = 3
MENU_TYPE_LOSE = 4

MENU_ITEM_BUTTON = 0
MENU_ITEM_LABEL = 1
MENU_ITEM_DYNAMIC_BUTTON = 2

#how many non selected buttons are visible
MENU_ITEM_DYNAMIC_SIZE_STEPS = 4

isLevelFileLoaded = False

######################################################################
## Menu Actions
## Button calls MenuItem.Action() with argument menuItem.args
def Stub(void):
    pass

def SetMenu_LevelSelect(void):
    if not isLevelFileLoaded:
        try:
            with open("data/levels/levels.txt", "r") as file:
                fileContent = file.read()
                file.close()
                for line in fileContent.split("\n")[:-1]:
                    
                    item = MenuItem(itemType=MENU_ITEM_DYNAMIC_BUTTON, title=line, Action=LoadLevel, args=line)
                    menus[MENU_TYPE_LEVEL_SELECT].append(item)
                
                    
        except Exception as e:
            print("Failed to load level file :: \n", e)
            return
                
    g.currentMenu = MENU_TYPE_LEVEL_SELECT
    g.selectedMenuItem = 1
    
    UpdateDynamicMenuItems(menus[g.currentMenu], 1)

def SetCurrentLevel(level):
    g.gameMode = g.GAME_MODE_GAME
    g.currentAngle = g.MIN_ANGLE
    g.shotsLeft = level.maxShots
    
    g.currentLevel = level

    g.entityManager.Reset()
    g.entityManager.static = level.walls[:] + level.boxes[:]
    g.entityManager.targets = level.targets[:]

    g.entityManager.BuildBSP(level.width, level.height)
    g.levelRenderTarget.Resize(level.width, level.height)    
    
def LoadLevel(levelName):
    level = Level("", "", 0, 0,  0, [], [], [])
    level.DeSerialize(levelName)

    SetCurrentLevel(level)
    
def LoadRandomizedLevel(void):
    level = levelGen.CreateRandomLevel()
    
    SetCurrentLevel(level)

def LoadMainMenu(void):
    g.gameMode = g.GAME_MODE_MENU
    g.currentMenu = MENU_TYPE_MAIN_MENU
    g.selectedMenuItem = 3
    g.entityManager.Reset()    

def ResetCurrentLevel(void):
    if g.currentLevel:
        SetCurrentLevel(g.currentLevel)
    else:
        LoadMainMenu(None)
        
def LoadNextLevel(void):
    if g.currentLevel.name:
        if g.currentLevel.nextLevel:
            LoadLevel(g.currentLevel.nextLevel)
        else:
            LoadMainMenu(None)
    else:
        LoadRandomizedLevel(None)

def SetMenu_LevelMaybeCleared(cleared):
    g.gameMode = g.GAME_MODE_MENU
    if cleared:
        g.currentMenu = MENU_TYPE_WIN
    else:
        g.currentMenu = MENU_TYPE_LOSE
    g.selectedMenuItem = 1

    g.entityManager.Reset()    
    
######################################################################
## Confirmation Actions, so don't specify arguments
def QuitGame(): 
    g.shouldQuit = True

######################################################################
## Some items might ask for confirmation, which is done through confirmationContext
## Set title for prompt which to display and Action which will be called if 'Yes' is pressed
## if 'No' is pressed, then old menu is restored
class ConfirmationContext:
    title = None
    oldSelectedMenuItem = 0;
    oldMenu = 0
    Action = None
    
confirmationContext = ConfirmationContext()

class ConfirmationArgs:
    def __init__(self, title, Action):
        self.title = title
        self.Action = Action
        
def SetMenu_AskForConfirmation(args):
    global confirmationContext
    global menus
    
    confirmationContext.title = args.title
    confirmationContext.Action = args.Action
    
    confirmationContext.oldSelectedMenuItem = g.selectedMenuItem
    g.selectedMenuItem = 1
    
    confirmationContext.oldMenu = g.currentMenu
    menus[MENU_TYPE_CONFIRM][0].title = args.title

    g.currentMenu = MENU_TYPE_CONFIRM
    
def Confirm(void):
    global confirmationContext
    confirmationContext.Action()

def Cancel(void):
    global confirmationContext
    g.selectedMenuItem = confirmationContext.oldSelectedMenuItem
    g.currentMenu = confirmationContext.oldMenu
    
######################################################################
class MenuItem:
    def __init__(self, title, itemType=MENU_ITEM_BUTTON, Action=Stub, args=None):
        self.title = title
        self.itemType = itemType
        self.Action = Action
        self.args = args
        self.transition = 0
        self.label = None
        self.label_BG = None
        self.dynamicScale = 1


##font size, color, highlight color
menuItemStyles = {
    MENU_ITEM_BUTTON : [34, [255, 255, 255, 255] , [100, 255, 100, 255]],
    MENU_ITEM_LABEL : [66, [120, 120, 0, 255], [100, 255, 100, 255]],
    MENU_ITEM_DYNAMIC_BUTTON : [34, [255, 255, 255, 255] , [100, 255, 100, 255]]
}
        
menus = {
    MENU_TYPE_MAIN_MENU : [MenuItem(itemType=MENU_ITEM_LABEL, title="Mielensä"),
                           MenuItem(itemType=MENU_ITEM_LABEL, title="pahoittaneet"),
                           MenuItem(itemType=MENU_ITEM_LABEL, title="sorsat"),
                           MenuItem(title="Play", Action=SetMenu_LevelSelect),
                           MenuItem(title="Randomized", Action=LoadRandomizedLevel),
                           MenuItem(title="Quit", Action=SetMenu_AskForConfirmation, args=ConfirmationArgs("Quit ?", QuitGame))],
    MENU_TYPE_CONFIRM : [MenuItem(itemType=MENU_ITEM_LABEL, title=""),
                         MenuItem(title="Yes", Action=Confirm),
                         MenuItem(title="No", Action=Cancel)],
    MENU_TYPE_LEVEL_SELECT : [MenuItem(itemType=MENU_ITEM_LABEL, title="Level Select"),
                              ],
    MENU_TYPE_WIN : [MenuItem(itemType=MENU_ITEM_LABEL, title="You Won!"),
                     MenuItem(itemType=MENU_ITEM_BUTTON, title="Next Level", Action=LoadNextLevel),
                     MenuItem(itemType=MENU_ITEM_BUTTON, title="Menu", Action=LoadMainMenu)],
    MENU_TYPE_LOSE : [MenuItem(itemType=MENU_ITEM_LABEL, title="You Lost!"),
                     MenuItem(itemType=MENU_ITEM_BUTTON, title="Try Again", Action=ResetCurrentLevel),
                     MenuItem(itemType=MENU_ITEM_BUTTON, title="Menu", Action=LoadMainMenu)]
                     
}

def IsHoverableItem(menuItems, index):
    menuItem = menuItems[index % len(menuItems)]
    return not menuItem.itemType == MENU_ITEM_LABEL
    
def UpdateMenuEntities(dt):
    sorsa = g.assetHandler.GetAsset("sorsa")
    
    if not len(g.entityManager.entities):
        for i in range(50):
            size = random.randrange(20, 100)
            rad = math.degrees(random.randrange(0, 360))
            
            g.entityManager.entities.append(Entity(random.randrange(0, g.window.width),
                                             random.randrange(0, g.window.height),
                                             size,
                                             size,
                                             math.degrees(random.randrange(0, 360)),
                                             math.cos(rad),
                                             math.sin(rad),
                                             sorsa.handle))
    cx = g.window.width / 2
    cy = g.window.height / 2

    for entity in g.entityManager.entities:
        pad = max(entity.scale_x, entity.scale_y) * 2
        
        entity.x += entity.dir_x * entity.speed * dt
        entity.y += entity.dir_y * entity.speed * dt
        
        if entity.x > g.window.width + pad:
            entity.x = -pad 
        elif entity.x < -pad:
            entity.x = g.window.width + pad
                        
        if entity.y > g.window.height + pad:
            entity.y = -pad
        elif entity.y < -pad:
            entity.y = g.window.height + pad
            
def UpdateDynamicMenuItems(menuItems, selectedMenuItem):
    "Update menu item size based on its index relative to selectedMenuItem"
    for i in range(len(menuItems)):
        item = menuItems[i]

        if not item.itemType == MENU_ITEM_DYNAMIC_BUTTON:
            continue

            
        d = abs(selectedMenuItem - i)
        if d >= MENU_ITEM_DYNAMIC_SIZE_STEPS:
            item.dynamicScale = 0
            continue
        item.dynamicScale = max(1 - d / MENU_ITEM_DYNAMIC_SIZE_STEPS, 0.05)
        
def UpdateMenu(dt, isSimUpdate=False):
    if not isSimUpdate:
        return
        
    if IsKeyUp("q") and not g.currentMenu == MENU_TYPE_MAIN_MENU:
        g.currentMenu = MENU_TYPE_MAIN_MENU
        g.selectedMenuItem = 3

            
    menuItems = menus[g.currentMenu]
        
    menuMoved = False
    if IsKeyUp('w'):
        for i in range(len(menuItems)):
            g.selectedMenuItem += len(menuItems) - 1
                
            if IsHoverableItem(menuItems, g.selectedMenuItem):                    
                menuMoved = True
                break
            
    if IsKeyUp('s'):
        for i in range(len(menuItems)):
            g.selectedMenuItem += 1
            if IsHoverableItem(menuItems, g.selectedMenuItem):
                menuMoved = True
                break
            
    if menuMoved:
        g.selectedMenuItem %= len(menuItems)
        UpdateDynamicMenuItems(menuItems, g.selectedMenuItem)
            
    if IsKeyUp(" "):
        menuItems[g.selectedMenuItem].Action(menuItems[g.selectedMenuItem].args)
    
    
def UpdateMenu_VisualOnly(dt):
    UpdateMenuEntities(dt)
  
    menuItems = menus[g.currentMenu]
    
    for i, item in enumerate(menuItems):
        if i == g.selectedMenuItem:
            item.transition = min(item.transition + (1.0 / TRANSITION_IN_SEC * dt), 1)
        else:
            item.transition = max(item.transition - (1.0 / TRANSITION_IN_SEC * dt), 0)

    
            
def ShouldSkipMenuItem(item):
    return not item.dynamicScale
        
def DrawMenu():
   
    menuItems = menus[g.currentMenu]
   
    y_off = 0;

    ##Scale ui based on window size
    scale = min(g.window.width / UI_DEFAULT_WINDOW_WIDTH,
                g.window.height / UI_DEFAULT_WINDOW_HEIGHT)

    scale = min(scale, 1.7)
    scale = max(scale, 0.1)


    ##Calculate font pad based on max font size in the menu
    maxFontSize = 0
    for i, item in enumerate(menuItems):
        if ShouldSkipMenuItem(item):
            continue
        maxFontSize = max(maxFontSize, menuItemStyles[item.itemType][0])
    fontPad = maxFontSize * scale * 0.5

    ##Calculate where the first item should be placed
    for i, item in enumerate(menuItems):
        if ShouldSkipMenuItem(item):
            continue
        fontSize = menuItemStyles[item.itemType][0] * item.dynamicScale
        y_off += (fontSize + fontPad) * scale
        
        
    x = g.window.width / 2;
    y = g.window.height / 2 + y_off / 2;

    if y > g.window.height - maxFontSize - fontPad:
        y = g.window.height - maxFontSize - fontPad
   
    for i, item in enumerate(menuItems):
        if ShouldSkipMenuItem(item):
            continue
        style = menuItemStyles[item.itemType]
        fontSize0 = style[0] * scale
        fontSize1 = fontSize0 * HOVER_MULTIPLIER 

        col0 = style[1]
        col1 = style[2]


        transition = item.transition
        
        fontSize = ((fontSize1 - fontSize0) * item.transition + fontSize0) * item.dynamicScale
        ######################################################################
        #Draw black "shadow" underneath the text
        bg = item.label_BG
        if not bg:
            bg = pyglet.text.Label(item.title,
                                   font_size=fontSize,
                                   x=x,
                                   y=y - fontSize * 0.1,
                                   anchor_x="center",
                                   anchor_y="center")
            bg.color = (0, 0, 0, 255)
            item.label_BG = bg

        bg.font_size = fontSize
        bg.x  = x
        bg.y = y - fontSize * 0.1
            
        bg.draw()
        
        ######################################################################
        
        label = item.label
        if not label:
            label = pyglet.text.Label(item.title,
                                      font_size=fontSize,
                                      x=x,
                                      y=y,
                                      anchor_x="center",
                                      anchor_y="center")
            item.label = label
            
        if not g.selectedMenuItem == i:
            label.color = (col0[0], col0[1], col0[2], col0[3])
        else:
            label.color = (col1[0], col1[1], col1[2], col1[3])

        label.font_size = fontSize
        label.x = x
        label.y = y
        y -= fontSize0 + fontPad
        label.draw()
        
        ######################################################################

        
