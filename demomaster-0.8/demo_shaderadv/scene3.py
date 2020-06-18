
#from random import randint, random
import math, sys, thread
import demobase, camerabase, geomutil, skydome2

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.actor.Actor import Actor


####################################################################################################################
class SceneDemo(demobase.DemoBase):
    # not a demo, just a base class
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()

        self.SetShader()
        self.changeParams(None)

##  not working
##            tex1 = loader.loadTexture("textures/8x8PagesSplotches2.png")
##            tex2 = loader.loadTexture("textures/Sepia1D.tga")
##            tex3 = loader.loadTexture("textures/1D_Noise.png")
##            self.addShader("shaders/oldmovie.sha", [ ("SplotchesTx", tex1), ("SepiaTx", tex2), ("noise", tex3) ])


    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-500,-500,10], [500,500,100],
                     #[-90,45, -2.5], [0,0,0],
                     #Vec3(0,-105,20),
                     [-45,45, -6], [0,0,0],
                     Vec3(0,-80,20),
                     rate=0.5, speed=30)
        self.att_cameracontrol.DefaultController()
        #self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.LockAt((0,5,10))
        self.att_cameracontrol.Stop()
        #self.att_cameracontrol.LockPosition()


    	#demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.cameraUpdated, "camupdate")


    def LoadLights(self):
        self.lightpivot = render.attachNewNode("lightpivot")
        self.lightpivot.setPos(0,0,20)
        self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()

        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 0.99, 0.96, 0.5, 1 ), Vec3(-40,-40,0),
                attenuation=Vec3( 0.1, 0.03, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=self.lightpivot,
                fBulb=True)
        self.att_pointLight.att_bulb.setBulbSize(None, 1.4)
        self.att_pointLight.att_bulb.setFireScale(None, 2)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setNotifier(self.changeParams)
        #self.att_pointLight.setNotifier(self.changelight)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        #self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.7, .7, .7, 1 ))
        self.att_ambientLight.setLight(render)

    def LoadSkyBox(self):
        #self.att_skydome = skydome1.SkyDome1(render, texturefile='textures/clouds_bw.png')
        self.att_skydome = skydome2.SkyDome2(render)
        self.att_skydome.setStandardControl()
        self.att_skydome.att_skycolor.setColor(Vec4(0.3,0.3,0.3,1))
        self.att_skydome.setPos(Vec3(0,0,-400))


        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )


    def LoadModels(self):
        self.LoadSkyBox()

        self.ground = geomutil.createPlane('myplane',100,100,1,1)
        self.ground.reparentTo(render)
        groundtex = loader.loadTexture("textures/grassc.jpg")
        #groundtex = loader.loadTexture("textures/dirt.png")
        self.ground.setTexture(groundtex)
        #self.ground.setColor(Vec4(0.1,0.2,0.1,1))


        self.modelnode = render.attachNewNode("models")

        self.teapot = loader.loadModel("models/teapotuv")
        #self.teapot.setTwoSided(True)
        self.teapot.setPos(0,0,0)
        self.teapot.setColor(1,1,0.5,1)
        self.teapot.reparentTo(self.modelnode)
        self.teapot.setScale(8)
        self.teapot.setH(90)

        nops = loader.loadTexture("models/nops.png")
        nops.setWrapU(Texture.WMRepeat)
        nops.setWrapV(Texture.WMRepeat)
        self.teapot.setTexture(nops, 1)

    def ClearScene(self):
        self.modelnode.clearShader()
        taskMgr.remove("camupdate")

        if hasattr(self, "att_skydome"):
            self.att_skydome.Destroy()

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)


    def cameraUpdated(self, task):
        self.att_skydome.skybox.setShaderInput('time', task.time)
        self.changeParams(None)

        return task.cont

