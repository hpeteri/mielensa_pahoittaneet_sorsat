##############################
# File :: shader.py
# Written on Friday,  3 September 2021.
# Author: Henrik Peteri
##############################
from pyglet.gl import *
import ctypes

class Shader:
    def __init__(self):
        self.handle = 0
        self.projectionLocation = 0

def CheckShaderModuleCompileStatus(module, path):
    success = ctypes.c_int(0)
       
    glGetShaderiv(module, GL_COMPILE_STATUS, ctypes.pointer(success))
    if success:
        return True
    else:
        print("COMPILE ERROR in {}".format(path))

    glError = ctypes.create_string_buffer(1024)
    glGetShaderInfoLog(module, 1024, None, glError)

    errorString = ""
    for i in glError:
        if i == b'\x00':
            break
        errorString += i.decode("utf-8")
                               
    print(errorString)
    return False
    
def LoadShader(shaderSources):
    shader = Shader()
    modules = [0, 0]
    types = [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER]
    
    for i, srcPath in enumerate(shaderSources):
        try:
            with open(srcPath, "rb") as file:
                fileContent = file.read()
                file.close()
                src = ctypes.create_string_buffer(fileContent)
                
                c_src = ctypes.cast(ctypes.pointer(ctypes.pointer(src)), ctypes.POINTER(ctypes.POINTER(GLchar)))
                modules[i] = glCreateShader(types[i])
                glShaderSource(modules[i], 1, c_src, None)
                glCompileShader(modules[i])
                if not CheckShaderModuleCompileStatus(modules[i], srcPath):
                    return Shader()
            
        except IOError:
            print("Failed to load shader source {}".format(src))
            return shader

    shaderHandle = glCreateProgram()
    for shaderModule in modules:
        glAttachShader(shaderHandle, shaderModule)
        
    glLinkProgram(shaderHandle)

    shader.handle = shaderHandle
    
    name = ctypes.create_string_buffer(b"projection")
    shader.projectionLocation = glGetUniformLocation(shader.handle, name)
    return shader

def BindShader(shader):
    glUseProgram(shader.handle)

def UnbindShader():
    glUseProgram(0)
