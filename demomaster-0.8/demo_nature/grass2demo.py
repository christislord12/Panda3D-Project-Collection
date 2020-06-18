
from random import randint, random
import math, sys
import demobase, camerabase, geomutil, grass2

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage
from direct.interval.LerpInterval import LerpFunc
from direct.actor.Actor import Actor

import grass1demo, skydome2
####################################################################################################################
class Grass2Demo(grass1demo.Grass1Demo):
    """
    Nature - Grass Demo 2
    Use GrassModel, which can mix diffenent types of leaf
    """
    def __init__(self, parent):
        self.functionlist = [ "Demo01","Demo02","Demo03","Demo04"]
        grass1demo.Grass1Demo.__init__(self, parent)

    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-500,-500,0], [500,500,100],
                     [-90,45, -5], [0,0,0],
                     Vec3(0,-148,38),
                     rate=0.5, speed=60)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.Stop()

    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.cameraUpdated, "camupdate")

    def LoadModels(self):
        self.LoadSkyBox()

        self.att_space = demobase.Att_FloatRange(False,"Grass Spacing",1.0 ,30.0, 5.0, 1);

        self.ground = geomutil.createPlane('myplane',100,100,1,1)
        self.ground.reparentTo(render)
        #self.ground.setShaderAuto()
        #self.ground.setLightOff()

        #groundtex = loader.loadTexture("textures/grass.png")
        groundtex = loader.loadTexture("textures/dirt.png")
        self.ground.setTexture(groundtex)
        #self.ground.setTexScale(TextureStage.getDefault(), 100,100)
        self.ground.setTexScale(TextureStage.getDefault(), 10,10)
        self.att_grass = grass2.GrassNode("Grass")

##        self.tree = geomutil.createPlane('tree',100,80,1,1)
##        self.tree.reparentTo(render)
##        self.tree.setHpr(0,90,0)
##        self.tree.setPos(-30,30,40)
##        self.tree.setTwoSided( True )
##        self.tree.setTransparency( TransparencyAttrib.MAlpha )
##        tex = loader.loadTexture("textures/tree1.png")
##        self.tree.setTexture(tex)
##        self.tree.setLightOff()

        model1 = grass2.GrassModel("Mix", 'shaders/grass1.sha', 'textures/grassPack.png',
                24.0/12.0/2,
            [
                grass2.LeafModel("Green leaf", 2, 12.0,24.0, [ (Point2(0,0.1),Point2(0.25,1)), (Point2(0.5,0.1),Point2(0.75,1))]),
                grass2.LeafModel("Brown leaf", 2, 12.0, 24.0, [ (Point2(0.25,0.1),Point2(0.5,1)), (Point2(0.75,0.1),Point2(1,1))])
            ])
        model2 = grass2.GrassModel("Green Only", 'shaders/grass1.sha', 'textures/grassPack.png',
                24.0/12.0/2,
            [
                grass2.LeafModel("Green leaf", 2, 12.0,24.0, [ (Point2(0,0.1),Point2(0.25,1)), (Point2(0.5,0.1),Point2(0.75,1))]),
            ])
        model3 = grass2.GrassModel("Brown Only", 'shaders/grass1.sha', 'textures/grassPack.png',
                24.0/12.0/2,
            [
                grass2.LeafModel("Brown leaf", 2, 12.0, 24.0, [ (Point2(0.25,0.1),Point2(0.5,1)), (Point2(0.75,0.1),Point2(1,1))])
            ])
        #modeldebug = grass1.LeafModel("White debug leaf", 2, 6.0, 10.0, 'shaders/grass1.sha', 'textures/white.png', None)
        self.modellist = [model1, model2, model3]
        self.model = 0
        self.randompos=True
        self.randomsize=False
        self.setModel()


    def setModel(self):
        self.att_grass.setModel(self.modellist[self.model])
        self.grasstextnode.setText(self.modellist[self.model].name)
        self.LoadEven()

    def LoadEven(self):
        self.att_grass.reset()
        space = self.att_space.v
        x = -50 + space
        #x = 25 + space
        while x < 50 - space/2:
            y = -50 + space
            #y = 25 + space
            while y < 50 - space/2:
                if self.randompos:
                    x1 = x + random() * space - space/2
                    y1 = y + random() * space - space/2
                else:
                    x1 = x
                    y1 = y
                h = random() * 90.0
                #np = self.att_grass.addGrassWithModel(Vec3(x1,y1,0), h)
                leaf = randint(0, len(self.att_grass.model.leafmodels)-1)
                np = self.att_grass.addGrassWithGrassModel(Vec3(x1,y1,0), h, leaf)
                if self.randomsize:
                    size = random() * 0.5+0.5
                    np.setScale(size)
                y += space
            x += space
        self.att_grass.flatten()
