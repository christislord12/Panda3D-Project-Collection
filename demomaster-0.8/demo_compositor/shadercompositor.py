
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
from direct.filter.FilterManager import FilterManager
from pandac.PandaModules import FrameBufferProperties, GraphicsPipe, GraphicsOutput, PNMImage


####################################################################################################################
class ShaderCompositorDemo(demobase.DemoBase):
    """
    Shaders - Compositor
    Filter Manager with various 2D shader port from Orge Demos
    Some shaders require 3D Texture, so only run on version 1.6.x or later
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)

        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.SetupParticle()
        self.manager = None
        self.quadlist = []
        self.shaderlist = []

        self.manager = FilterManager(base.win, base.cam)
        self.noisetex = loader.loadTexture("textures/normalNoiseColor.png")


        self.motion = False
        self.addSnapshot = False
        self.snapshotbuffer = None
        self.count = 0
        self.savetex = [Texture(), Texture()]
        #winprops = WindowProperties().getDefault()
        #xsize = winprops.getXSize()
        #ysize = winprops.getYSize()



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
        self.att_cameracontrol.LockAt((0,5,16))
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
                attenuation=Vec3( 0.1, 0.01, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=self.lightpivot,
                fBulb=True)
        self.att_pointLight.att_bulb.setBulbSize(None, 1.4)
        self.att_pointLight.att_bulb.setFireScale(None, 2)
        self.att_pointLight.setLight(render)
        #self.att_pointLight.setNotifier(self.changelight)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        #self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .4, 1 ))
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.8, .8, .8, 1 ))
        self.att_ambientLight.setLight(render)
        #self.att_ambientLight2 = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.7, .7, .7, 1 ))
        #self.att_ambientLight2.setLight(self.actor)

    def SetupParticle(self):
        self.particle = ParticleEffect()
        self.particle.loadConfig(Filename("demo_nature/particles/fire3.ptf"))
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
        self.groundts = TextureStage('grass')
        #groundtex = loader.loadTexture("textures/dirt.png")
        self.ground.setTexture(self.groundts, groundtex)
        #self.ground.setColor(Vec4(0.1,0.2,0.1,1))

        if True:
            self.actor= Actor('models/fleur/fleur.egg', {'walk' : 'models/fleur/fleur-anim.egg'})
            self.actor.setScale(3.5)
            self.actor.reparentTo(render)
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

    def ClearScene(self):
        self.Reset()
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
        if self.motion and self.snapshotbuffer != None:
            self.motioncount += 1
            if self.motioncount >= self.motionframes:
                # switching textures so that I can use it in motion detection shader
                self.count = (1 + self.count) % 2
                self.snapshotbuffer.clearRenderTextures()
                self.snapshotbuffer.addRenderTexture(self.snapshottex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
                self.snapshotbuffer.addRenderTexture(self.savetex[self.count], GraphicsOutput.RTMCopyTexture, GraphicsOutput.RTPColor)
                self.snapshotquad.setShaderInput("count", self.count)
                self.motioncount = 0

        self.att_skydome.skybox.setShaderInput('time', task.time)
        self.setShaderInfo(task.time)

        self.ground.setTexOffset(self.groundts, 0, - task.time * 0.05)

        return task.cont

    def fire(self, mode):
#        return
        if mode > 0:
            h = (self.actor.neck.getR()) / 180 * math.pi
            p0 = self.particle.getParticlesNamed('particles-1')
            p0.setBirthRate(0.01)
            emitter = p0.getEmitter()
            v = 7
            emitter.setExplicitLaunchVector(Vec3(v * math.sin(h), -v * math.cos(h), -1.0000))
        else:
            p0 = self.particle.getParticlesNamed('particles-1')
            p0.setBirthRate(100000.0)

    def Reset(self, task=None):
        if self.manager != None:
            self.manager.cleanup()
            self.manager = None
            for quad in self.quadlist:
                quad.clearShader()
            self.quadlist = []
            self.shaderlist = []

    def addShader(self, shaderfile, shaderinputs=None):
        self.manager.cleanup()
        for quad in self.quadlist:
            quad.clearShader()
        self.quadlist = []
        self.dummytex = None
        self.snapshotbuffer = None

        if shaderfile == None:
            self.shaderlist = []
            self.motion = False
            return

        shader = loader.loadShader(shaderfile)
        if shader != None:
            src1 = None
            tex1 = Texture()
            finalquad = self.manager.renderSceneInto(colortex=tex1)
            for shaderinfo in self.shaderlist:
                tex2 = Texture()
                interquad = self.manager.renderQuadInto(colortex=tex2)
                interquad.setShaderInput("src", tex1)
                #interquad.setShaderInput("tex0", tex1)
                #interquad.setTexture(ts0, tex1)
                sha, info, motion = shaderinfo
                interquad.setShader(sha)
                self.quadlist.append(interquad)
                src1 = tex1
                tex1 = tex2
                self.setShaderInfo(None,interquad)
                if info != None:
                    self.setShaderSpecificInfo(interquad,info,src1)
                if motion:
                    self.snapshottex = tex1
                    self.snapshotbuffer = self.manager.buffers[-1]
                    self.snapshotquad = interquad

            if self.addSnapshot:
                #self.srctape = Texture()
                #self.manager.buffers[-1].addRenderTexture(self.dummytex2, GraphicsOutput.RTMCopyTexture, GraphicsOutput.RTPColor)
                self.snapshotbuffer = self.manager.buffers[-1]
                self.snapshottex = tex1
                self.snapshotquad = finalquad
            finalquad.setShader(shader)
            finalquad.setShaderInput("src", tex1)
            if shaderinputs != None:
                self.setShaderSpecificInfo(finalquad,shaderinputs,src1)
            #finalquad.setShaderInput("tex0", tex1)
            #finalquad.setTexture(ts0, tex1)
            self.shaderlist.append((shader,shaderinputs,self.addSnapshot))
            self.quadlist.append(finalquad)
            self.setShaderInfo(None,finalquad)
            self.addSnapshot = False

    def setShaderInfo(self,time,quad=None):
        winprops = WindowProperties().getDefault()
        xsize = winprops.getXSize()
        ysize = winprops.getYSize()
        if quad == None:
            for quad in self.quadlist:
                if time == None:
                    quad.setShaderInput('vTexelSize', 1.0/xsize, 1.0/ysize, 0, 0)
                    quad.setShaderInput('count', 0)
                    time = 0
                quad.setShaderInput('time', time,0,0,0)
        else:
                if time == None:
                    quad.setShaderInput('vTexelSize', 1.0/xsize, 1.0/ysize, 0, 0)
                    quad.setShaderInput('count', 0)
                    time = 0
                quad.setShaderInput('time', time,0,0,0)

    def setShaderSpecificInfo(self, quad, shaderinputs, src1):
        for input in shaderinputs:
            key,v = input
            if key == "src1":
                quad.setShaderInput(key, src1)
            else:
                quad.setShaderInput(key, v)

    def Demo01(self):
        """Clear All"""
        self.adding = [ None ]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "reset")

    def Demo03(self):
        """Red Only"""
        self.adding = ["shaders/colorfilter.sha", [ ("colorfilter", Vec4(1,0,0,1))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo04(self):
        """Green Only"""
        self.adding = ["shaders/colorfilter.sha", [ ("colorfilter", Vec4(0,1,0,1))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo05(self):
        """Blue Only"""
        self.adding = ["shaders/colorfilter.sha", [ ("colorfilter", Vec4(0,0,1,1))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo06(self):
        """Emboss"""
        self.adding = ["shaders/embossed.sha"]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo07(self):
        """Sharpen Edge"""
        self.adding = ["shaders/sharpenedge.sha"]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo08(self):
        """Invert"""
        self.adding = ["shaders/invert.sha"]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo09(self):
        """Posterize"""
        self.adding = ["shaders/posterize.sha", [ ("param1", Vec4(8,0.6,0,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo10(self):
        """Laplace"""
        self.adding = ["shaders/laplace.sha", [ ("param1", Vec4(1,0.0,0,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo11(self):
        """Tiling"""
        self.adding = ["shaders/tiling.sha",  [ ("param1", Vec4(100,0.75,0,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo12(self):
        """Radial Blur"""
        self.adding = ["shaders/radial_blur.sha",  [ ("param1", Vec4(1,2.2,0,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo13(self):
        """Blur"""
        self.adding = ["shaders/blur.sha"]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo14(self):
        """B & W"""
        self.adding = ["shaders/greyscale.sha"]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo15(self):
        """Random Dither"""
        self.adding = ["shaders/randomdither.sha", [ ("noise", self.noisetex), ("param1", Vec4(0.3,0,0,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo16(self):
        """Night Vision"""
        self.adding = ["shaders/nightvision.sha", [ ("noise", self.noisetex), ("lum", Vec4(0.3,0.59,0.11,0))]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo17(self):
        """Ascii"""
        alphatex = loader.loadTexture("textures/alpha.png")
        self.adding = ["shaders/ascii.sha", [
                ("alpha", alphatex),
                ("param1", Vec4(100,50,0.010,0.02)),
                ("param2", Vec4(0.005,0.01,0.734375,0)),
                #("param1", Vec4(200,100,0.005,0.01)),
                #("param2", Vec4(0.0025,0.005,0.734375,0)),
                #("param1", Vec4(150,75,0.00667,0.01333)),
                #("param2", Vec4(0.00336,0.00667,0.734375,0)),
                ("lum", Vec4(0.30,0.59,0.11,0.0)) ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo18(self):
        """Glass"""
        normalmaptex = loader.loadTexture("textures/WaterNormal1.tga")
        self.adding = ["shaders/glass.sha", [ ("normalmap", normalmaptex)]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo29(self):
        """Motion Detect 1"""
        self.addMotionDetect("shaders/motiondetect.sha", 1,0)

    def Demo30(self):
        """Motion Detect 2"""
        self.addMotionDetect("shaders/motiondetect.sha", 1,0.005)

#    def Demo21(self):
#        """Motion Detect 3"""
#        self.addMotionDetect("shaders/motiongrey.sha", 1,0.005)


    def addMotionDetect(self, shader, scale, threshold):
        if self.motion:
            return
        self.motion = True
        self.adding = [shader,
                [ ("prevsrc0", self.savetex[0]),
                  ("prevsrc1", self.savetex[1]),
                  ("param1", Vec4(scale,threshold,0,0))]]
        self.addSnapshot = True
        self.motioncount = 0
        self.motionframes = 1
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo32(self):
        """Motion Delay"""
        if self.motion:
            return
        self.motion = True
        self.adding = ["shaders/motiondelay.sha",
                [ ("prevsrc0", self.savetex[0]),
                  ("prevsrc1", self.savetex[1]),
                  ("param1", Vec4(0.5,0,0,0))
                  ]]
        self.addSnapshot = True
        self.motioncount = 0
        self.motionframes = 50
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo33(self):
        """Motion Highlight"""
        if self.motion:
            return
        self.motion = True
        self.adding = ["shaders/motiondelta.sha",
                [ ("prevsrc0", self.savetex[0]),
                  ("prevsrc1", self.savetex[1]),
                  ("param1", Vec4(1,0,0,0))
                  ]]
        self.addSnapshot = True
        self.motioncount = 0
        self.motionframes = 3
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo40(self):
        """Heat Effect"""
        #normalmaptex = loader.loadTexture("textures/heat.bmp")
        normalmaptex = loader.loadTexture("textures/WaterNormal1.tga")
        self.adding = ["shaders/heat.sha", [ ("normalmap", normalmaptex)]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")



    def Demo41(self):
        """Old TV"""
        randomtex = loader.loadTexture("textures/Random3D.dds")
        noisetex = loader.loadTexture("textures/NoiseVolume.dds")
        self.adding = ["shaders/oldtv.sha",
                [ ("rand", randomtex),
                  ("noise", noisetex),
                  ("param1", Vec4(2.7,0.5,0.93,0.5)),
                  ("param2", Vec4(0.4,0.26,6.0,0))
                  ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo42(self):
        """Old Movie"""
        tex1 = loader.loadTexture("textures/8x8PagesSplotches2.png")
        tex2 = loader.loadTexture("textures/Sepia1D.tga")
        tex3 = loader.loadTexture("textures/1D_Noise.png")
        self.adding = [
                "shaders/oldmovie.sha",
                [ ("SplotchesTx", tex1), ("SepiaTx", tex2), ("noise", tex3) ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo43(self):
        """Ascii 2"""
        alphatex = loader.loadTexture("textures/ASCII.dds")
        self.adding = ["shaders/ascii2.sha", [
                ("alpha", alphatex),
                ("param1", Vec4(100,50,0.010,0.02)),
                ("param2", Vec4(0.005,0.01,0.734375,0)),
                #("param1", Vec4(200,100,0.005,0.01)),
                #("param2", Vec4(0.0025,0.005,0.734375,0)),
                #("param1", Vec4(150,75,0.00667,0.01333)),
                #("param2", Vec4(0.00336,0.00667,0.734375,0)),
                ("lum", Vec4(0.30,0.59,0.11,0.0))
                 ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def addShaderLater(self, task):
        self.addShader(* self.adding)

    def addShaderLater2(self, task):
        self.addShader(* self.adding2)

    def Demo44(self):
        """Half Tone"""
        tex = self.createHalfToneTexture(64,64,64)
        #tex = loader.loadTexture("textures/NoiseVolume.dds")
        self.adding = ["shaders/halftone.sha", [
                ("pattern", tex),
                ("param1", Vec4(133.3,100,0.00750750,0.01)),
                ("param2", Vec4(0.00375375,0.005,0,0)),
                ("lum", Vec4(0.30,0.59,0.11,0.0))
                 ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def createHalfToneTexture(self,depth,width,height):
        tex = Texture()
        tex.setupTexture(Texture.TT3dTexture, width,height,depth, Texture.TUnsignedByte, Texture.FLuminance);
        p = tex.modifyRamImage()
        for z in range(depth):
            offset = width * height * z
            for y in range(height):
                for x in range(width):
                    fx = float(width)/2.0-x+0.5
                    fy = float(height)/2.0-y+0.5
                    fz = float(depth)/2.0-float(z)/3.0+0.5
                    distanceSquare = fx*fx+fy*fy+fz*fz
                    index = (offset + width * y + x)
                    if (distanceSquare < 1024.0):
                        p.setElement(index,255)
                    else:
                        p.setElement(index,0)

        return tex

    def Demo45(self):
        """Bloom 2"""
        self.adding = ["shaders/blur1.sha", [
                ("param1", Vec4(0.01,0,0.0,0.0))
                ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

        self.adding2 = ["shaders/bloom2.sha", [
                ("src1", None),
                ("param1", Vec4(1,0.7,0,0)),
                ]
        ]
        taskMgr.doMethodLater(0.6, self.addShaderLater2, "addshader2")

    def Demo46(self):
        """Tone Mapping"""
        self.adding = ["shaders/blur1.sha", [
                ("param1", Vec4(0.01,0,0.0,0.0))
                ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

        self.adding2 = ["shaders/tonemapping.sha", [
                ("src1", None),
                ("param1", Vec4(2,0.4,0.55,0)),
                ]
        ]
        taskMgr.doMethodLater(0.6, self.addShaderLater2, "addshader2")

##    def Demo47(self):
##        """Simple Thermal"""
##        self.adding = ["shaders/thermal.sha"]
##        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")


    def Demo48(self):
        """Heat Effect 2"""
        #normalmaptex = loader.loadTexture("textures/heat.bmp")
        noisetex = loader.loadTexture("textures/NoiseVolume.dds")
        self.adding = ["shaders/heat2.sha", [
            ("noisemap", noisetex),
            ("param1", 0.005),
            ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo49(self):
        """Hatching 1"""
        params = []
        for i in range(6):
            hatch = loader.loadTexture("demo_shaderadv/textures/Hatch%d.dds" % i)
            params.append(('hatch%d' % i, hatch))
        #params.append(("lum", Vec4(0.30,0.59,0.11,10.0)))
        params.append(("lum", Vec4(1,1,1,1.0)))
        self.adding = ["shaders/hatching.sha", params]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo50(self):
        """Hatching 2"""
        params = []
        for i in range(6):
            hatch = loader.loadTexture("demo_shaderadv/textures/Hatch%d.dds" % i)
            params.append(('hatch%d' % i, hatch))
        params.append(("lum", Vec4(0.8,0.8,0.8,5.0)))
        self.adding = ["shaders/hatching.sha", params]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo51(self):
        """Color Hatching"""
        params = []
        for i in range(6):
            hatch = loader.loadTexture("demo_shaderadv/textures/Hatch%d.dds" % i)
            params.append(('hatch%d' % i, hatch))
        params.append(("lum", Vec4(0.8,0.8,0.8,5.0)))
        self.adding = ["shaders/hatchingc.sha", params]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")

    def Demo52(self):
        """Multiple 3 x 3"""
        self.adding = ["shaders/multiple.sha", [
                ("param1", Vec4(3,3,0.0,0.0))
                ]]
        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")
##    def Demo52(self):
##        """Lens Flare"""
##        self.adding = ["shaders/lenflare2.sha", [
##                ("param1", Vec4(0.1,0,0.0,0.0))
##                ]]
##        taskMgr.doMethodLater(0.5, self.addShaderLater, "addshader")
