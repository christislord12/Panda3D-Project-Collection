
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

import dofmanager
####################################################################################################################
class DOFShaderDemo(demobase.DemoBase):
    """
    Shaders - DOF
    Depth of Field Shader
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        #if (base.win.getGsg().getSupportsBasicShaders() == 0):
        #    addTitle("Normal Mapping: Video driver reports that shaders are not supported.")
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.att_dof = dofmanager.DOFManager(render)
        self.att_dof.setStandardControl()

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,-45], [59,59,45], [-45,45, -5], [0,0,0], Vec3(0,-14,2), rate=0.1)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.Stop()
        self.att_cameracontrol.ShowPosition(self.textnode)
        #self.att_cameracontrol.LockAt()

    	demobase.addInstructionList(-1,0.95,0.05,self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        taskMgr.add(self.timer, 'mytimer')

        #self.att_reflectivity = demobase.Att_FloatRange(False,"Reflectivity",0.0,1.0,1.0,2)

        #self.att_reflectivity.setNotifier(self.changeparams)

        #self.Demo05()

    def timer(self, task):
        #render.setShaderInput('time', task.time)
        self.monkey.setShaderInput("eyePositionW", Vec4(base.camera.getX(),base.camera.getY(),base.camera.getZ(),0.0));
        return task.cont

    #def changeparams(self, object):
        #self.monkey.setShaderInput("param1", self.att_reflectivity.v, self.att_reflectionblur.v, self.att_transmittance.v, 0)

    def LoadLights(self):
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,-30,20), attenuation=Vec3( 0.0, 0.02, 0.0 ), node=render, fBulb=True)
        self.att_pointLight.setLight(render)
##        self.att_pointLight.setLightOn(None, False)
##        self.att_pointLight.setLight(render)
        pass

    def LoadModels(self):
        skybox1 = self.LoadSkyBox('models/angmap26/skybox.egg')
        skybox2 = self.LoadSkyBox('models/skyboxtemplate/skybox.egg')
        skybox3 = self.LoadSkyBox('models/morningbox/morningbox.egg')
        self.skyboxes = [skybox1, skybox2, skybox3]
        self.skyboxselection = 0

        base.cam.node().getLens( ).setNear( 10 )
        base.cam.node().getLens( ).setFar( 4000 )

        self.box = loader.loadModel("models/cube")
        self.box.setColor(Vec4(0.7,0.7,0.7,1))
        self.box.reparentTo(render)
        self.box.setPos(-4,15,0)
        self.box.setScale(5)
        self.monkey = loader.loadModel("models/monkey")
        self.monkey.reparentTo(render)
        self.monkey2 = loader.loadModel("models/monkey")
        self.monkey2.reparentTo(render)
        self.monkey2.setH(45)
        self.monkey2.setPos(4,4,0)
        self.monkey3 = loader.loadModel("models/monkey")
        self.monkey3.reparentTo(render)
        self.monkey3.setH(-45)
        self.monkey3.setPos(-4,-4,0)
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
        self.att_dof.Destroy()
        taskMgr.remove('mytimer')

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

#    def Reset(self):
#        self.monkey.clearShader()
#        ShaderPool.releaseAllShaders()

#    def LoadShader(self, file):
#        myShader = loader.loadShader(file)
#        self.monkey.setShader(myShader)
#        return myShader

    def Demo02(self):
        """Toggle skybox"""
        self.skyboxselection = ( self.skyboxselection + 1 ) % len(self.skyboxes)
        self.setSkyBox()

    def setCubeMap(self, cubemapfile):
        tex = loader.loadCubeMap(cubemapfile)
        tex.setMinfilter( Texture.FTLinearMipmapLinear ) # for reflection blur to work
        #self.monkey.setShaderInput('texcube',tex)


