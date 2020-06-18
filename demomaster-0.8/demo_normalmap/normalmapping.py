
from random import randint, random
import math, sys, colorsys, threading
import demobase, camerabase

from pandac.PandaModules import Filename
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
#from pandac.PandaModules import Material,LightAttrib

from pandac.PandaModules import NodePath, WindowProperties
#from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

### ode
##from pandac.PandaModules import OdeWorld, OdeSimpleSpace, OdeJointGroup
##from pandac.PandaModules import OdeBody, OdeMass, OdeSphereGeom, OdePlaneGeom, OdeTriMeshGeom, OdeTriMeshData
##from pandac.PandaModules import BitMask32, Quat, Mat4
##
### particle
##from direct.particles.ParticleEffect import ParticleEffect
##
##import odebase

####################################################################################################################
class NormalMappingDemo(demobase.DemoBase):
    """
    Misc - Normal Mapping Demo
    Just the normal mapping demo from the tutorial.
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        #if (base.win.getGsg().getSupportsBasicShaders() == 0):
        #    addTitle("Normal Mapping: Video driver reports that shaders are not supported.")

        #self.SetCameraPos(Vec3(0,-60,15), Vec3(0,0,15))
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,5], [59,59,45], [-45,45, 0], [0,0,45], Vec3(55,-55,20), rate=0.2)
        self.att_cameracontrol.DefaultController()
    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)


    def LoadModels(self):
        self.room = loader.loadModel("models/abstractroom")
        self.room.reparentTo(render)

        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambientLight.setLight(render)
        if True:
            self.lightpivot = render.attachNewNode("lightpivot")
            self.lightpivot.setPos(0,0,25)
            self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()
            self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(45,0,0), attenuation=Vec3( 0.7, 0.05, 0.0 ), node=self.lightpivot, fBulb=True)
            self.att_pointLight.setLight(render)
            # auto shader does not require to set the shader input
            # render.setShaderInput("light", self.att_pointLight.light)


    def ClearScene(self):
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        #taskMgr.remove("myDemo2")
        base.camera.detachNode()
        #render.clearShaderInput('light')
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    #def stopcameracontrol(self):
    #    self.att_cameracontrol.Stop()

#    def Demo1(self):
#        "render.explore()"
#        render.explore()

    #def Demo1(self):
        #"""Retrieving auto generated shader"""
        #render.ls()
        #demobase.DemoBase.ShowShaderSource(self, self.room.node().getChild(0))
        #demobase.DemoBase.ShowShaderSource(self, self.room.node().getChild(0).getChild(0))

