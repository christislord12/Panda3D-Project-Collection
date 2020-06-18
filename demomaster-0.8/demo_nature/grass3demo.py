
from random import randint, random
import math, sys
import demobase, camerabase, geomutil, grass1, skydome2

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect

from direct.actor.Actor import Actor

####################################################################################################################
class Grass3Demo(demobase.DemoBase):
    """
    Nature - Grass Demo 3, walking forever
    Panda walking at night with moving grass
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.textnode = render2d.attachNewNode("textnode")
        #self.grasstextnode = demobase.addInstructions(-1.0,-0.9, "", align=TextNode.ALeft, node=self.textnode)

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.SetupParticle()

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
        #self.att_cameracontrol.Stop()
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
        #self.att_pointLight.setLight(render)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setNotifier(self.changelight)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        #self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.7, .7, .7, 1 ))
        self.att_ambientLight.setLight(render)

        self.att_grasscolor = demobase.Att_color(False, "Grass Color", Vec4(.07,.11,.05,1))
        self.att_grasscolor.setNotifier(self.changelight)

        self.changelight(None)


    def changelight(self, object):
        grasscolor = self.att_grasscolor.getColor()
        light = self.att_pointLight.light
        lightcolor = self.att_pointLight.att_lightcolor.getColor()
        attenuation = self.att_pointLight.light.node().getAttenuation()
        self.grassfield.setShaderInput('ambient', grasscolor)
        self.grassfield.setShaderInput('light', light)
        self.grassfield.setShaderInput('lightcolor', lightcolor)
        self.grassfield.setShaderInput('attenuation', attenuation[0],attenuation[1],attenuation[2],0 )


    def LoadSkyBox(self):
        #self.att_skydome = skydome1.SkyDome1(render, texturefile='textures/clouds_bw.png')
        self.att_skydome = skydome2.SkyDome2(render)
        self.att_skydome.setStandardControl()
        self.att_skydome.att_skycolor.setColor(Vec4(0.3,0.3,0.3,1))
        self.att_skydome.setPos(Vec3(0,0,-400))


        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def setModel(self):
        # store the position to an array, so that I can do some animations
        self.grassrows = []
        self.model = self.modellist[self.modelno]
        #self.grasstextnode.setText(self.modellist[self.model].name)

        space = self.att_space.v
        y = -90
        #x = 25 + space
        while y < 90:
            grassrow = grass1.GrassNode("Grass", self.grassfield)
            grassrow.setModel(self.model)
            grassrow.reset()
            self.grassrows.append(grassrow)
            x = -50 + space
            while x < 50 - space/2:
                if self.randompos:
                    x1 = x + random() * space - space/2
                    y1 = y + random() * space - space/2
                else:
                    x1 = x
                    y1 = y
                h = random() * 90.0
                np = grassrow.addGrassWithModel(Vec3(x1,y1-y,0), h)
                if self.randomsize:
                    size = random() * 0.3+0.7
                    np.setScale(size)
                x += space
            grassrow.flatten()
            grassrow.grassNP.setPos(0,y,0)
            y += space
        self.totaldisplacement = 0

    def LoadModels(self):
        self.LoadSkyBox()
        self.att_space = demobase.Att_FloatRange(False,"Grass Spacing",1.0 ,16.0, 5.0, 1);
        #self.att_speed = demobase.Att_FloatRange(False,"Walking Speed",0.0 ,40.0, 15, 1);
        self.att_speed = demobase.Att_FloatRange(False,"Walking Speed",0.0 ,40.0, 13, 1);
        self.att_speed.setNotifier(self.speedchange)

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

        self.grassfield = render.attachNewNode("grassfield")

        model1 = grass1.LeafModel("Long leaf", 3, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        #model2 = grass1.LeafModel("Short leaf", 3, 12.0, 7.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        #model3 = grass1.LeafModel("Shortest leaf", 3, 12.0, 5.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        #model4 = grass1.LeafModel("Cross Long leaf", 2, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        #model5 = grass1.LeafModel("Plane Long leaf", 1, 12.0, 10.0, 'shaders/grass2.sha', 'textures/grass_02.png', None)
        #modeldebug = grass1.LeafModel("White debug leaf", 3, 12.0, 10.0, 'shaders/grass2.sha', 'textures/white.png', None)
        #self.modellist = [model1, model2, model3, model4, model5, modeldebug ]
        self.modellist = [model1]
        self.modelno = 0
        self.randompos=True
        self.randomsize=True
        self.setModel()

        if True:
            #self.actor= Actor('models/fleur/fleur-HR.egg', {'walk' : 'models/fleur/fleur-HR-anim.egg'})
            self.actor= Actor('models/fleur/fleur.egg', {'walk' : 'models/fleur/fleur-anim.egg'})
            self.actor.setScale(3.5)
            self.actor.reparentTo(render)
            self.actor.neck = self.actor.controlJoint(None, 'modelRoot', 'testa')
            self.actor.mouth = self.actor.controlJoint(None, 'modelRoot', 'mandibola')

            #self.actor.mouthnode = self.actor.mouth.attachNewNode("mouth")
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

        else:
            self.actor= Actor('panda.egg', {'walk' : 'panda-walk.egg'})
            self.actor.setScale(2)
            self.actor.reparentTo(render)
            self.actor.loop("walk")
            #self.actor.setPos(Vec3(0,-10,0))
            self.actor.setPos(Vec3(0,5,0))

        # if I enable the auto shader for the panda, the performance will drop very significantly
        # self.actor.setShaderAuto()

    def speedchange(self,object):
        self.actor.setPlayRate(1.3 * self.att_speed.v / 13,'walk')

    def ClearScene(self):
        self.actorseq.finish()
        self.particle.disable()
        self.particle.cleanup()

        taskMgr.remove("camupdate")

        if hasattr(self, "att_skydome"):
            self.att_skydome.Destroy()

        for g in self.grassrows:
            g.Destroy()

        if hasattr(self, "att_tree"):
            self.att_tree.Destroy()

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def cameraUpdated(self, task):
        campos = base.camera.getPos()
        render.setShaderInput('time', task.time)

        # hack into grass object, not good practice but fast implementation
        # Grass jitter
        time = task.time
        dx  = 1.8 * math.sin( time * 1.6 )
        dx += 2.1 * math.sin( time * 0.5 )
        dx += 2.6 * math.sin( time * 0.1 )
        dx *= self.model.jitter
        self.grassfield.setShaderInput( 'grass', Vec4(dx,dx,0,1200))

        if hasattr(self, "att_tree"):
            self.att_tree.setTime(task.time)

        # move the grass
        speed = self.att_speed.v
        space = self.att_space.v
        #displacement = min(space, globalClock.getDt() * speed)
        #displacement = globalClock.getDt() * speed
        displacement = 0.03 * speed
        for grassrow in self.grassrows:
            y = grassrow.grassNP.getY()
            grassrow.grassNP.setY(y + displacement)
        self.totaldisplacement += displacement
        if self.totaldisplacement >= space:
            lastrow = self.grassrows[-1]
            y = self.grassrows[0].grassNP.getY() - space
            lastrow.grassNP.setY(y)
            self.grassrows = [lastrow] + self.grassrows[0:-1]
            self.totaldisplacement -= space
        return task.cont


    def fire(self, mode):
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
