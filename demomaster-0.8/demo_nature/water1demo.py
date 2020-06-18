from random import randint, random
import math, sys, os
import demobase, camerabase, splashCard

from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3

#from skydome import *
import waterplane1
import ocean2demo

####################################################################################################################
class Water1Demo(ocean2demo.Ocean2Demo):
    """
    Nature - Water shader from yarr
    Water shader from yarr
    """
    def __init__(self, parent):
        self.functionlist = ["Demo01"]
        ocean2demo.Ocean2Demo.__init__(self, parent)

    def LoadWaterNode(self):
        #self.att_water = ocean2.WaterNode(1000,1000,50,50, self._water_level.getZ())
        self.att_water = waterplane1.WaterNode(-500,-500,500,500, self._water_level.getZ())
        self.att_water.setStandardControl()

