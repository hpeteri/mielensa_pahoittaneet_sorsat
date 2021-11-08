##############################
# File :: game.py
# Written on Sunday,  5 September 2021.
# Author: Henrik Peteri
##############################
import pyglet
from pyglet.gl import *

import math
import time

import myGlobals as g
from inputHandler import IsKeyHeld, IsKeyDown, IsKeyUp, GetMousePosition, UpdateKeyboard
from renderer import SetRenderTarget, BlitRenderTarget
from entityManager import Entity
import menu
import collision
import vector
from entityUpdate import *

SEC_TO_MAX_ANGLE = 2
SEC_TO_MAX_FORCE = 2

UI_SCALE = 1
UI_FONT_SIZE = 24 * UI_SCALE
UI_TEXT_COLOR = (255, 255, 255, 255)
    
fpsLabel = None
shotsLabel = None
angleLabel = None
forceLabel = None

def BlitLevel():
    x = g.window.width / 2
    y = g.window.height / 2

    scale = max(g.levelRenderTarget.width / g.window.width,
                g.levelRenderTarget.height / g.window.height)
    
    g.renderer.PushDrawCall("quad",
                            g.levelRenderTarget.colorAttachment,
                            x,
                            y,
                            g.levelRenderTarget.width / scale,
                            -g.levelRenderTarget.height / scale,
                            0,
                            ~0)
    SetRenderTarget(0, g.window.width, g.window.height)
    g.renderer.Flush(g.window.width, g.window.height)
    
def DrawFPS():
    global fpsLabel
    if not fpsLabel:
        fpsLabel = pyglet.text.Label("",
                                      font_size=14,
                                      x=0,
                                      y=0,
                                      anchor_x="right",
                                      anchor_y="top")

    fpsLabel.color = (0, 0, 0, 255)
    fpsLabel.text = str(g.fps)
    fpsLabel.x = g.window.width - 20
    fpsLabel.y = g.window.height - 20
    fpsLabel.draw()
    
def DrawApplication():
    ##########################################################################################    
    for entity in g.entityManager.drawables:
        g.renderer.PushDrawCall("quad", entity.textureHandle, entity.x, entity.y, entity.scale_x, entity.scale_y, entity.rot_z, entity.color)

    ##########################################################################################    
    if g.gameMode == g.GAME_MODE_GAME:
        SetRenderTarget(g.levelRenderTarget.frameBufferID,
                        g.levelRenderTarget.width,
                        g.levelRenderTarget.height)

        sling = g.assetHandler.GetAsset("sling")
        g.renderer.PushDrawCall("quad", sling.handle, g.SHOT_START_X, g.SHOT_START_Y, g.TILE_SIZE, g.TILE_SIZE, 0, ~0)
        DrawFlightPath()

        g.renderer.Flush(g.levelRenderTarget.width, g.levelRenderTarget.height)
        BlitLevel()        
    else:
        SetRenderTarget(0,
                        g.window.width,
                        g.window.height)
       
        g.renderer.Flush(g.window.width, g.window.height)

    ##########################################################################################
    #Draw UI
    SetRenderTarget(0, g.window.width, g.window.height)
    DrawFPS()
    
    if g.gameMode == g.GAME_MODE_GAME:
        DrawUI()
    elif g.gameMode == g.GAME_MODE_MENU:
        menu.DrawMenu()

    ##########################################################################################
    

def GetCollidingTarget(e):
    for target in g.entityManager.targets:
                
        sep_x, sep_y = collision.HandleCollision_Circle_Circle(e.collisionShape,
                                                               target.collisionShape)
        if not (sep_x and sep_y):
            continue

        return target
            
    
def DrawFlightPath():
    if g.inFlight or not g.applyingForce:
        return
    
    ball = g.assetHandler.GetAsset("ball")
    x = g.SHOT_START_X
    y = g.SHOT_START_Y
    rad = math.radians(g.currentAngle)
        
    dir_x = math.cos(rad) * g.currentForce
    dir_y = math.sin(rad) * g.currentForce
    points = []
    frameStep = 20  #how many frames should pass until new point is added to the path

    e = Entity(x, y, g.TILE_SIZE, g.TILE_SIZE, 0, dir_x, dir_y)
    
    for i in range(math.floor(1 / g.sim_dt_step)):
        
        UpdateEntitiesAndHandleCollisions(g.sim_dt_step, [e], g.entityManager.bsp)
        
        target = GetCollidingTarget(e)
        if target:
            if len(points) <= 2:
                points.append([e.x, e.y])
            break
      
        if ShouldShotBeRemoved(e):
            break
        #draw points when enough frames have passed
        if not i % frameStep:
            points.append([e.x, e.y])

    transition = g.runningTimer % g.SHOT_TRANSITION_TIME / g.SHOT_TRANSITION_TIME
    for i in range(len(points) - 1):
        p0 = points[i]
        p1 = points[i + 1]
        points[i][0] = (p1[0] - p0[0]) * transition + p0[0]
        points[i][1] = (p1[1] - p0[1]) * transition + p0[1]
        
        
    for point in points[:-2]:
       g.renderer.PushDrawCall("quad", ball.handle, point[0], point[1], g.TILE_SIZE, g.TILE_SIZE, 0, 0xffffffff)

    if len(points) > 2:
        lastIndex = len(points) - 2
        alpha = int(0xff * (1 - transition))
        g.renderer.PushDrawCall("quad", ball.handle, points[lastIndex][0], points[lastIndex][1], g.TILE_SIZE, g.TILE_SIZE, 0, alpha << 24 | 0x00ffffff)
        
def DrawUI():
    portrait = g.assetHandler.GetAsset("sorsa_portrait")
       
    pad = 20 * UI_SCALE    
    scale_x = g.TILE_SIZE * UI_SCALE
    scale_y = scale_x * 2
    p0_x = pad + scale_x / 2
    p0_y = pad + scale_y / 2
    
    g.renderer.PushDrawCall("quad",
                            portrait.handle,
                            p0_x, g.window.height - p0_y,
                            scale_x, scale_y,
                            0,
                            ~0)
    g.renderer.Flush(g.window.width, g.window.height)

    ##########################################################################################
    
    p0_x += scale_x

    global shotsLabel
    global angleLabel
    global forceLabel
    
    # Shots left
    if not shotsLabel:
        shotsLabel = pyglet.text.Label("",
                                       font_size=UI_FONT_SIZE,
                                       x=0,
                                       y=0,
                                       anchor_x="left",
                                       anchor_y="center")

    shotsLabel.x = p0_x
    shotsLabel.y = g.window.height - p0_y
    shotsLabel.text = "x {}".format(g.shotsLeft)
    shotsLabel.draw()
    
    ##########################################################################################
    # Angle
    p0_y += scale_y / 2 + pad

    if not angleLabel:
        angleLabel = pyglet.text.Label("",
                                        font_size=UI_FONT_SIZE,
                                        x=0,
                                        y=0,
                                        anchor_x="left",
                                        anchor_y="center")
        
    angleLabel.x = pad
    angleLabel.y = g.window.height - p0_y
    angleLabel.text = "Angle :: {:.0f}".format(g.currentAngle)
    angleLabel.draw()

    ##########################################################################################
    # Force
    p0_y += UI_FONT_SIZE * 1.5

    if not forceLabel:
        forceLabel = pyglet.text.Label("",
                                       font_size=UI_FONT_SIZE,
                                       x=0,
                                       y=0,
                                       anchor_x="left",
                                       anchor_y="center")
        
    forceLabel.x = pad
    forceLabel.y = g.window.height - p0_y
    forceLabel.text = "Force :: {:.0f}".format(g.currentForce)
    forceLabel.draw()    

def UpdateGame(dt, isSimUpdate=False):
    if isSimUpdate:
        if not g.inFlight:
            if IsKeyHeld("w") :
                g.currentAngle = min(g.currentAngle + ((g.MAX_ANGLE - g.MIN_ANGLE) * (1 / SEC_TO_MAX_ANGLE * dt)), g.MAX_ANGLE)
                
            if IsKeyHeld("s") :
                g.currentAngle = max(g.currentAngle - ((g.MAX_ANGLE - g.MIN_ANGLE) * (1 / SEC_TO_MAX_ANGLE * dt)), g.MIN_ANGLE)

            if not g.applyingForce:
                if IsKeyHeld(" "):
                    g.applyingForce = True

                if IsKeyUp("q"):
                    menu.LoadMainMenu(None)
                    
                
            if g.applyingForce:
                g.currentForce = max(min(g.currentForce + (g.MAX_FORCE * 1 / SEC_TO_MAX_FORCE * dt), g.MAX_FORCE), g.MIN_FORCE)
            
                if not IsKeyHeld(" "):
                    ##Shoot
                    sorsa = g.assetHandler.GetAsset("sorsa")
                    rad = math.radians(g.currentAngle)
                    g.entityManager.entities.append(Entity(g.SHOT_START_X, g.SHOT_START_Y,
                                                           g.TILE_SIZE, g.TILE_SIZE,
                                                           0,
                                                           math.cos(rad) * g.currentForce,
                                                           math.sin(rad) * g.currentForce,
                                                           sorsa.handle))
                    g.inFlight = True
                    g.applyingForce = False
                    g.currentForce = 0
                    g.shotsLeft -= 1
                    
    ##########################################################################################
    
    UpdateEntitiesAndHandleCollisions(dt, g.entityManager.entities, g.entityManager.bsp)
    
    for e in g.entityManager.entities:
        target = GetCollidingTarget(e)
        if target:
            g.entityManager.targets.remove(target)            
            e.dir_x = 0
            e.dir_y = 0
            e.collidedThisFrame = True
            
        if ShouldShotBeRemoved(e):
            g.entityManager.entities.remove(e)

            if isSimUpdate:
                if not len(g.entityManager.targets):
                    menu.SetMenu_LevelMaybeCleared(True)
                elif not g.shotsLeft:
                    menu.SetMenu_LevelMaybeCleared(False)
                
    g.inFlight = len(g.entityManager.entities)
            
        
def UpdateTiming():
    endTime = time.time_ns() 
    dt = ((endTime - g.startTime)) * 10 ** -9
   
    g.startTime = endTime
    g.elapsed += dt
    g.frameCounter += 1
    
    if g.elapsed > 1.0:
        g.fps = g.frameCounter
        g.frameCounter = 0
        g.elapsed -= 1.0

    
    return min(dt, g.max_dt)
    
def UpdateAndDraw():
    #glClearColor(1, 0.68, 0.72, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    SetRenderTarget(g.levelRenderTarget.frameBufferID,
                    g.levelRenderTarget.width,
                    g.levelRenderTarget.height)
    
    glClear(GL_COLOR_BUFFER_BIT)

    SetRenderTarget(0,
                    g.window.width,
                    g.window.height)
    
    ########################################################
    dt = UpdateTiming()
    g.runningTimer += dt
    ########################################################
    
    simTime = dt + g.sim_dt_excess
    steps = int(simTime / g.sim_dt_step)
    g.sim_dt_excess = simTime % g.sim_dt_step
    
    for i in range(steps):
        if g.gameMode == g.GAME_MODE_MENU:
            menu.UpdateMenu(g.sim_dt_step, True)
            
        if g.gameMode == g.GAME_MODE_GAME:
            UpdateGame(g.sim_dt_step, True)
        UpdateKeyboard()
        
    ########################################################
    ## Visual only Update can be with the whole dt and without copying entities
    if g.gameMode == g.GAME_MODE_MENU:
        menu.UpdateMenu_VisualOnly(dt)
        
    ##Simulate visual copy so we hit our frame time
    simEntityManager = g.entityManager
    g.entityManager = g.entityManager.Copy()
    
    if g.gameMode == g.GAME_MODE_MENU:
        menu.UpdateMenu(g.sim_dt_excess, False)

    if g.gameMode == g.GAME_MODE_GAME:
        UpdateGame(g.sim_dt_excess, False)
    
        
    simEntityManager.drawables = g.entityManager.entities + simEntityManager.static + g.entityManager.targets
    g.entityManager = simEntityManager
    

    DrawApplication()
    
    ########################################################
    
def Init_Time():
    g.startTime = time.time_ns()
   
