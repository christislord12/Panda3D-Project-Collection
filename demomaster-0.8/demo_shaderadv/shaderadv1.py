
#from random import randint, random
import math, sys, thread
import demobase, camerabase

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


####################################################################################################################
class ShaderAdvance1Demo(demobase.DemoBase):
    """
    Shaders - Advance Demo 1
    Some shader examples Cg Tutorial
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
                     [-59,-59,-45], [59,59,45], [-45,45, -5], [0,0,-45], Vec3(0,-0,0), rate=0.1)
        self.att_cameracontrol.DefaultController()
        #self.att_cameracontrol.Stop()
        self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.LockAt()

    	demobase.addInstructionList(-1,0.95,0.05,self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        taskMgr.add(self.timer, 'mytimer')

        self.att_reflectivity = demobase.Att_FloatRange(False,"Reflectivity",0.0,1.0,1.0,2)
        self.att_reflectionblur = demobase.Att_FloatRange(False,"Reflection Blur",0.0,10.0,2.0,2)
        self.att_transmittance = demobase.Att_FloatRange(False,"Transmittance",0.0,1.0,1.0,2)
        self.att_etaRatio = demobase.Att_Vecs(False,"etaRatio",3,(1.5,1.4,1.3), 1.0,3.0, 3)
        self.att_fresnelPower = demobase.Att_FloatRange(False, "Fresnel Power", 0.0, 10.0, 5.0)
        self.att_fresnelScale = demobase.Att_FloatRange(False,"Fresnel Scale",0.0,5.0,1.0,1)
        self.att_fresnelBias = demobase.Att_FloatRange(False, "Fresnel Bias", 0.0, 1.0, 0.328)

        self.att_velvet = demobase.Att_FloatRange(False,"Velvet Exp",0.0,1.0,0.225,3)
        self.att_mariocolor = demobase.Att_FloatRange(False,"Mariocolor",0.1,10.0,3,2)
        self.att_marioshade = demobase.Att_FloatRange(False,"Marioshade",0.1,10.0,3,2)

        self.att_reflectivity.setNotifier(self.changeparams)
        self.att_reflectionblur.setNotifier(self.changeparams)
        self.att_transmittance.setNotifier(self.changeparams)
        self.att_etaRatio.setNotifier(self.changeparams)
        self.att_fresnelPower.setNotifier(self.changeparams)
        self.att_fresnelScale.setNotifier(self.changeparams)
        self.att_fresnelBias.setNotifier(self.changeparams)

        self.att_velvet.setNotifier(self.changeparams)
        self.att_mariocolor.setNotifier(self.changeparams)
        self.att_marioshade.setNotifier(self.changeparams)

        self.Demo05()

    def timer(self, task):
        #render.setShaderInput('time', task.time)
        self.monkey.setShaderInput("eyePositionW", Vec4(base.camera.getX(),base.camera.getY(),base.camera.getZ(),0.0));
        return task.cont

    def changeparams(self, object):
        self.monkey.setShaderInput("param1", self.att_reflectivity.v, self.att_reflectionblur.v, self.att_transmittance.v, 0)
        r = self.att_etaRatio.getValue()
        self.monkey.setShaderInput("etaRatio", r[0], r[1], r[2],0 )
        self.monkey.setShaderInput("fresnel", self.att_fresnelPower.v, self.att_fresnelScale.v, self.att_fresnelBias.v, 0)

        # velvet shader input
        self.monkey.setShaderInput("velvet", self.att_velvet.v )
        self.monkey.setShaderInput('light',self.att_pointLight.light)
        r = self.att_pointLight.light.node().getAttenuation()
        self.monkey.setShaderInput("atten", r[0], r[1], r[2],0 )

        # crystal shader input
        #self.monkey.setShaderInput("param1", self.att_reflectivity.v, self.att_reflectionblur.v, self.att_transmittance.v, 0)
        self.monkey.setShaderInput('cam',camera)

        self.monkey.setShaderInput('param2',Vec4(self.att_mariocolor.v,self.att_marioshade.v,0,0))

    def LoadLights(self):
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,-11,20), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setNotifier(self.changeparams)

    def LoadModels(self):
        skybox1 = self.LoadSkyBox('models/angmap26/skybox.egg')
        skybox2 = self.LoadSkyBox('models/skyboxtemplate/skybox.egg')
        skybox3 = self.LoadSkyBox('models/morningbox/morningbox.egg')
        self.skyboxes = [skybox1, skybox2, skybox3]
        self.skyboxselection = 0

        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 4000 )

        self.monkey = loader.loadModel("models/monkey")
        nops = loader.loadTexture("models/nops.png")
        nops.setWrapU(Texture.WMRepeat)
        nops.setWrapV(Texture.WMRepeat)
        self.monkey.setTexture(nops, 1)

        #self.monkey = loader.loadModel("models/elephant")
        #self.monkey.setScale(0.5)
        self.monkey.reparentTo(render)
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
        base.saveCubeMap(cubemapfile, size = 256)
        self.setCubeMap(cubemapfile)

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
        self.monkey.clearShader()
        ShaderPool.releaseAllShaders()

    def LoadShader(self, file):
        myShader = loader.loadShader(file)
        self.monkey.setShader(myShader)
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
        #base.saveCubeMap('tmp/cube_map#.png', size= 256)
        self.changeparams(None)
        self.LoadShader('shaders/reflection.sha')

    def Demo04(self):
        """Refraction Shader"""
        self.Reset()
        #base.saveCubeMap('tmp/cube_map#.png', size= 256)
        self.changeparams(None)
        self.LoadShader('shaders/refraction.sha')

    def Demo05(self):
        """Fresnel Shader"""
        self.Reset()
        #base.saveCubeMap('tmp/cube_map#.png', size= 256)
        self.changeparams(None)
        self.LoadShader('shaders/fresnel.sha')

    def Demo06(self):
        """Velvet Shader - test only"""
        self.Reset()
        #base.saveCubeMap('tmp/cube_map#.png', size= 256)
        self.changeparams(None)
        self.LoadShader('shaders/velvet2.sha')

    def Demo07(self):
        """Crystal Shader - mavasher"""
        self.Reset()
        self.changeparams(None)
        self.LoadShader('shaders/crystal.sha')

    def Demo08(self):
        """Mario Shader - mavasher"""
        self.Reset()
        self.changeparams(None)
        self.LoadShader('shaders/mario.sha')

    def setCubeMap(self, cubemapfile):
        tex = loader.loadCubeMap(cubemapfile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear ) # for reflection blur to work
        self.monkey.setShaderInput('texcube',tex)
        #ts = TextureStage('environ')
        #self.monkey.setTexGen(ts, TexGenAttrib.MEyeCubeMap)
        #self.monkey.setTexture(ts, tex)

