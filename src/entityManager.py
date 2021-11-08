##############################
# File :: entityManager.py
# Written on Thursday,  2 September 2021.
# Author: Henrik Peteri
##############################
import math
import matrix
from copy import deepcopy
import bsp
import collision_sat
import collision_aabb

DEFAULT_SPEED = 100
class Entity:    
    def __init__(self, x, y, scale_x, scale_y, rot_z=0, dir_x=0, dir_y=0, textureHandle=0):
        self.x = x
        self.y = y
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rot_z = rot_z
        self.speed = DEFAULT_SPEED
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.textureHandle = textureHandle
        self.color = ~0
        self.collidedThisFrame = False
        self.collisionShape = None
    def Copy(self):
        return deepcopy(self)
    def UpdateCollision(self, shape):
        self.collisionShape = collision_sat.GetCollisionShapeCopy_Transformed(shape,
                                                                               self.x, self.y,
                                                                               self.scale_x, self.scale_y,
                                                                               self.rot_z)        
    def ResetPerFrameVariables(self):
        self.collidedThisFrame = False
        
    
def SerializeEntityTransform(entity):
    return "{} {} {} {} {}".format(entity.x, entity.y, entity.scale_x, entity.scale_y, entity.rot_z)

def DeSerializeEntityTransform(line):
    fields = line.split(" ")
    for i in range(len(fields)):
        fields[i] = float(fields[i])
    return fields

class EntityManager:
    def __init__(self):
        self.Reset()
                
    def Reset(self):
        self.entities = []
        self.static = []
        self.targets = []
        self.drawables = []
        self.bsp = None
    
    def Copy(self):
        copy = EntityManager()
        copy.entities = self.entities[:]
        copy.static   = self.static[:]
        copy.targets = self.targets[:]

        for i, e in enumerate(copy.entities):
            copy.entities[i] = e.Copy()
            
        for i, e in enumerate(copy.static):
            copy.static[i] = e.Copy()
            
        for i, e in enumerate(copy.targets):
            copy.targets[i] = e.Copy()

        # Currently we only insert static entities once and don't remove or insert anything
        # so copying isn't neccesary
        copy.bsp = self.bsp 
        return copy

    def BuildBSP(self, width, height):
        self.bsp = bsp.BSP(0, 0, width, height)
        
        for e in self.static:
            e.UpdateCollision(collision_sat.quadShape)
            
            self.bsp.Insert(e,
                            e.collisionShape.min_x, e.collisionShape.min_y,
                            e.collisionShape.max_x, e.collisionShape.max_y)

        for e in self.targets:
            e.UpdateCollision(collision_sat.circleShape)
            
        
