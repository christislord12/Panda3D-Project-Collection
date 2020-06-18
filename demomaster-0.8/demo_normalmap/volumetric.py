
from random import randint, random
import math, sys, colorsys, threading
import demobase, camerabase

from pandac.PandaModules import Filename
from pandac.PandaModules import NodePath, WindowProperties, ConfigVariableBool
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from direct.filter.CommonFilters import CommonFilters

####################################################################################################################
class VolumetricLightDemo(demobase.DemoBase):
    """
    Misc - Volumetric Light Demo
    Volumetric Light Demo
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.load = False
        if self.parent.pandaversion < 1.6:
            self.parent.MessageBox("Volumetric Light Demo",
            "This demonstration requires Panda version 1.6.x\n"
            )
            return

        if ConfigVariableBool("basic-shaders-only").getValue():
            self.parent.MessageBox("Volumetric Light Demo",
            "This demonstration uses advance shader technique, which need to set the basic-shaders-only option to #f\nTo run this demo you need a powerful video card, and run demomaster by:\ndemomaster.py f\n"
            )
            return
        self.load = True

        #if (base.win.getGsg().getSupportsBasicShaders() == 0):
        #    addTitle("Normal Mapping: Video driver reports that shaders are not supported.")

        #self.SetCameraPos(Vec3(0,-60,15), Vec3(0,0,15))
        self.textnode = render2d.attachNewNode("textnode")
        self.LoadFilter()
        self.LoadModels()

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,5], [59,59,45], [-45,45, 0], [0,0,45], Vec3(55,-55,20), rate=0.2)
        self.att_cameracontrol.DefaultController()
    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

    def LoadFilter(self):
        # Check video card capabilities.
        if (base.win.getGsg().getSupportsBasicShaders() == 0):
            self.addTitle("Filter: Video driver reports that shaders are not supported.")
            return
        self.filters = CommonFilters(base.win, base.cam)

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
                Vec4( 1, 1, 1, 1 ), Vec3(45,0,0), attenuation=Vec3( 0.7, 0.05, 0.0 ), node=self.lightpivot,
                fBulb=True)
            self.att_pointLight.setLight(render)
            self.bulb = loader.loadModel("models/sphere")
            self.bulb.reparentTo(self.att_pointLight.light)
            self.filters.setVolumetricLighting(self.bulb,32,0.5,1.0,0.05)
            self.bulb.hide()
            # auto shader does not require to set the shader input
            # render.setShaderInput("light", self.att_pointLight.light)


    def ClearScene(self):
        if self.load:
            taskMgr.remove("common-filters-update")
            self.filters.cleanup()
            self.textnode.removeNode()
            self.att_cameracontrol.Destroy()
            #taskMgr.remove("myDemo2")
            base.camera.detachNode()
            #render.clearShaderInput('light')
            self.DestroyAllLights()
            render.removeChildren()
            base.camera.reparentTo(render)

