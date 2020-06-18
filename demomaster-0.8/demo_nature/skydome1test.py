import demobase, camerabase
from pandac.PandaModules import NodePath,Vec3,Vec4,TextureStage,TexGenAttrib

from skydome1 import *

class SkyDomeDemo(demobase.DemoBase):
    """
    Nature - Skydome 1 effect
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        self.LoadModels()
        self.CameraSetup()

    def CameraSetup(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-200,-200,15], [200,200,50], #[-89,89, -15], [0,0,-107],
                    [-89,89, -5], [0,0,0],
                     Vec3(0,0,100),
                     rate=0.2)

        self.att_cameracontrol.DefaultController()
        self.textnode = render2d.attachNewNode("textnode")
##    	demobase.addInstructionList(-1,0.95,0.05,
##"""Press ESC to release mouse, Enter to resume mouse control
##Move mouse to rotate camera
##Left mouse button to move forwards
##Right mouse button to move backwards
##f key to quick zoom in
##g key to quick zoom out""",node=self.textnode)



    def LoadModels(self):
        self.att_skybox = SkyDome1(render)
        self.att_skybox.setStandardControl()
        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def ClearScene(self):
        self.att_cameracontrol.Destroy()
        self.att_skybox.Destroy()
        self.textnode.removeNode()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)


