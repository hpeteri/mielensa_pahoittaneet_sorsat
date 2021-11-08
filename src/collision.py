##############################
# File :: collision.py
# Written on Friday, 24 September 2021.
# Author: Henrik Peteri
##############################
from collision_sat import *
from collision_aabb import * 

def HandleCollision(shape0, shape1):
    if not CheckCollision_AABB(shape0.min_x, shape0.min_y, shape0.max_x, shape0.max_y,
                                              shape1.min_x, shape1.min_y, shape1.max_x, shape1.max_y):
        return 0, 0
    if (shape0.shape == COLLISION_SHAPE_CIRCLE and
        shape1.shape == COLLISION_SHAPE_CIRCLE):
        return HandleCollision_Circle_Circle(shape0, shape1)
    
    return HandleCollision_SAT(shape0, shape1)
