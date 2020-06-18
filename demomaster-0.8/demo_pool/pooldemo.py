
from random import randint, random
import math, sys, colorsys, threading
import demobase, camerabase, waterplane1

from pandac.PandaModules import Filename
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
#from pandac.PandaModules import Material,LightAttrib

from pandac.PandaModules import NodePath, WindowProperties
#from direct.gui.OnscreenImage import OnscreenImage
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib

from direct.filter.FilterManager import FilterManager

####################################################################################################################
class PoolDemo(demobase.DemoBase):
    """
    Misc - Pool Demo
    Testing scene
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        #if (base.win.getGsg().getSupportsBasicShaders() == 0):
        #    addTitle("Normal Mapping: Video driver reports that shaders are not supported.")

        #self.SetCameraPos(Vec3(0,-60,15), Vec3(0,0,15))
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.setBloomShader()

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,3], [59,59,40], [-45,45, 0], [0,0,84], Vec3(55,0,10), rate=0.2)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.setFov(None, 100)
    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        taskMgr.add(self.cameraUpdated, "camupdate")

        self.att_cameracontrol.setNotifier(self.camchanged)
        self.camchanged(None)

    def camchanged(self, object):
        self.att_water.setFov(self.att_cameracontrol.att_fov.v)

    def LoadModels(self):
        self.att_water = waterplane1.WaterNode(-40,-30,40,30, 0)
        self.att_water.setStandardControl()
        self.att_water.att_scale.update(5)
        self.att_water.att_refractionfactor.update(0.3)
        self.att_water.att_vx.update(0.03)
        self.att_water.att_vy.update(0.03)

        self.room = loader.loadModel("models/pool/pool2-3")
        self.room.setScale(4)
        self.room.reparentTo(render)

        self.male = loader.loadModel("models/male/male.egg")
        self.male.reparentTo(render)
        self.male.setScale(1.4)
        self.male.setZ(-7)
        self.male.setH(90)

        self.female = loader.loadModel("models/female/female.egg")
        self.female.reparentTo(render)
        self.female.setScale(1.4)
        self.female.setPos(0,5,-7)
        self.female.setH(90)

        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.7, .7, .7, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( 1, 1, 1, 1 ), 88, 28.0, Vec3(0,0,100), Point3(0,0,0), attenuation=Vec3( 0.04, 0.0, 0.0 ))
        self.att_spotLight.setLight(render)

        if False:
            self.lightpivot = render.attachNewNode("lightpivot")
            self.lightpivot.setPos(0,0,25)
            self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()
            self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(45,0,0), attenuation=Vec3( 0.7, 0.05, 0.0 ), node=self.lightpivot, fBulb=True)
            self.att_pointLight.setLight(render)
            # auto shader does not require to set the shader input
            # render.setShaderInput("light", self.att_pointLight.light)


    def ClearScene(self):
        self.att_water.Destroy()
        taskMgr.remove("camupdate")

        self.manager.cleanup()
        self.manager = None
        for quad in self.quadlist:
            quad.clearShader()
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


    def setBloomShader(self):
        self.manager = FilterManager(base.win, base.cam)
        self.quadlist = []
        src1 = None
        tex1 = Texture()
        finalquad = self.manager.renderSceneInto(colortex=tex1)

        tex2 = Texture()
        interquad = self.manager.renderQuadInto(colortex=tex2)
        interquad.setShaderInput("src", tex1)

        sha = loader.loadShader("shaders/blur1.sha")
        interquad.setShader(sha)
        interquad.setShaderInput("src", tex1)
        #interquad.setShaderInput("param1", 0.02)

        self.quadlist.append(interquad)
        src1 = tex1
        tex1 = tex2

        sha = loader.loadShader("shaders/bloom2.sha")
        finalquad.setShader(sha)
        finalquad.setShaderInput("src", tex1)
        finalquad.setShaderInput("src1", src1)
        #finalquad.setShaderInput("param1", Vec4(1.8,0.7,0,0))
        self.quadlist.append(finalquad)

        self.att_blurness = demobase.Att_FloatRange(False,"Blurness",0,0.04,0.01,3)
        self.att_factor = demobase.Att_Vecs(False,"Factors",2,[1.6,0.7], 0, 3)
        self.att_blurness.setNotifier(self.setShaderParam)
        self.att_factor.setNotifier(self.setShaderParam)

        self.setShaderParam(None)

    def setShaderParam(self, object):
        self.quadlist[0].setShaderInput("param1", self.att_blurness.v)
        l = self.att_factor.getListValue()
        self.quadlist[1].setShaderInput("param1", Vec4(l[0], l[1], 0, 0))


    def cameraUpdated(self, task):
        self.att_water.waterNP.setShaderInput('time', task.time)
        pos = base.camera.getPos()
        mc = base.camera.getMat( )
        self.att_water.changeCameraPos(pos, mc)
        return task.cont

