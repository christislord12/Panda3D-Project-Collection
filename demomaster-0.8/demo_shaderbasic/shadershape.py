
#from random import randint, random
import math, sys
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
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool
from direct.interval.LerpInterval import LerpFunc



####################################################################################################################
class ShaderShapeDemo(demobase.DemoBase):
    """
    Shaders - Change Shapes
    Testing of change shape shaders
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-100,-100,-100], [100,100,100], [-45,45, -17], [0,0,45],
                     Vec3(48,-48,21),
                     rate=0.2)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.Stop()

    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.timer, 'mytimer')

    def timer(self, task):
        render.setShaderInput('time', task.time)
        return task.cont

    def LoadLights(self):
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,0),
                attenuation=Vec3( 0., 0.0, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=render, fBulb=True)
        self.att_pointLight.setLight(render)
        self.att_pointLight.setLightOn(None, False)
        self.att_pointLight.setLight(render)


    def LoadModels(self):
        self.plane = None

        self.att_waveFreq = demobase.Att_FloatRange(False, "Water:Wave Freq", 0.0, 3, 0.5, 3)
        self.att_waveAmp = demobase.Att_FloatRange(False, "Water:Wave Amp", 0.0, 25.0, 1.8, 2)
        self.att_bumpSpeed = demobase.Att_Vecs(False,"Water:Bump Speed",2,(0.015,0.005), -0.1, 0.1)
        self.att_textureScale = demobase.Att_Vecs(False,"Water:Texture Scale",2,(25,25), 0, 40, 1)
        self.att_waveFreq.setNotifier(self.setPlaneShaderInput)
        self.att_waveAmp.setNotifier(self.setPlaneShaderInput)
        self.att_bumpSpeed.setNotifier(self.setPlaneShaderInput)
        self.att_textureScale.setNotifier(self.setPlaneShaderInput)

    def ClearScene(self):
        taskMgr.remove('mytimer')

        self.Reset()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Reset(self):
        if self.plane != None:
            self.plane.clearShader()
            self.plane.removeNode()
            self.plane = None
        # clear other animation effects
        if hasattr(self, "interval"):
            self.interval.pause()
        self.att_pointLight.setLightOn(None, False)
        ShaderPool.releaseAllShaders()

    def Demo01(self):
        """Clear all"""
        self.Reset()

    def Demo02(self):
        """Wave 1"""
        self.Reset()
        self.plane = geomutil.createPlane('myplane',50,50,50,50)
        self.plane.reparentTo(render)

        #myShader = demobase.loadShader("shaders/timevary2.sha")
        myShader = loader.loadShader("shaders/timevary2.sha")
        self.plane.setShader(myShader)
        self.setPlaneShaderInput(None)
        self.att_pointLight.setLightOn(None, True)
        self.att_pointLight.setPosition(None, Vec3(0,0,20))
        #self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        #self.interval.loop()
        self.plane.setShaderInput("light", self.att_pointLight.light)

    def Demo03(self):
        """Wave 2"""
        self.Reset()
        self.plane = geomutil.makeEggPlane(50,50,50,50)
        self.plane.reparentTo(render)

        #myShader = demobase.loadShader("shaders/timevary3.sha")
        myShader = loader.loadShader("shaders/timevary3.sha")
        self.plane.setShader(myShader)
        self.setPlaneShaderInput(None)
        self.att_pointLight.setLightOn(None, True)
        self.att_pointLight.setPosition(None, Vec3(0,0,20))
        #self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        #self.interval.loop()
        self.plane.setShaderInput("light", self.att_pointLight.light)
        wood = loader.loadTexture("models/wood.png")
        self.plane.setTexture(wood)


    def Demo04(self):
        """Wave 3 - Circular"""
        self.Reset()
        self.plane = geomutil.createPlane('myplane',50,50,50,50)
        #self.plane = geomutil.makeEggPlane(50,50,10,10)
        self.plane.reparentTo(render)

        myShader = loader.loadShader("shaders/timevary4.sha")
        self.plane.setShader(myShader)
        self.setPlaneShaderInput(None)
        self.att_pointLight.setLightOn(None, True)
        self.att_pointLight.setPosition(None, Vec3(0,0,20))
        #self.interval = LerpFunc(self.animate8, 10.0, 0.0, 360.0)
        #self.interval.loop()
        self.plane.setShaderInput("light", self.att_pointLight.light)



    def setPlaneShaderInput(self, object):
        self.plane.setShaderInput('waveInfo', Vec4( self.att_waveFreq.v, self.att_waveAmp.v, 0,0 ))
        bumpSpeed = self.att_bumpSpeed.getValue()
        textureScale = self.att_textureScale.getValue()
        self.plane.setShaderInput('param2', Vec4( bumpSpeed[0], bumpSpeed[1], textureScale[0], textureScale[1] ))

