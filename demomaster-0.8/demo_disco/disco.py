
from random import randint, random
import math, sys, colorsys, threading

#import direct.directbase.DirectStart
from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText
#from direct.showbase.DirectObject import DirectObject
#from pandac.PandaModules import *
from pandac.PandaModules import Material,LightAttrib

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import AmbientLight,DirectionalLight, PerspectiveLens, PointLight,Spotlight,LightRampAttrib
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from direct.filter.CommonFilters import CommonFilters

import demobase

####################################################################################################################
class DiscoDemo(demobase.DemoBase):
    """
    Misc - Disco Light
    Just the disco light demo from the tutorial.
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.LoadModels()
        #self.LoadFilter()
        #render.setAttrib(LightRampAttrib.makeHdr0())
        #render.setAttrib(LightRampAttrib.makeHdr1())
        #node.setAttrib(LightRampAttrib.makeHdr2())

    def LoadModels(self):
        self.SetCameraPos(Vec3(0,0,5), Vec3(0,0,5))
##        self.box = loader.loadModel("models/nbox")
##        self.box.reparentTo(render)
##        self.box.setPos(0, 30, 0)
##        self.box.setScale(3)

        self.room = loader.loadModel("models/disco_hall")
        self.room.reparentTo(render)
        self.room.setPosHpr(0, 50, -4, 90, 0, 0)

        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.1, .1, .1, 1 ))
        self.att_ambinentLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False,"Light:Directional Light",Vec4( .35, .35, .35, 1 ) ,Vec3( 1, 1, -2 ) )
        self.att_directionalLight.setLight(render)


        self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( .45, .45, .45, 1 ), 16, 60.0, Vec3(0,0,0), Point3(0,0,0), attenuation=Vec3( 1, 0.0, 0.0 ), node=camera)
        self.att_spotLight.setLight(render)

        self.pointLightHelper = render.attachNewNode( "pointLightHelper" )
        self.pointLightHelper.setPos(0, 50, 11)

        self.att_pointLightRed = demobase.Att_pointLightNode(False, "Light:Red Point Light",  \
                Vec4( 0.35, 0, 0, 1 ), Vec3(-6.5,-3.75,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=self.pointLightHelper, fBulb=True)
        self.att_pointLightRed.att_bulb.setBulbSize(None, 0.5)
        self.att_pointLightRed.att_bulb.setBulbColor(None, Vec4(1,0.125,0.125,1))
        self.att_pointLightRed.att_bulb.setFireColor(None, Vec4(1,0.45,0.45,1))
        self.att_pointLightRed.setLight(render)

        self.att_pointLightGreen = demobase.Att_pointLightNode(False, "Light:Green Point Light",  \
                Vec4( 0, 0.35, 0, 1 ), Vec3(0,7.5,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=self.pointLightHelper, fBulb=True)
        self.att_pointLightGreen.att_bulb.setBulbSize(None, 0.5)
        self.att_pointLightGreen.att_bulb.setBulbColor(None, Vec4(0.125,1,0.125,1))
        self.att_pointLightGreen.att_bulb.setFireColor(None, Vec4(0.45,1,0.45,1))
        self.att_pointLightGreen.setLight(render)

        self.att_pointLightBlue = demobase.Att_pointLightNode(False, "Light:Blue Point Light",  \
                Vec4( 0, 0, 0.35, 1 ), Vec3(6.5,-3.75,0), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=self.pointLightHelper, fBulb=True)
        self.att_pointLightBlue.att_bulb.setBulbSize(None, 0.5)
        #self.att_pointLightBlue.att_bulb.setBulbColor(None, Vec4(0.45,0.45,1,1))
        #self.att_pointLightBlue.att_bulb.setFireColor(None, Vec4(0.75,0.75,1,1))
        self.att_pointLightBlue.setLight(render)


        self.pointLightsSpin = self.pointLightHelper.hprInterval(6, Vec3(360, 0, 0))
        self.pointLightsSpin.loop()

        #self.cameracontrol = demobase.CameraController1(self.parent, (-59,-59,5), (59,59,45), (-45,45), Vec3(55,-55,20), rate=0.2)
        #self.parent.Accept("escape", self.stopcameracontrol)

    def ClearScene(self):
        #self.cameracontrol.Destroy()
        #taskMgr.remove("myDemo2")
        base.camera.detachNode()
        #render.clearShaderInput('light')
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    #def stopcameracontrol(self):
    #    self.cameracontrol.Stop()

    def LoadFilter(self):
        # Check video card capabilities.
        if (base.win.getGsg().getSupportsBasicShaders() == 0):
            self.addTitle("Glow Filter: Video driver reports that shaders are not supported.")
            return
        # Use class 'CommonFilters' to enable a bloom filter.
        # The brightness of a pixel is measured using a weighted average
        # of R,G,B,A.  We put all the weight on Alpha, meaning that for
        # us, the framebuffer's alpha channel alpha controls bloom.
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom(blend=(1,0,0,1), desat=-0.5, intensity=3.0, size=1)
        if (filterok == False):
            self.addTitle("Toon Shader: Video card not powerful enough to do image postprocessing")
            return
