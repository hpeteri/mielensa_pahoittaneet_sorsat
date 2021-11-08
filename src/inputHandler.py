##############################
# File :: inputHandler.py
# Written on Friday,  3 September 2021.
# Author: Henrik Peteri
##############################
import myGlobals as g
import time
import math

VIRTUAL_KEY_FLAG_IS_DOWN = 1 
VIRTUAL_KEY_FLAG_WAS_DOWN = 1 << 1

class VirtualKey:
    def __init__(self):
        self.flags = 0

        # Converts int to char; 32 [space] -> " "
def IntToChar(keycode) -> str:
        if type(keycode) == int:
            if keycode > 255:
                return "INVALID"
            return chr(keycode)
        return keycode
    

mousePosition_x = 0
mousePosition_y = 0
mouseDelta_x = 0
mouseDelta_y = 0

keyboardBufferIndex = 0
keyboardBufferSize = math.ceil(g.max_dt / g.sim_dt_step) + 1
keyboardBuffer = [{}] * keyboardBufferSize
    
def HandleKeyEvent(keycode, isDown):
    global keyboardBuffer
    global keyboardBufferSize
    eventTime = time.time_ns()
    keyEventIndex = min(math.floor(((eventTime - g.startTime) * 10 ** -9) / g.sim_dt_step),
                        keyboardBufferSize - 1)
    
    
    key = None
    keycode = IntToChar(keycode)

        
    keyboard = keyboardBuffer[(keyboardBufferIndex + keyEventIndex) % keyboardBufferSize]
    try:
        key = keyboard[keycode]
    except KeyError:
        keyboard[keycode] = VirtualKey()
        key = keyboard[keycode]

    if isDown:
        key.flags |= VIRTUAL_KEY_FLAG_IS_DOWN
    else:
        key.flags &= VIRTUAL_KEY_FLAG_WAS_DOWN    
        
def UpdateKeyboard():
    global keyboardBufferIndex

    keyboard = keyboardBuffer[keyboardBufferIndex].copy()

    for key in keyboard.values():
        down = key.flags & VIRTUAL_KEY_FLAG_IS_DOWN        
        key.flags = ((key.flags << 1) & 0b11) | (key.flags & VIRTUAL_KEY_FLAG_IS_DOWN)
        key.flags |= down

    keyboardBufferIndex = (keyboardBufferIndex + 1) % keyboardBufferSize

    currentKeyboard = keyboardBuffer[keyboardBufferIndex % keyboardBufferSize]
    
    
    for key in keyboard.keys():
        currentKeyboard[key].flags = (keyboard[key].flags & VIRTUAL_KEY_FLAG_WAS_DOWN) | (currentKeyboard[key].flags & VIRTUAL_KEY_FLAG_IS_DOWN)

    
def IsKeyDown(keycode) -> bool:
    keycode = IntToChar(keycode)
    keyboard = keyboardBuffer[keyboardBufferIndex]
    try:
        return keyboard[keycode].flags == VIRTUAL_KEY_FLAG_IS_DOWN
    except KeyError:
        return False

def IsKeyUp(keycode) -> bool:
    keycode = IntToChar(keycode)
    keyboard = keyboardBuffer[keyboardBufferIndex]
    try:
        return keyboard[keycode].flags == VIRTUAL_KEY_FLAG_WAS_DOWN
    except KeyError:
        return False

def IsKeyHeld(keycode) -> bool:
    keycode = IntToChar(keycode)
    keyboard = keyboardBuffer[keyboardBufferIndex]
    try:
        return keyboard[keycode].flags == (VIRTUAL_KEY_FLAG_WAS_DOWN | VIRTUAL_KEY_FLAG_IS_DOWN)
    except KeyError:
        return False

def HandleMouseMove(x, y, dx, dy):
    global mousePosition_x
    global mousePosition_y
    global mouseDelta_x
    global mouseDelta_y
    
    mousePosition_x = x
    mousePosition_y = y
    mouseDelta_x = dx
    mouseDelta_y = dy
    
def GetMousePosition():    
    return mousePosition_x, mousePosition_y
def HasMouseMoved():
    return mouseDelta_x or mouseDelta_y
