
from random import randint, random
import math, sys
import demobase, camerabase, geomutil, grass1

#from pandac.PandaModules import Filename
#from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage

class Hairs():
    def __init__(self, parent):
        self.att_hairs = grass1.GrassNode("Hair",parentnode=parent,
            #color=Vec4(0.6,0.6,0.6,1))
            #color=Vec4(1,1,1,1))
            #color=Vec4(.902,0.615,0.213,1))
            color=Vec4(.6302,0.425,0.153,1))
            #Vec4(1,1,1,1))
        hairmodel = grass1.LeafModel("Hair", 2, 0.25, 0.25, 'shaders/grass1color.sha', 'textures/hair2.png', None)
        self.att_hairs.setModel(hairmodel)

    def BuildHairs(self, vtxlist, l = 1):
        self.att_hairs.reset()
        for info in vtxlist:
            vtx,normal = info
            pos = vtx
            v = 0.5
            h = l * (v + (1-v) * random())
            x = vtx[0]
            y = vtx[1]
            z = vtx[2]
            v = 0.05
            m = v  - v * random() * 2
            x += m
            m = v  - v * random() * 2
            y += m
            #m = v  - v * random() * 2
            #z -= m
            #if abs(x) < 1:
            #    h += (1-abs(x)) * 0.5

            np = self.att_hairs.addGrassWithModel(Vec3(x,y,z), 0)
            np.setScale(1,1,h)
            v = 25
            m1 = v - random() * v * 2
            m2 = v - random() * v * 2
            m3 = v - random() * v * 2
            np.setHpr(m1,m2,m3)
        self.att_hairs.flatten()
        self.att_hairs.setTime(0)

    def setColor(self, color):
        self.att_hairs.setColor(color)

    def Destroy(self):
        self.att_hairs.Destroy()