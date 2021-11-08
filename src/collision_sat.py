##############################
# File :: collision_sat.py
# Written on Thursday,  9 September 2021.
# Author: Henrik Peteri
##############################

from math import ceil, inf
from copy import deepcopy
import collision_aabb
import matrix
import vector

COLLISION_SHAPE_INVALID = 0
COLLISION_SHAPE_CIRCLE = 1
COLLISION_SHAPE_CONVEX = 2

def RemoveDuplicateNormals(normals0):
    normals = []
    normals0_n = ceil(len(normals0) / 2)
    for i in range(normals0_n):
        x = normals0[i * 2]
        y = normals0[i * 2 + 1]
        slope = inf
        if x:
            slope = y / x
        
        duplicate = False
        for ni in range(ceil(len(normals) / 2)):
            normal_x = normals[ni * 2]
            normal_y = normals[ni * 2 + 1]
            
            normal_slope = inf
            if normal_x:
                normal_slope = normal_y / normal_x
        
            if(normal_slope == slope):
                duplicate = True
                break
            
        if not duplicate:
            normals.extend([x,y])
    return normals

class CollisionShape:
    def __init__(self, points=[], r=0):
        self.points = points
        self.r = r
        if not r:
            for i in range(ceil(len(points) / 2)):
                self.r = max(self.r, vector.Length(points[i * 2:2]))
            
        self.cx = 0
        self.cy = 0
        
        l = len(points)
        self.normals = l * [0]
        for i in range(ceil(l / 2)):
            p0_x = points[i * 2 % l]
            p0_y = points[(i * 2 + 1) % l]

            p1_x = points[(i * 2 + 2) % l]
            p1_y = points[(i * 2 + 3) % l]

            self.normals[i * 2] = p1_y - p0_y
            self.normals[i * 2 + 1] = -(p1_x - p0_x)
 
        self.normals = RemoveDuplicateNormals(self.normals)
        
        if not l:
            self.shape = COLLISION_SHAPE_CIRCLE
            self.min_x, self.min_y, self.max_x, self.max_y = collision_aabb.GetAABB_Circle(self.cx, self.cy, self.r)

        else:
            self.shape = COLLISION_SHAPE_CONVEX
            self.min_x, self.min_y, self.max_x, self.max_y =  collision_aabb.GetAABB(self.points)
        
            
    def Copy(self):
        return deepcopy(self)

    def GetAABB(self):
        return self.min_x, self.min_y, self.max_x, self.max_y
    
        
quadShape = CollisionShape(points=[-0.5, 0.5, 0.5, 0.5, 0.5, -0.5, -0.5, -0.5])
circleShape = CollisionShape(r=0.5)
    
##########################################################################################
def HandleCollision_Circle_Circle(shape0, shape1):
    v0_x = shape1.cx - shape0.cx
    v0_y = shape1.cy - shape0.cy

    d = vector.Length([v0_x, v0_y])
    
    allowed_d = shape0.r + shape1.r
    
    if not d:
        return 0, -allowed_d
    
    if d < allowed_d:
        return v0_x / d * -(d - allowed_d), v0_y / d * -(d - allowed_d)

    return 0, 0    

#shape0 is a circle
def HandleCollision_Circle_Convex(shape0, shape1):
    min_d = inf
    circleAxis = [0, 0]
    pointCount = ceil(len(shape1.points) / 2)
    for i in range(pointCount):
        axis = [shape1.points[i * 2] - shape0.cx,
               shape1.points[i * 2 + 1] - shape0.cy]
        d = vector.Length(axis)
        if d < min_d:
            min_d = d
            circleAxis = [axis[0] / d, axis[1] / d]

    normals = RemoveDuplicateNormals(circleAxis + shape1.normals[:])
    normals_n = ceil(len(normals) / 2)
    ############################################################
    points0 = [shape0.cx, shape0.cy]
    points1 = shape1.points
    points0_n = 1
    points1_n = ceil(len(points1) / 2)
    ############################################################
    shortestDistance = inf
    shortestDistanceIndex = 0
    inverseMul = 1
    
    def GetShortestSeparatingAxis(min0, max0, min1, max1, i, shortestDistance, shortestDistanceIndex):
        delta = max1 - min0
        other_delta = max0 - min1

        if other_delta < delta:
            delta = -other_delta
            
        if abs(delta) < abs(shortestDistance):
            shortestDistance = delta
            shortestDistanceIndex = i

        return shortestDistance, shortestDistanceIndex

    def GetProjectionMinMax(points, pointCount, normal, checkY):
        min0 = inf
        max0 = -inf
        for i in range(pointCount):
            dot = vector.DotProduct(points[i * 2 : i * 2 + 2], normal)

            max0 = max(max0, dot)
            min0 = min(min0, dot)

        return min0, max0
    
    for i in range(normals_n):
        checkY = 0
        if not normals[i * 2]:
            checkY = 1

        min0, max0 = GetProjectionMinMax(points0, points0_n, normals[i * 2: i * 2 + 2], checkY)
        min0 -= shape0.r
        max0 += shape0.r
                
        min1, max1 = GetProjectionMinMax(points1, points1_n, normals[i * 2: i * 2 + 2], checkY)

        if (max0 < min1 or max1 < min0):
            return 0, 0
        
        ## moved shape is 'lower'
        if max0 > min1:
            shortestDistance, shortestDistanceIndex = GetShortestSeparatingAxis(min1, max1, min0,  max0, i, shortestDistance, shortestDistanceIndex)
            inverseMul = -1
            
        ## other shape is 'lower'
        elif max1 > min0:
            shortestDistance, shortestDistanceIndex = GetShortestSeparatingAxis(min0, max0, min1, max1, i, shortestDistance, shortestDistanceIndex)
            inverseMul = 1
            
    x = normals[shortestDistanceIndex * 2]
    y = normals[shortestDistanceIndex * 2 + 1]

    if x < 0 or (not x and y < 0):
        x *= -1
        y *= -1
    else:
        shortestDistance *= -1

    return x * shortestDistance * inverseMul, y * shortestDistance * inverseMul

def HandleCollision_Convex_Convex(shape0, shape1):
    normals = RemoveDuplicateNormals(shape0.normals[:] + shape1.normals[:])
    normals_n = ceil(len(normals) / 2)
    ############################################################   
    points0 = shape0.points
    points1 = shape1.points
    points0_n = ceil(len(points0) / 2)
    points1_n = ceil(len(points1) / 2)
    ############################################################
    
    shortestDistance = inf
    shortestDistanceIndex = 0
    inverseMul = 1
    
    def GetShortestSeparatingAxis(min0, max0, min1, max1, i, shortestDistance, shortestDistanceIndex):
        delta = max1 - min0
        other_delta = max0 - min1

        if other_delta < delta:
            delta = -other_delta
            
        if abs(delta) < abs(shortestDistance):
            shortestDistance = delta
            shortestDistanceIndex = i

        return shortestDistance, shortestDistanceIndex

    def GetProjectionMinMax(points, pointCount, normal, checkY):
        min0 = inf
        max0 = -inf
        
        for i in range(pointCount):
            dot = vector.DotProduct(points[i * 2 : i * 2 + 2], normal)

            max0 = max(max0, dot)
            min0 = min(min0, dot)

        return min0, max0
    
    for i in range(normals_n):
        checkY = 0
        if not normals[i * 2]:
            checkY = 1

        min0, max0 = GetProjectionMinMax(points0, points0_n, normals[i * 2: i * 2 + 2], checkY)
        min1, max1 = GetProjectionMinMax(points1, points1_n, normals[i * 2: i * 2 + 2], checkY)

        if (max0 < min1 or max1 < min0):
            return 0, 0
        
        ## moved shape is 'lower'
        if max0 > min1:
            shortestDistance, shortestDistanceIndex = GetShortestSeparatingAxis(min1, max1, min0,  max0, i, shortestDistance, shortestDistanceIndex)
            inverseMul = -1
            
        ## other shape is 'lower'
        elif max1 > min0:
            shortestDistance, shortestDistanceIndex = GetShortestSeparatingAxis(min0, max0, min1, max1, i, shortestDistance, shortestDistanceIndex)
            inverseMul = 1
            
    x = normals[shortestDistanceIndex * 2]
    y = normals[shortestDistanceIndex * 2 + 1]

    if x < 0 or (not x and y < 0):
        x *= -1
        y *= -1
    else:
        shortestDistance *= -1

    return x * shortestDistance * inverseMul, y * shortestDistance * inverseMul

            
def HandleCollision_SAT(shape0, shape1):    
    
    if shape0.shape == COLLISION_SHAPE_CIRCLE:
        return HandleCollision_Circle_Convex(shape0, shape1)
    if shape1.shape == COLLISION_SHAPE_CIRCLE:
        x, y = HandleCollision_Circle_Convex(shape1, shape0)
        return -x, -y;
    
    return HandleCollision_Convex_Convex(shape0, shape1)            
    

##########################################################################################
def GetCollisionShapeCopy_Transformed(shape, x, y, scale_x, scale_y, rot):
    shape = shape.Copy()
    shape.cx = x
    shape.cy = y
    model = matrix.GetModelMatrix(x, y, scale_x, scale_y, rot)
        
    normals = shape.normals
    normals_n = ceil(len(normals) / 2)
       
    for i in range(normals_n):
        normals[i * 2], normals[i * 2 + 1], z, w = matrix.Mul_Vec_Mat([normals[i * 2], normals[i * 2] + 1, 0, 1], matrix.RotateZ(rot))
        
    points = shape.points
    points_n = ceil(len(points) / 2)
    
    for i in range(points_n):
        points[i * 2], points[i * 2 + 1], z, w = matrix.Mul_Vec_Mat([points[i * 2], points[i * 2 + 1], 0, 1], model)

    shape.r *= max(scale_x, scale_y)

    
    if shape.shape == COLLISION_SHAPE_CIRCLE:
        shape.min_x, shape.min_y, shape.max_x, shape.max_y = collision_aabb.GetAABB_Circle(shape.cx, shape.cy, shape.r)
    elif shape.shape == COLLISION_SHAPE_CONVEX:
        shape.min_x, shape.min_y, shape.max_x, shape.max_y =  collision_aabb.GetAABB(shape.points)
       
    return shape
    

##########################################################################################    

