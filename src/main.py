##############################
# File :: main.py
# Written on Thursday,  2 September 2021.
# Author: Henrik Peteri
##############################
import pyglet
pyglet.options['debug_gl'] = False
from pyglet.gl import *
import os
import time

import myGlobals as g
import game
from inputHandler import HandleKeyEvent, HandleMouseMove
from levelGen import CreateRandomLevelSet
from renderer import RenderTarget

def PrintGLString(idString, glString):
    c_string = glGetString(glString)
    string = ""
    for i in c_string:
        if not i:
            break
        string += chr(i)
        
    print("{} :: {}".format(idString, string))

def OnUpdateAndDraw():
    try:
        game.UpdateAndDraw()
    except GLException as e:
        print(e)

def StubUpdate(dt):
    if g.shouldQuit:
        pyglet.app.exit()
    
            
def OnKeyDown(key, mods):
    HandleKeyEvent(key, True)

def OnKeyUp(key, mods):
    HandleKeyEvent(key, False)

def main():
    g.window = pyglet.window.Window(resizable=True)
    
    g.window.on_draw = OnUpdateAndDraw
    g.window.on_key_press = OnKeyDown
    g.window.on_key_release = OnKeyUp
    g.window.on_mouse_motion = HandleMouseMove
    pyglet.clock.schedule_interval(StubUpdate, 1 / 9999)

    g.levelRenderTarget = RenderTarget(g.window.width, g.window.height)
    game.Init_Time()
    ######################################################################
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    glClearColor(1, 0.68, 0.72, 1)

    PrintGLString("GL_VENDOR", GL_VENDOR)
    PrintGLString("GL_RENDERER", GL_RENDERER)
    PrintGLString("GL_VERSION", GL_VERSION)
    PrintGLString("GL_SHADING_LANGUAGE_VERSION", GL_SHADING_LANGUAGE_VERSION)
    
    
    #CreateRandomLevelSet("The FitnessGram Pacer test is a multistage aerobic capacity test that progressively gets more difficult as it continues. The 20 meter Pacer test will begin in 30 seconds. Line up at the start. The running speed starts slowly, but gets faster each minute after you hear this signal *boop*. A single lap should be completed each time you hear this sound *ding*. Remember to run in a straight line, and run as long as possible. The second time you fail to complete a lap before the sound, your test is over. The test will begin on the word start. On your mark, get ready, start.")
    try:
        pyglet.app.run()
    finally:
        g.window.close()
        
        
main()
