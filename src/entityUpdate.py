##############################
# File :: entityUpdate.py
# Written on Saturday, 25 September 2021.
# Author: Henrik Peteri
##############################
import myGlobals as g
import collision
import vector

def ShouldShotBeRemoved(e):
    scale = max(e.scale_x, e.scale_y)   
    if e.x < 0 - scale:
        return True
    if e.x > g.currentLevel.width + scale:
        return True
    
    if e.y < 0 - scale:
        return True
    if e.y > g.currentLevel.height + scale:
        return True
    
    
    return vector.Length([e.dir_x, e.dir_y]) < 0.1 and e.collidedThisFrame
            
def UpdateEntitiesAndHandleCollisions(dt, entities, bsp):
    for e in entities:
        e.ResetPerFrameVariables()
        e.dir_y -= g.GRAVITY * dt
                
        e.x += e.dir_x * e.speed * dt
        e.y += e.dir_y * e.speed * dt
        
        e.UpdateCollision(collision.circleShape)
        
        statics = bsp.GetPartitionContainers(e.collisionShape.min_x,
                                             e.collisionShape.min_y,
                                             e.collisionShape.max_x,
                                             e.collisionShape.max_y)
        
        for static in statics:
            sep_x, sep_y = collision.HandleCollision(e.collisionShape, static.collisionShape)

            if not (sep_x or sep_y):
                continue

            e.x -= sep_x
            e.y -= sep_y
            e.collidedThisFrame = True
            
            e.UpdateCollision(collision.circleShape)
            
            reflectionAxis = vector.Normalize([sep_x, sep_y])
            reflection = vector.Reflect([e.dir_x, e.dir_y], reflectionAxis)
            e.dir_x = reflection[0] * 0.75
            e.dir_y = reflection[1] * 0.75
            
