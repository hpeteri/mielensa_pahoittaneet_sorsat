##############################
# File :: level.py
# Written on Sunday, 12 September 2021.
# Author: Henrik Peteri
##############################
import myGlobals as g
from entityManager import Entity, SerializeEntityTransform, DeSerializeEntityTransform

LEVEL_FILE_VERSION = 1

LEVEL_DIR = "data/levels/"
class Level:
    def __init__(self, name, nextLevelName,width, height, maxShots, walls, boxes, targets):
        self.name = name
        self.nextLevel = nextLevelName
        self.width = width
        self.height = height
        self.maxShots = maxShots

        ##Only used for serialization
        self.walls = walls
        self.boxes = boxes
        self.targets = targets
    def Serialize(self):
        fileContent = ""        
        fileContent += "FileVersion :: {}\n".format(LEVEL_FILE_VERSION)
        fileContent += "name :: {}\n".format(self.name)
        fileContent += "next :: {}\n".format(self.nextLevel)
        fileContent += "w :: {}\n".format(self.width)
        fileContent += "h :: {}\n".format(self.height)
        fileContent += "shots :: {}\n".format(self.maxShots)
        
        fileContent += "walls :: {}\n".format(len(self.walls))
        for it in self.walls:
            fileContent += "{}\n".format(SerializeEntityTransform(it))
        
        fileContent += "boxes :: {}\n".format(len(self.boxes))
        for it in self.boxes:
            fileContent += "{}\n".format(SerializeEntityTransform(it))
            
        fileContent += "targets :: {}\n".format(len(self.targets))
        for it in self.targets:
            fileContent += "{}\n".format(SerializeEntityTransform(it))


        try:
            with open("{}{}.level".format(LEVEL_DIR, self.name), "w") as file:
                file.write(fileContent)
                file.close()
        except Exception as e:
            print("Failed to save level file :: ", e)
    def DeSerialize(self, name):
        fileContent = ""
        try:
            with open("{}{}.level".format(LEVEL_DIR, name), "r") as file:
                fileContent = file.read()
                file.close()
        except Exception as e:
            print("Failed to load level file :: ", e)
            return

        lines = fileContent.split("\n")
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith("FileVersion :: "): ##We don't care about the file version currently
                
                continue
            elif line.startswith("name :: "):
                self.name = line.split("::")[1].strip()
                continue
            elif line.startswith("next :: "):
                self.nextLevel = line.split("::")[1].strip()
                continue            
            elif line.startswith("w :: "):
                self.width = int(line.split("::")[1].strip())
                continue
            elif line.startswith("h :: "):
                self.height = int(line.split("::")[1].strip())
                continue
            elif line.startswith("shots :: "):
                self.maxShots = int(line.split("::")[1].strip())
                continue
            elif line.startswith("walls :: "):
                count = int(line.split("::")[1].strip())
                wall = g.assetHandler.GetAsset("wall")
                i += 1
                for y in range(count):
                    fields = DeSerializeEntityTransform(lines[i + y])
                    x = fields[0]
                    y = fields[1]
                    scale_x = fields[2]
                    scale_y = fields[3]
                    rot_z = fields[4]
                    
                    self.walls.append(Entity(x, y, scale_x, scale_y, rot_z, 0, 0, wall.handle))
            
                continue
            elif line.startswith("boxes :: "):
                count = int(line.split("::")[1].strip())
                box = g.assetHandler.GetAsset("box")
                i += 1
                for y in range(count):
                    fields = DeSerializeEntityTransform(lines[i + y])
                    x = fields[0]
                    y = fields[1]
                    scale_x = fields[2]
                    scale_y = fields[3]
                    rot_z = fields[4]
                    
                    self.boxes.append(Entity(x, y, scale_x, scale_y, rot_z, 0, 0, box.handle))
                continue
            elif line.startswith("targets :: "):
                count = int(line.split("::")[1].strip())
                target = g.assetHandler.GetAsset("target")
                i += 1
                for y in range(count):
                    fields = DeSerializeEntityTransform(lines[i + y])
                    x = fields[0]
                    y = fields[1]
                    scale_x = fields[2]
                    scale_y = fields[3]
                    rot_z = fields[4]
                    
                    self.targets.append(Entity(x, y, scale_x, scale_y, rot_z, 0, 0, target.handle))
                continue
                        
