
from random import randint, random
import math, sys
import demobase, camerabase, geomutil, grass1

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib, ColorBlendAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage
from direct.interval.LerpInterval import LerpFunc
from direct.actor.Actor import Actor

import grass1demo, skydome2
####################################################################################################################
class Grass1aDemo(grass1demo.Grass1Demo):
    """
    Nature - Grass Demo 1 with light shader
    Testing of creating a grass shader supports ambient and point light
    http://developer.nvidia.com/object/nature_scene.html
    Partly from Ogre
    """
    def __init__(self, parent):
        self.functionlist = [ "Demo01","Demo02","Demo03","Demo04"]
        grass1demo.Grass1Demo.__init__(self, parent)

    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-500,-500,0], [500,500,100],
                     #[-90,45, -2.5], [0,0,0],
                     #Vec3(0,-105,20),
                     [-90,45, -6], [0,0,0],
                     Vec3(0,-80,20),
                     rate=0.5, speed=30)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.Stop()

    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.cameraUpdated, "camupdate")
        #taskMgr.add(self.test1u, "test1u")

    def LoadLights(self):
        self.lightpivot = render.attachNewNode("lightpivot")
        self.lightpivot.setPos(0,0,20)
        self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()

        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 0.99, 0.96, 0.5, 1 ), Vec3(-40,-40,0),
                attenuation=Vec3( 0.1, 0.03, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=self.lightpivot,
                fBulb=True)
        #self.att_pointLight.setLight(render)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setNotifier(self.changelight)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ))
        self.att_ambientLight.setLight(render)

        self.att_grasscolor = demobase.Att_color(False, "Grass Color", Vec4(.07,.11,.05,1))
        self.att_grasscolor.setNotifier(self.changelight)

        self.changelight(None)

    def changelight(self, object):
        self.att_grass.setShaderInfo(self.att_grasscolor.getColor(),self.att_pointLight.light,self.att_pointLight.att_lightcolor.getColor(),self.att_pointLight.light.node().getAttenuation())


    def LoadSkyBox(self):
        #self.att_skydome = skydome1.SkyDome1(render, texturefile='textures/clouds_bw.png')
        self.att_skydome = skydome2.SkyDome2(render)
        self.att_skydome.setStandardControl()
        self.att_skydome.att_skycolor.setColor(Vec4(0.3,0.3,0.3,1))
        #self.att_skydome.setPos(Vec3(0,0,-500))


        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def LoadModels(self):
        self.LoadSkyBox()
        self.att_space = demobase.Att_FloatRange(False,"Grass Spacing",1.0 ,16.0, 5.0, 1);

        self.ground = geomutil.createPlane('myplane',100,100,1,1)
        self.ground.reparentTo(render)
        #self.ground.setShaderAuto()
        #self.ground.setLightOff()

        #groundtex = loader.loadTexture("textures/grass.png")
        #groundtex = loader.loadTexture("textures/dirt.png")
        #self.ground.setTexture(groundtex)
        self.ground.setColor(Vec4(0.1,0.2,0.1,1))
        #self.ground.setTexScale(TextureStage.getDefault(), 100,100)
        self.ground.setTexScale(TextureStage.getDefault(), 10,10)

        self.att_grass = grass1.GrassNode("Grass")

        model1 = grass1.LeafModel("Long leaf", 3, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        model2 = grass1.LeafModel("Short leaf", 3, 12.0, 7.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        model3 = grass1.LeafModel("Shortest leaf", 3, 12.0, 5.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        model4 = grass1.LeafModel("Cross Long leaf", 2, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        model5 = grass1.LeafModel("Plane Long leaf", 1, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        modeldebug = grass1.LeafModel("White debug leaf", 3, 12.0, 10.0, 'shaders/grass2.sha', 'textures/white.png', None)
        self.modellist = [model1, model2, model3, model4, model5, modeldebug ]
        self.model = 0
        self.randompos=True
        self.randomsize=False
        self.setModel()
        #TEMP
        #self.textnode.hide()

        #return
        self.actor= Actor('panda.egg', {'walk' : 'panda-walk.egg'})
        self.actor.setScale(2)
        self.actor.reparentTo(render)
        self.actor.loop("walk")
        #self.actor.setPos(Vec3(0,-10,0))
        self.actor.setPos(Vec3(0,5,0))

        # if I enable the auto shader for the panda, the performance will drop very significantly
        # self.actor.setShaderAuto()

##        test1 = geomutil.createPlane('myplane',4,4,1,1)
##        test1.setPos(20,0,10)
##        test1.setHpr(0,90,0)
##        test1.reparentTo(render)
##        test1.setBillboardPointWorld()
##
##        #test1.setTwoSided( True )
##        test1.setDepthWrite( False )
##        test1.setTransparency( TransparencyAttrib.MAlpha )
##        ts = TextureStage('ts')
##        #ts.setMode(TextureStage.MAdd)
##
##        attrib = ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
##        test1.node().setAttrib(attrib)
##        test1.setBin('fixed', 0)
##        tex = loader.loadTexture("textures/flare1.png")
##        test1.setTexture(ts, tex)
##        test1.setLightOff()
##        test1.setColor(Vec4(1,1,1,1))
##        self.test1 = test1

##    def test1u(self,task):
##        v = abs(math.sin(task.time))
##        self.test1.setColor(Vec4(v,v,v,1))
##        return task.cont
