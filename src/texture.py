##############################
# File :: texture.py
# Written on Friday,  3 September 2021.
# Author: Henrik Peteri
##############################
from pyglet.gl import *

import ctypes #OpenGL functions need C-type arrays
import png

class Texture:
    def __init__(self, handle, width, height):
        self.handle = handle
        self.width = width
        self.height = height
def LoadTexture(path):
    try:
        r = png.Reader(filename=path)
        w, h, pixels, metadata = r.read_flat()
        return CreateTexture(pixels, w, h)
    except Exception:
        print("Failed to load texture [}".format(path))
        return CreateTexture([], 4, 4)
                
def CreateTexture(fileContent, width, height) -> Texture:
    size = width * height* 4
   
    data = (GLbyte * size)(*fileContent)

    if not len(fileContent):
        ctypes.memset(data, 255, size)

    textureID = (GLuint * 1)()
    glGenTextures(1, textureID)
    glBindTexture(GL_TEXTURE_2D, *textureID)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glBindTexture(GL_TEXTURE_2D, 0)

    texture = Texture(textureID[0], width, height)
    return texture
    
def BindTexture(handle):
    glBindTexture(GL_TEXTURE_2D, handle)
