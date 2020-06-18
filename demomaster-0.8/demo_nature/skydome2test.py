import demobase, camerabase
from pandac.PandaModules import NodePath,Vec3,Vec4,TextureStage,TexGenAttrib

from skydome2 import *

class SkyDome2Demo(demobase.DemoBase):
    """
    Nature - Skydome 2 effect
    Code from: http://panda3d.org/phpbb2/viewtopic.php?t=2385
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        taskMgr.add(self.cameraUpdated, "camupdate")
        self.LoadModels()
        self.CameraSetup()

    def CameraSetup(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-500,-500,10], [500,500,300], #[-89,89, -15], [0,0,-107],
                    [-89,89, -5], [0,0,0],
                     Vec3(0,0,100),
                     fov=[5.0,120.0,68.0],
                     rate=1.0, speed=60)
##
##        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
##                     [-200,-200,15], [200,200,50], #[-89,89, -15], [0,0,-107],
##                    [-89,89, 0],
##                    [0,0,0],
##                     Vec3(0,0,0),
##                     rate=0.2)

        self.att_cameracontrol.DefaultController()
        self.textnode = render2d.attachNewNode("textnode")
##    	demobase.addInstructionList(-1,0.95,0.05,
##"""Press ESC to release mouse, Enter to resume mouse control
##Move mouse to rotate camera
##Left mouse button to move forwards
##Right mouse button to move backwards
##f key to quick zoom in
##g key to quick zoom out""",node=self.textnode)
        self.att_cameracontrol.ShowPosition(self.textnode)



    def LoadModels(self):
        self.att_skybox = SkyDome2(render)
        #self.att_skybox = SkyDome(render)
        self.att_skybox.setStandardControl()
        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def ClearScene(self):
        self.att_cameracontrol.Destroy()
        taskMgr.remove("camupdate")
        self.att_skybox.Destroy()
        self.textnode.removeNode()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def cameraUpdated(self, task):
        pos = base.camera.getPos()
        pos.setZ( 0 )
        self.att_skybox.setPos(pos)
        render.setShaderInput('time', task.time)
        return task.cont
