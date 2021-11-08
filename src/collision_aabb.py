##############################
# File :: collision_aabb.py
# Written on Thursday, 23 September 2021.
# Author: Henrik Peteri
##############################
import matrix
from math import inf, ceil

def GetAABB(points):
        
    min_x = inf
    min_y = inf
    max_x = -inf
    max_y = -inf

    for i in range(ceil(len(points) / 2)):
        x, y = points[i * 2], points[i * 2 + 1]
        
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

    
    return min_x, min_y, max_x, max_y
def GetAABB_Circle(cx, cy, r):
    return cx - r, cy -r, cx + r, cy + r
            
def CheckCollision_AABB(min0_x, min0_y, max0_x, max0_y,
                        min1_x, min1_y, max1_x, max1_y):

    return (min0_x < max1_x and max0_x > min1_x and
            min0_y < max1_y and max0_y > min1_y)

def CheckCollision_AABB_EntirelyInside(min0_x, min0_y, max0_x, max0_y,
                        min1_x, min1_y, max1_x, max1_y):

    return (min0_x >= min1_x and max0_x <= max1_x and
            min0_y >= min1_y and max0_y <= max1_y)
