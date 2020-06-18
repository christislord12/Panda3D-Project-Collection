
#from random import randint, random
import math, sys
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
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool
from direct.interval.LerpInterval import LerpFunc



####################################################################################################################
class ShaderBasicDemo(demobase.DemoBase):
    """
    Shaders - Basic Demo
    Some shader examples from manual and http://panda3d.org/phpbb2/viewtopic.php?t=4893
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
                     [-59,-59,5], [59,59,45], [-45,45, -17], [0,0,45], Vec3(8,-8,3), rate=0.2)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.Stop()

    	demobase.addInstructionList(-1,0.95,0.05,self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.timer, 'mytimer')

    def timer(self, task):
        render.setShaderInput('time', task.time)
        return task.cont

    def LoadLights(self):
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setLightOn(None, False)
        self.att_pointLight.setLight(render)
        self.att_pointLight0 = demobase.Att_pointLightNode(False, "Light:Point Light 0",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight0.setLight(render)
        self.att_pointLight0.setLightOn(None, False)
        self.att_pointLight0.setLight(render)
        self.att_pointLight1 = demobase.Att_pointLightNode(False, "Light:Point Light 1",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight1.setLight(render)
        self.att_pointLight1.setLightOn(None, False)
        self.att_pointLight1.setLight(render)
        self.att_pointLight2 = demobase.Att_pointLightNode(False, "Light:Point Light 2",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight2.setLight(render)
        self.att_pointLight2.setLightOn(None, False)
        self.att_pointLight2.setLight(render)


    def LoadModels(self):
        modelCube = loader.loadModel("models/mycube")
        self.root = render.attachNewNode("Root")
        cubes = []
        for x in [-3.0, 0.0, 3.0]:
            cube = modelCube.copyTo(self.root)
            cube.setPos(x, 0.0, 0.0)
            cubes += [ cube ]

    def ClearScene(self):
        taskMgr.remove('mytimer')

        if hasattr(self, "interval"):
            self.interval.pause()
        self.root.clearShader()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Reset(self):
        self.root.clearShader()
        self.root.removeNode()
        self.LoadModels()

        # clear other animation effects
        if hasattr(self, "interval"):
            self.interval.pause()
        self.att_pointLight.setLightOn(None, False)
        self.att_pointLight0.setLightOn(None, False)
        self.att_pointLight1.setLightOn(None, False)
        self.att_pointLight2.setLightOn(None, False)
        ShaderPool.releaseAllShaders()

    def LoadShader(self, file):
        myShader = loader.loadShader(file)
        self.root.setShader(myShader)
        return myShader

    def Demo01(self):
        """Clear all shaders"""
        self.Reset()

    def Demo02(self):
        """Red Green Swap"""
        self.Reset()
        self.LoadShader('shaders/redgreenswap.sha')

    def Demo03(self):
        """Disable Red"""
        self.Reset()
        self.LoadShader('shaders/3.sha')

    def Demo04(self):
        """Disable Red"""
        self.Reset()
        self.LoadShader('shaders/3.sha')

    def Demo05(self):
        """setShaderInput Test"""
        self.Reset()
        self.LoadShader('shaders/5.sha')
        self.root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)

        self.interval = LerpFunc(self.animate4, 5.0, 0.0, 360.0)
        self.interval.start()

    def animate4(self,t):
        c = abs(math.cos(math.radians(t)))
        self.root.setShaderInput("panda3drocks", c, c, c, 1.0)


    def Load2Textures(self, shaderFile):
        self.Reset()
        self.LoadShader(shaderFile)

        textureArrow = loader.loadTexture("models/arrow.png")
        textureArrow.setWrapU(Texture.WMClamp)
        textureArrow.setWrapV(Texture.WMClamp)

        """
        DIRTY
        Try to increase the setSort parameter and look at the results. Somehow we can
        influence the shader, nevertheless the cube is only textured with one texture.
        """
        stageArrow = TextureStage("Arrow")
        stageArrow.setSort(1)

        textureCircle = loader.loadTexture("models/circle.png")
        textureCircle.setWrapU(Texture.WMClamp)
        textureCircle.setWrapV(Texture.WMClamp)

        stageCircle = TextureStage("Circle")
        stageCircle.setSort(2)

        self.root.setTexture(stageArrow, textureArrow)
        self.root.setTexture(stageCircle, textureCircle)

    def Demo06(self):
        """One Texture, up side down"""
        self.Load2Textures("shaders/6.sha")

    def Demo07(self):
        """2 Textures"""
        self.Load2Textures("shaders/7.sha")

    def animate8(self, t):
        radius = 4.3
        angle = math.radians(t)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        z = math.sin(angle) * radius
        #light.setPos(x, y, z)
        self.att_pointLight.setPosition(None, Vec3(x,y,z))

    def Demo08(self):
        """Point Light, no shader"""
        self.Reset()
        #self.root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)
        self.att_pointLight.setLightOn(None, True)

        self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        self.interval.loop()

    def Demo09(self):
        """Point Light, with shader"""
        self.Reset()
        #self.root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)
        self.att_pointLight.setLightOn(None, True)

        self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        self.interval.loop()

        shader = self.LoadShader("shaders/9.sha")
        self.root.setShaderInput("light", self.att_pointLight.light)

    def Demo10(self):
        """Point Light, with fshader"""
        self.Reset()
        #self.root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)
        self.att_pointLight.setLightOn(None, True)

        self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        self.interval.loop()

        shader = self.LoadShader("shaders/10.sha")
        self.root.setShaderInput("light", self.att_pointLight.light)


    def animate11(self, t):
        radius = 4.3
        angle = math.radians(t)
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        z = math.sin(angle) * radius
        #light.setPos(x, y, z)
        self.att_pointLight0.setPosition(None, Vec3(x,y,z))
        self.att_pointLight1.setPosition(None, Vec3(y,x,0))
        self.att_pointLight2.setPosition(None, Vec3(z,0,x))

    def Demo11(self):
        """3 Point Light, with fshader"""
        self.Reset()
        #self.root.setShaderInput("panda3drocks", 1.0, 0.0, 1.0, 1.0)
        self.att_pointLight0.setLightOn(None, True)
        self.att_pointLight1.setLightOn(None, True)
        self.att_pointLight2.setLightOn(None, True)

        self.interval = LerpFunc(self.animate11, 10.0, 0.0, 360.0)
        self.interval.loop()

        shader = self.LoadShader("shaders/11.sha")
        #self.root.setShaderInput("light", self.att_pointLight.light)
        self.root.setShaderInput("light0", self.att_pointLight0.light)
        self.root.setShaderInput("light1", self.att_pointLight1.light)
        self.root.setShaderInput("light2", self.att_pointLight2.light)

    def Demo12(self):
        """Shape Changing with time"""
        self.Reset()
        shader = self.LoadShader("shaders/timevary1.sha")

    #def Demo13(self):
    #    """Retrieving auto generated shader"""
    #    demobase.DemoBase.ShowShaderSource(self, render)

