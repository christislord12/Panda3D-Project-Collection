from random import randint, random
import math, sys, os
import demobase, camerabase, splashCard

from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3

#from skydome import *
import ocean2
import ocean2demo

####################################################################################################################
class Ocean2SimpleDemo(ocean2demo.Ocean2Demo):
    """
    Nature - Ocean 2 cubemap only
    Only with cubemap support
    """
    def __init__(self, parent):
        self.functionlist = ["Demo01"]
        ocean2demo.Ocean2Demo.__init__(self, parent)

    def LoadWaterNode(self):
        self.att_water = ocean2.WaterNode(1000,1000,50,50, self._water_level.getZ(), True)

        self.att_water.setStandardControl()

