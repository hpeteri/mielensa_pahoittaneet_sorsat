##############################
# File :: renderer.py
# Written on Thursday,  2 September 2021.
# Author: Henrik Peteri
##############################
from pyglet.gl import *
import ctypes

import math
import matrix

import myGlobals as g
from shader import BindShader, UnbindShader
from texture import BindTexture

MAX_BATCH_COUNT = 500


class Vertex(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float),
                ("y", ctypes.c_float),
                ("tcx", ctypes.c_float),
                ("tcy", ctypes.c_float)]
                
    def __init__(self, x, y, tcx, tcy):
        self.x, self.y = x, y
        self.tcx, self.tcy = tcx, tcy
        

    def __str__(self):
        return "{} {} {} {} {}".format(self.x, self.y, self.tcx, self.tcy, self.color)

class Instance(ctypes.Structure):
    _fields_ = [("transform_col0", ctypes.c_float * 4),
                ("transform_col1", ctypes.c_float * 4),
                ("transform_col2", ctypes.c_float * 4),
                ("transform_col3", ctypes.c_float * 4),
                ("color", ctypes.c_uint)]
    
    def __init__(self, x, y, scale_x,  scale_y, z_rot, color):
        model = matrix.Mul_Mat_Mat(matrix.RotateZ(z_rot), matrix.Scale(scale_x, scale_y, 1))
        model = matrix.Mul_Mat_Mat(matrix.Translate(x, y, 1), model)
        self.transform_col0 = (ctypes.c_float * 4)(*[model[0], model[1], model[2], model[3]])
        self.transform_col1 = (ctypes.c_float * 4)(*[model[4], model[5], model[6], model[7]])
        self.transform_col2 = (ctypes.c_float * 4)(*[model[8], model[9], model[10], model[11]])
        self.transform_col3 = (ctypes.c_float * 4)(*[model[12], model[13], model[14], model[15]])
        self.color = color
        
class DrawCall:
    def __init__(self):
        self.gl_vertexBufferSize = 0
        self.gl_vertexBuffer = None
        self.gl_indexBufferSize = 0
        self.gl_indexBuffer = None
        self.batches = []
        
class Batch():    
    def __init__(self):
        self.textureHandle = 0
        self.count = 0
        self.instances = (Instance * MAX_BATCH_COUNT)()
        self.gl_instanceBufferSize = ctypes.sizeof(Instance) * MAX_BATCH_COUNT
        self.gl_instanceBuffer  = CreateInstanceBuffer(self.gl_instanceBufferSize, None)
        
class BufferObject(ctypes.Structure):
    _fields_ = [("bufferID", GLuint),
                ("bufferType", GLenum)]
    def __init__(self, bufferID, bufferType):
        self.bufferID = bufferID
        self.bufferType = bufferType

def CreateBuffer(bufferType, size, data, use):
    bufferID = ctypes.c_uint()
    glGenBuffers(1, ctypes.pointer(bufferID))
    if not bufferID:
        return 0

    if size:
        glBindBuffer(bufferType, bufferID)
        glBufferData(bufferType, size, data, use)
        glBindBuffer(bufferType, 0)

    return BufferObject(bufferID, bufferType)
    
def CreateIndexBuffer(size = 0, data = None):
    return CreateBuffer(GL_ELEMENT_ARRAY_BUFFER, size, data, GL_STATIC_READ)
    
def CreateVertexBuffer(size = 0, data = None):
    return CreateBuffer(GL_ARRAY_BUFFER, size, data, GL_STATIC_READ)

def CreateUniformBuffer(size = 0, data = None):
    return CreateBuffer(GL_UNIFORM_BUFFER, size, data, GL_DYNAMIC_READ)

def CreateInstanceBuffer(size = 0, data = None):
    return CreateBuffer(GL_ARRAY_BUFFER, size, data, GL_DYNAMIC_READ)

def BindBuffer(bufferObject):
    glBindBuffer(bufferObject.bufferType, bufferObject.bufferID)

def UnbindBuffer(bufferObject):
    glBindBuffer(bufferObject.bufferType, 0)

def FillBuffer(bufferObject, size, data, use):
    BindBuffer(bufferObject)
    glBufferData(bufferType, size, data, use)
    UnbindBuffer(bufferObject)    

######################################################################
# RenderTarget
class RenderTarget():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.frameBufferID = ctypes.c_uint(0)
        self.colorAttachment = ctypes.c_uint(0)

        ## Create color attachment texture
        glGenTextures(1, ctypes.pointer(self.colorAttachment))
        glBindTexture(GL_TEXTURE_2D, self.colorAttachment)

        glTexImage2D(GL_TEXTURE_2D, 0,GL_RGBA, self.width, self.height, 0,GL_RGBA, GL_UNSIGNED_BYTE, 0);

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glBindTexture(GL_TEXTURE_2D, 0)
        
        #Create FrameBuffer and attach attachments
        glGenFramebuffers(1,ctypes.pointer(self.frameBufferID))
        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBufferID)
    
        glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, self.colorAttachment, 0);
        glBindFramebuffer(GL_FRAMEBUFFER,0);

    def Resize(self, width, height):
        self.width = width
        self.height = height

        glBindFramebuffer(GL_FRAMEBUFFER, self.frameBufferID)
        glBindTexture(GL_TEXTURE_2D, self.colorAttachment)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, 0);
        glBindRenderbuffer(GL_RENDERBUFFER,0);
        
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.frameBufferID)

        glClear(GL_COLOR_BUFFER_BIT)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER,0);
        
def SetRenderTarget(renderTargetID, width, height):
    glBindFramebuffer(GL_FRAMEBUFFER, renderTargetID)
    glViewport(0, 0, width, height)

def BlitRenderTarget(src, src_x, src_y, src_width, src_height, dst, dst_x, dst_y, dst_width, dst_height):
    
    glBindFramebuffer(GL_READ_FRAMEBUFFER,src)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER,dst);
    
    glBlitFramebuffer(src_x,
                      src_y,
                      src_width,
                      src_height,
                      dst_x,
                      dst_y,
                      dst_width,
                      dst_height,
                      GL_COLOR_BUFFER_BIT,
                      GL_NEAREST);
######################################################################        
class Renderer:
    def GetNewBatch(self):
        if len(self.batchPool):
            batch = self.batchPool.pop()
            batch.count = 0
            return batch

        return Batch()

    def FindMatchingBatch(self, drawCall, textureHandle):
        if len(drawCall.batches):
            for batch in drawCall.batches:

                if not batch.textureHandle == textureHandle:
                    continue
                if batch.count == MAX_BATCH_COUNT:
                    continue
                return batch
            
        batch = self.GetNewBatch()
        batch.textureHandle = textureHandle
        drawCall.batches.append(batch)
        return batch
        
    def __init__(self):
        self.drawCalls = {}
        self.batchPool = []
        
        #Create VertexArrayObject
        self.vao = ctypes.c_uint()
        glGenVertexArrays(1, ctypes.pointer(self.vao))
        glBindVertexArray(self.vao)

        drawCall = DrawCall()
        vertexSize = ctypes.sizeof(Vertex)

        #Default quad drawCall
        vertices = (Vertex * 4)(*[Vertex(-.5, -.5, 0, 1), Vertex(-.5, 0.5, 0, 0), Vertex(0.5, 0.5, 1, 0), Vertex(0.5, -.5, 1, 1)])
        indices = (ctypes.c_ubyte * 6)(*[0, 1, 2, 0, 2, 3])
        
        drawCall.gl_vertexBufferSize = 4 * vertexSize
        drawCall.gl_vertexBuffer = CreateVertexBuffer(drawCall.gl_vertexBufferSize, vertices)

        drawCall.gl_indexBufferSize = 6
        drawCall.gl_indexBuffer = CreateIndexBuffer(drawCall.gl_indexBufferSize, indices)
        
        drawCall.batches = [self.GetNewBatch()]
        self.drawCalls["quad"] = drawCall
        
    def PushDrawCall(self, name, textureHandle, x, y, scale_x, scale_y, rot_z, color):
        drawCall = None
        try:
           drawCall = self.drawCalls[name]                        
        except KeyError:
            print("Could not find drawcall for {}".format(name))
            return            

        
        batch = self.FindMatchingBatch(drawCall, textureHandle)
        batch.instances[batch.count] = Instance(x, y, scale_x, scale_y, rot_z, color)
        batch.count += 1
            
    def Flush(self, width, height):
        if width == 0 or height == 0:
            for drawCall in self.drawCalls.values():
                self.batchPool.extend(drawCall.batches)
                drawCall.batches = []
                drawCall.instanceCount = 0
            return
            
        vertexSize = ctypes.sizeof(Vertex)
        instanceSize = ctypes.sizeof(Instance)
                        
        shader = g.assetHandler.GetAsset("pixelShader")
        BindShader(shader)  
        
        ortho = (ctypes.c_float * 16)(*matrix.Orthographic(0, width, height, 0,  -1, 1000))
                
        glUniformMatrix4fv(shader.projectionLocation, 1, GL_FALSE, ortho)
        

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)
        glEnableVertexAttribArray(3)
        glEnableVertexAttribArray(4)
        glEnableVertexAttribArray(5)
        glEnableVertexAttribArray(6)            
        
        for drawCall in self.drawCalls.values():
        
            #Vertex data which is shared by instances
            BindBuffer(drawCall.gl_vertexBuffer)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, vertexSize, 0)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertexSize, 8)

            #Instance transform matrix
            for batch in drawCall.batches:
                BindTexture(batch.textureHandle)
                BindBuffer(batch.gl_instanceBuffer)
                glBufferSubData(batch.gl_instanceBuffer.bufferType, 0, batch.count * instanceSize, batch.instances)

                #Instance Transform
                glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, instanceSize, 0)
                glVertexAttribDivisor(2, 1)
                glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, instanceSize, 16)
                glVertexAttribDivisor(3, 1)
                glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, instanceSize, 32)
                glVertexAttribDivisor(4, 1)
                glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, instanceSize, 48)
                glVertexAttribDivisor(5, 1)
            
                #Instance color
                glVertexAttribPointer(6, 4, GL_UNSIGNED_BYTE, GL_FALSE, instanceSize, 64)
                glVertexAttribDivisor(6, 1)

                #Element buffer
                BindBuffer(drawCall.gl_indexBuffer)
                glDrawElementsInstanced(GL_TRIANGLES, drawCall.gl_indexBufferSize, GL_UNSIGNED_BYTE, None, batch.count)
                UnbindBuffer(batch.gl_instanceBuffer)
                              
            self.batchPool.extend(drawCall.batches)
            drawCall.batches = []
            drawCall.instanceCount = 0
            
            UnbindBuffer(drawCall.gl_indexBuffer)
            UnbindBuffer(drawCall.gl_vertexBuffer)

        UnbindShader()
            
        BindTexture(0)
        
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)
        glDisableVertexAttribArray(2)
        glDisableVertexAttribArray(3)
        glDisableVertexAttribArray(4)
        glDisableVertexAttribArray(5)
        glDisableVertexAttribArray(6)


renderer = Renderer()
