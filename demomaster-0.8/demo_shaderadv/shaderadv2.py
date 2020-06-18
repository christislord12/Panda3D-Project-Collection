
#from random import randint, random
import math, sys, thread
import demobase, camerabase, geomutil

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
#from pandac.PandaModules import Material,LightAttrib

from pandac.PandaModules import NodePath, WindowProperties
#from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.actor.Actor import Actor


####################################################################################################################
class ShaderAdvance2Demo(demobase.DemoBase):
    """
    Shaders - Advance Demo 2
    Dynamic Mirror
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        #if (base.win.getGsg().getSupportsBasicShaders() == 0):
        #    addTitle("Normal Mapping: Video driver reports that shaders are not supported.")
        base.setBackgroundColor(0.0, 0.0, 0.0)
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-100,-100,-45], [100,100,45], [-45,45, 0], [0,0,-5], Vec3(0,-83,0), rate=0.1)
        self.att_cameracontrol.DefaultController()
        #self.att_cameracontrol.Stop()
        self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.LockAt((0,0,0))

    	demobase.addInstructionList(-1,0.95,0.05,self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        taskMgr.add(self.timer, 'mytimer')

        self.att_waveFreq = demobase.Att_FloatRange(False, "Water:Wave Freq", 0.0, 3, 0.283, 3)
        self.att_waveAmp = demobase.Att_FloatRange(False, "Water:Wave Amp", 0.0, 25.0, 1.8, 2)
        self.att_reflectivity = demobase.Att_FloatRange(False,"Reflectivity",0.0,1.0,1.0,2)
        self.att_reflectionblur = demobase.Att_FloatRange(False,"Reflection Blur",0.0,10.0,2.0,2)
        self.att_transmittance = demobase.Att_FloatRange(False,"Transmittance",0.0,1.0,1.0,2)
        self.att_etaRatio = demobase.Att_Vecs(False,"etaRatio",3,(1.5,1.4,1.3), 1.0,3.0, 3)
        self.att_fresnelPower = demobase.Att_FloatRange(False, "Fresnel Power", 0.0, 10.0, 5.0)
        self.att_fresnelScale = demobase.Att_FloatRange(False,"Fresnel Scale",0.0,5.0,1.0,1)
        self.att_fresnelBias = demobase.Att_FloatRange(False, "Fresnel Bias", 0.0, 1.0, 0.328)

        self.att_waveFreq.setNotifier(self.changeparams)
        self.att_waveAmp.setNotifier(self.changeparams)
        self.att_reflectivity.setNotifier(self.changeparams)
        self.att_reflectionblur.setNotifier(self.changeparams)
        self.att_transmittance.setNotifier(self.changeparams)
        self.att_etaRatio.setNotifier(self.changeparams)
        self.att_fresnelPower.setNotifier(self.changeparams)
        self.att_fresnelScale.setNotifier(self.changeparams)
        self.att_fresnelBias.setNotifier(self.changeparams)

        self.Demo03()

    def timer(self, task):
        #render.setShaderInput('time', task.time)
        self.mirror.setShaderInput("eyePositionW", Vec4(base.camera.getX(),base.camera.getY(),base.camera.getZ(),0.0));
        self.mirror.setShaderInput("time", task.time)
        return task.cont

    def changeparams(self, object):
        self.mirror.setShaderInput('waveInfo', Vec4( self.att_waveFreq.v, self.att_waveAmp.v, 0,0 ))
        self.mirror.setShaderInput("param1", self.att_reflectivity.v, self.att_reflectionblur.v, self.att_transmittance.v, 0)
        r = self.att_etaRatio.getValue()
        self.mirror.setShaderInput("etaRatio", r[0], r[1], r[2],0 )
        self.mirror.setShaderInput("fresnel", self.att_fresnelPower.v, self.att_fresnelScale.v, self.att_fresnelBias.v, 0)

    def LoadLights(self):
##        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
##                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
##        self.att_pointLight.setLight(render)
##        self.att_pointLight.setLightOn(None, False)
##        self.att_pointLight.setLight(render)
        pass

    def LoadModels(self):
        skybox1 = self.LoadSkyBox('models/angmap26/skybox.egg')
        skybox2 = self.LoadSkyBox('models/skyboxtemplate/skybox.egg')
        skybox3 = self.LoadSkyBox('models/morningbox/morningbox.egg')
        self.skyboxes = [skybox1, skybox2, skybox3]
        self.skyboxselection = 0

        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 4000 )

        self.mirror = geomutil.createPlane("mirror", 30,30,40,40)
        self.mirror.setHpr(0,90,0)
        self.mirror.reparentTo(render)

        self.actor= Actor('panda.egg', {'walk' : 'panda-walk.egg'})
        self.actor.setScale(2)
        self.actor.setHpr(180,0,0)
        self.actor.setPos(Vec3(10,-60,-10))
        self.actor.reparentTo(render)
        #self.actor.loop("walk")
        #self.actor.setPos(Vec3(0,-10,0))

        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light",
            Vec4(1, 1, 1, 1 ),  Vec3( 0, -1, 0))
        self.att_directionalLight.setLight(self.actor)
        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.5, .5, .5, 1 ))
        self.att_ambinentLight.setLight(self.actor)

        # I have to save the cube map one here, otherwise it may crash when called later....
        # what is the reason ?
        #base.saveCubeMap('tmp/cube_map#.png', size= 256)
        self.setSkyBox()

    def setSkyBox(self):
        for skybox in self.skyboxes:
            skybox.hide()
        self.skyboxes[self.skyboxselection].show()
        cubemapfile = 'tmp/cube%s_#.jpg' % self.skyboxselection
        #cubemapfile = 'tmp/cube_map#.png'
        pos = base.camera.getPos()
        hpr  = base.camera.getHpr()
        #self.actor.show()
        base.camera.setPosHpr(0,0,0,0,0,0)
        base.saveCubeMap(cubemapfile, size = 512)
        base.camera.setPos(pos)
        base.camera.setHpr(hpr)
        self.setCubeMap(cubemapfile)
        #self.actor.hide()

    def ClearScene(self):
        taskMgr.remove('mytimer')
        self.Reset()

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Reset(self):
        self.mirror.clearShader()
        ShaderPool.releaseAllShaders()

    def LoadShader(self, file):
        myShader = loader.loadShader(file)
        self.mirror.setShader(myShader)
        return myShader

    def Demo01(self):
        """Clear all shaders"""
        self.Reset()

    def Demo02(self):
        """Toggle skybox"""
        self.skyboxselection = ( self.skyboxselection + 1 ) % len(self.skyboxes)
        self.setSkyBox()

    def Demo03(self):
        """Reflection Shader"""
        self.Reset()
        self.changeparams(None)
        self.LoadShader('shaders/mirror.sha')

    def Demo04(self):
        """Reflection Shader 2"""
        self.Reset()
        self.changeparams(None)
        self.LoadShader('shaders/fmirror.sha')


    def setCubeMap(self, cubemapfile):
        tex = loader.loadCubeMap(cubemapfile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear ) # for reflection blur to work
        #tex.setMagfilter( Texture.FTLinearMipmapLinear )
        self.mirror.setShaderInput('texcube',tex)
        #ts = TextureStage('environ')
        #self.mirror.setTexGen(ts, TexGenAttrib.MEyeCubeMap)
        #self.mirror.setTexture(ts, tex)

