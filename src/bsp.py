##############################
# File :: bsp.py
# Written on Thursday, 23 September 2021.
# Author: Henrik Peteri
##############################

from collision_aabb import CheckCollision_AABB_EntirelyInside as AABB

class BSP:
    def __init__(self, min_x, min_y, max_x, max_y, parent=None):
        self.min_x = min_x
        self.min_y = min_y
        
        self.max_x = max_x
        self.max_y = max_y

        self.count = 0
        self.container = []
        self.partition0 = None
        self.partition1 = None
        self.parent = parent
        if self.parent:
            self.depth = parent.depth + 1
        else:
            self.depth = 0
            
    def CreatePartition(self):
        width = self.max_x - self.min_x
        height = self.max_y - self.min_y
        if width > height:
            self.partition0 = BSP(self.min_x, self.min_y, self.min_x + width / 2, self.max_y, self)
            self.partition1 = BSP(self.min_x + width / 2, self.min_y, self.max_x, self.max_y, self)
        else:
            self.partition0 = BSP(self.min_x, self.min_y, self.max_x, self.min_y + height / 2, self)
            self.partition1 = BSP(self.min_x, self.min_y + height / 2, self.max_x, self.max_y, self)

    def Insert(self, element, min_x, min_y, max_x, max_y):
        self.count += 1
        
        if not self.partition0: 
            self.CreatePartition()

        if AABB(min_x, min_y, max_x, max_y, self.partition0.min_x, self.partition0.min_y, self.partition0.max_x, self.partition0.max_y):
            self.partition0.Insert(element, min_x, min_y, max_x, max_y)
            return

        if AABB(min_x, min_y, max_x, max_y, self.partition1.min_x, self.partition1.min_y, self.partition1.max_x, self.partition1.max_y):
            self.partition1.Insert(element, min_x, min_y, max_x, max_y)
            return
        self.container.append(element)

    def Remove(self, element, min_x, min_y, max_x, max_y) -> bool:
        if not self.partition0:
            return False
        
        if AABB(min_x, min_y, max_x, max_y, self.partition0.min_x, self.partition0.min_y, self.partition0.max_x, self.partition0.max_y):
            removed = self.partition0.Remove(element, min_x, min_y, max_x, max_y)
            if removed:
                self.count -= 1
            return removed

        if AABB(min_x, min_y, max_x, max_y, self.partition1.min_x, self.partition1.min_y, self.partition1.max_x, self.partition1.max_y):
            removed = self.partition1.Remove(element, min_x, min_y, max_x, max_y)
            if removed:
                self.count -= 1
            return removed
        
        self.container.remove(element)
        self.count -= 1

        if not self.count:
            del self.partition0
            del self.partition1
            
            self.partition0 = None
            self.partition1 = None
        
        return True

    def GetPartition(self, min_x, min_y, max_x, max_y):
        if not self.partition0:
            return self

        if AABB(min_x, min_y, max_x, max_y, self.partition0.min_x, self.partition0.min_y, self.partition0.max_x, self.partition0.max_y):
            return self.partition0.GetPartition(min_x, min_y, max_x, max_y)
                    
        if AABB(min_x, min_y, max_x, max_y, self.partition1.min_x, self.partition1.min_y, self.partition1.max_x, self.partition1.max_y):
            return self.partition1.GetPartition(min_x, min_y, max_x, max_y)
        
        return self
    
    def GetPartitionContainers(self, min_x, min_y, max_x, max_y):
        partition = self.GetPartition(min_x, min_y, max_x, max_y)

        result =  partition.GetPartitionContainers_Child()
        result += partition.GetPartitionContainers_Parent()
        return result

    def GetPartitionContainers_Parent(self):
        if not self.parent:
            return []
        
        result = self.parent.container[:]
        result += self.parent.GetPartitionContainers_Parent()
        return result
    
    def GetPartitionContainers_Child(self):
        result = self.container[:]

        if self.partition0:
            result += self.partition0.GetPartitionContainers_Child()
            result += self.partition1.GetPartitionContainers_Child()
            
        return result
    
        
