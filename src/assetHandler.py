##############################
# File :: assetHandler.py
# Written on Thursday,  2 September 2021.
# Author: Henrik Peteri
##############################
import os

from texture import * 
from shader import *

#Asset flags
IS_LOADED = 1

#assetTypes
ASSET_TYPE_TEXTURE = "Texture"
ASSET_TYPE_SHADER = "Shader"

DATA_FOLDER =  "data"

class AssetTag:
    def __init__(self):
        self.name = ""
        self.paths = []
        self.assetType = 0
        self.flags = 0
        self.asset = None


def LoadAsset(paths, assetType):
    if assetType == ASSET_TYPE_TEXTURE:
        return LoadTexture(paths[0])
    if assetType == ASSET_TYPE_SHADER:
        return LoadShader(paths)

class AssetHandler():
    def RegisterAssetTag(self, tag):
        self.tags[tag.name] = tag
    def RegisterDefaultTags(self):
        tag = AssetTag()
        tag.name = "sorsa"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/sorsa.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
        
        tag = AssetTag()
        tag.name = "ball"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/ball.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
        
        tag = AssetTag()
        tag.name = "sorsa_portrait"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/sorsa_portrait.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
        
        tag = AssetTag()
        tag.name = "box"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/box.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
            
        tag = AssetTag()
        tag.name = "wall"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/wall.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
                
        tag = AssetTag()
        tag.name = "target"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/target.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
        
        tag = AssetTag()
        tag.name = "sling"
        tag.path = [os.path.join(DATA_FOLDER, "sprites/sling.png")]
        tag.assetType = ASSET_TYPE_TEXTURE
        self.RegisterAssetTag(tag)
        
        ######################################################################
        tag = AssetTag()
        tag.name = "pixelShader"
        tag.path = [os.path.join(DATA_FOLDER, "shaders/pixelShader.vert.glsl"),
                    os.path.join(DATA_FOLDER, "shaders/pixelShader.frag.glsl")]
        
        tag.assetType = ASSET_TYPE_SHADER
        self.RegisterAssetTag(tag)
        ######################################################################    

    def __init__(self):
        self.tags = {}
        self.RegisterDefaultTags()
        
    def GetAsset(self, name):
        try:
            tag = self.tags[name]
            if not tag.flags & IS_LOADED:
                tag.asset = LoadAsset(tag.path, tag.assetType)
                tag.flags |= IS_LOADED
                
            return tag.asset
        except KeyError:
            print("Asset '{}' is not registered".format(name))
        except Exception as e:
            print(e)
        print("Failed to find '{}' from '{}'".format(name, self.tags.keys()))
        return None
