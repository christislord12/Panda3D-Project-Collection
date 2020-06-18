
#from random import randint, random
import math, sys, thread
import demobase, camerabase, geomutil, skydome2

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib, LightRampAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.actor.Actor import Actor


####################################################################################################################
class MiscHDRTestDemo(demobase.DemoBase):
    """
    Misc - HDR Test
    Just show the hdr effects
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        render.setAttrib(LightRampAttrib.makeHdr0())
        render.setShaderAuto()
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.SetupParticle()


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
                attenuation=Vec3( 0.1, 0.00, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=self.lightpivot,
                fBulb=True)
        self.att_pointLight.att_bulb.setBulbSize(None, 1.4)
        self.att_pointLight.att_bulb.setFireScale(None, 2)
        self.att_pointLight.setLight(render)
        #self.att_pointLight.setNotifier(self.changelight)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        #self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.7, .7, .7, 1 ))
        self.att_ambientLight.setLight(render)

    def SetupParticle(self):
        self.particle = ParticleEffect()
        self.particle.loadConfig(Filename("demo_nature/particles/fire2.ptf"))
        p0 = self.particle.getParticlesNamed('particles-1')
        p0.setBirthRate(100000)
        particleRenderNode = render.attachNewNode("fireNode")
        self.particle.start(self.actor.mouthnode, particleRenderNode)
        #particleRenderNode = render.find("BaseParticleRenderer render node")
        particleRenderNode.setBin('fixed', 0)
        particleRenderNode.setDepthWrite(False)
        particleRenderNode.setShaderOff(2)


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
        if True:
            self.actor= Actor('models/fleur/fleur.egg', {'walk' : 'models/fleur/fleur-anim.egg'})
            self.actor.setScale(3.5)
            self.actor.reparentTo(self.modelnode)
            self.actor.neck = self.actor.controlJoint(None, 'modelRoot', 'testa')
            self.actor.mouth = self.actor.controlJoint(None, 'modelRoot', 'mandibola')

            #self.actor.mouthnode = self.actor.mouth.attachNewNode("mouse")
            self.actor.mouthnode = self.actor.exposeJoint(None, 'modelRoot', 'mandibola').attachNewNode("mouth")
            self.actor.loop("walk")
            self.actor.setPos(Vec3(0,5,0))
            mhpr = self.actor.mouth.getHpr()
            mhpr1 = Point3(mhpr[0],mhpr[1]-20,mhpr[2])
            angle = 45
            hprInterval1= self.actor.neck.hprInterval(3,Point3(0,0,angle), startHpr=Point3(0,0,0))
            hprInterval2= self.actor.neck.hprInterval(3,Point3(0,0,-angle), startHpr=Point3(0,0,angle))
            hprInterval3= self.actor.neck.hprInterval(3,Point3(0,0,0), startHpr=Point3(0,0,-angle))
            hprInterval4= self.actor.mouth.hprInterval(1,mhpr1, startHpr=mhpr)
            hprInterval5= self.actor.mouth.hprInterval(1,mhpr, startHpr=mhpr1)
            self.actorseq = Sequence(
                    hprInterval1,
                    hprInterval4,
                    Func(self.fire, 1),Wait(2),Func(self.fire, 0),
                    hprInterval5,
                    hprInterval2,
                    hprInterval4,
                    Func(self.fire, 1),Wait(2),Func(self.fire, 0),
                    hprInterval5,
                    hprInterval3,
                    name = "turnneck")
            self.actorseq.loop()

        if True:
            self.panda= Actor('panda.egg', {'walk' : 'panda-walk.egg'})
            self.panda.setScale(2)
            self.panda.reparentTo(self.modelnode)
            self.panda.loop("walk")
            self.panda.setPos(Vec3(-15,5,0))

        if True:
            self.virus = loader.loadModel("models/virus")
            self.virus.setScale(5)
            self.virus.reparentTo(self.modelnode)
            self.virus.setPos(Vec3(15,5,8))
            hprInterval= self.virus.hprInterval(3,Point3(360,360,0), startHpr=Point3(0,0,0))
            hprInterval.loop()


    def ClearScene(self):
        self.actorseq.finish()
        self.particle.disable()
        self.particle.cleanup()

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
        return task.cont

    def fire(self, mode):
#        return
        if mode > 0:
            h = (self.actor.neck.getR()) / 180 * math.pi
            p0 = self.particle.getParticlesNamed('particles-1')
            p0.setBirthRate(0.05)
            emitter = p0.getEmitter()
            v = 10
            emitter.setExplicitLaunchVector(Vec3(v * math.sin(h), -v * math.cos(h), -1.0000))
        else:
            p0 = self.particle.getParticlesNamed('particles-1')
            p0.setBirthRate(100000.0)


    def Demo01(self):
        "makeHdr0"
        render.setAttrib(LightRampAttrib.makeHdr0())

    def Demo02(self):
        "makeHdr1"
        render.setAttrib(LightRampAttrib.makeHdr1())

    def Demo03(self):
        "makeHdr2"
        render.setAttrib(LightRampAttrib.makeHdr2())
