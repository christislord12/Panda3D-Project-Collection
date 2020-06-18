from random import randint, random
import math, sys, os
import demobase, camerabase, splashCard

from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3

from skydome1 import *
from skydome2 import *
import ocean2
#import waterplane1

####################################################################################################################
class Ocean2Demo(demobase.DemoBase):
    """
    Nature - Ocean 2 from Ogre
    Port from Ogre Ocean 2
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def CameraSetup(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-500,-500,20], [500,500,300], #[-89,89, -15], [0,0,-107],
                    [-89,89, -5], [0,0,0],
                     Vec3(0,0,30),
                     fov=[5.0,120.0,68.0],
                     rate=1.0, speed=60)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.setNotifier(self.camchanged)
        self.textnode = render2d.attachNewNode("textnode")
    	demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

    def InitScene(self):
        splash=splashCard.splashCard('textures/loading.png')
        self.CameraSetup()
        self._water_level = Vec4(0.0, 0.0, 12.0, 1.0)
        self.LoadModels()

        taskMgr.add(self.cameraUpdated, "camupdate")
        #self.att_water.setStandardControl()

        self.setSkyBox()
        splash.destroy()


    def camchanged(self, object):
        self.att_water.setFov(self.att_cameracontrol.att_fov.v)


    def LoadModels(self):
        # skybox
        #skybox1 = self.LoadSkyBox('models/daybox1/skybox.egg')
        skybox1 = self.LoadSkyBox('models/skyboxtemplate/skybox.egg')
        skybox2 = self.LoadSkyBox('models/morningbox/morningbox.egg')
        self.att_skydome1 = SkyDome1(render)
        self.att_skydome1.setStandardControl()

        self.att_skydome2 = SkyDome2(render,scale=(4000,4000,1000))
        self.att_skydome2.setStandardControl()

        self.skyboxselection = 0
        self.skyboxes = [skybox2, self.att_skydome1, skybox1, self.att_skydome2]

        self.att_water = None
        self.LoadWaterNode()
        render.setShaderInput('time', 0)

        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def LoadWaterNode(self):
        self.att_water = ocean2.WaterNode(1000,1000,50,50, self._water_level.getZ())
        # self.att_water = waterplane1.WaterNode(-500,-500,500,500, self._water_level.getZ())
        self.att_water.setStandardControl()

    def cameraUpdated(self, task):
        pos = base.camera.getPos()
        pos.setZ( -10 )
        for skybox in self.skyboxes:
            skybox.setPos(pos)
            #skybox.setPos(Vec3(campos[0],campos[1],campos[2]+100))

        render.setShaderInput('time', task.time)
        #render.setShaderInput('time', (1,1))

        pos = base.camera.getPos()
        mc = base.camera.getMat( )
        self.att_water.changeCameraPos(pos, mc)
        return task.cont

    def ClearScene(self):
        self.att_cameracontrol.Destroy()
        taskMgr.remove("camupdate")
        self.att_water.Destroy()
        self.att_skydome1.Destroy()
        self.att_skydome2.Destroy()
        self.textnode.removeNode()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def Demo01(self):
        """Toggle skybox"""
        self.skyboxselection = ( self.skyboxselection + 1 ) % len(self.skyboxes)

        #render.hide()
        splash=splashCard.splashCard('textures/loading.png')
        self.setSkyBox()
        splash.destroy()
        #render.show()

    def Demo02(self):
        """Toggle cubemap/reflection camera mode"""
        if hasattr(self.att_water, "cubemap_mode"):
            self.att_water.cubemap_mode = not self.att_water.cubemap_mode
            self.att_water.changeParams(None)

    def setSkyBox(self):
        for skybox in self.skyboxes:
            skybox.hide()
        self.skyboxes[self.skyboxselection].show()
        self.att_water.hide()
        # use a different file name otherwise the cache manager will be confused
        cubemapfile = 'tmp/cube%s_#.jpg' % self.skyboxselection
        #cubemapfile = 'tmp/cube_map#.png'
        base.saveCubeMap(cubemapfile, size = 256)

        self.att_water.setCubeMap(cubemapfile)
        self.att_water.show()


