
import math, sys
import demobase, camerabase

import splashCard
from pandac.PandaModules import Filename
#from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode, FadeLODNode
from pandac.PandaModules import Vec3,Vec4,Point3
#from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool
#from direct.interval.LerpInterval import LerpFunc

####################################################################################################################
class LODDemo(demobase.DemoBase):
    """
    Misc - Splash Card and LOD
    Code from pleopard, astelix: http://panda3d.org/phpbb2/viewtopic.php?t=5795
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        #self.SetCameraPos(Vec3(0,-11,0), Vec3(0,0,0))

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,-45], [59,59,45], [0,0.001, 0], [0,0.001,0], Vec3(0,-11,0), rate=0.02)

        self.att_cameracontrol.DefaultController(moveup=None,movedown=None,moveleft=None,moveright=None,fovup=None,fovdown=None)
    	demobase.addInstructionList(-1,0.95,0.05,
"""Press ESC to release mouse, Enter to resume mouse control
Left mouse button to move forwards
Right mouse button to move backwards
f key to quick zoom in
g key to quick zoom out""",node=self.textnode)


    def LoadLights(self):
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.7, .7, .7, 1 ),  Vec3( 1, 1, 0 ))
        self.att_directionalLight.setLight(render)

    def LoadModels(self):
        splash=splashCard.splashCard('textures/loading.png')

        lodNode = NodePath(FadeLODNode('lod'))
        lodNode.reparentTo(render)
        lodNode.setPos(0, 3, 0)

        # assign the model with less poligons to the farthest distance range
        lod0 = loader.loadModel("models/monkeylod/monkey00")
        lod0.reparentTo(lodNode)
        lodNode.node().addSwitch(999999, 40)

        lod1 = loader.loadModel("models/monkeylod/monkey01")
        lod1.reparentTo(lodNode)
        lodNode.node().addSwitch(40, 20)

        lod1 = loader.loadModel("models/monkeylod/monkey02")
        lod1.reparentTo(lodNode)
        lodNode.node().addSwitch(20, 10)

        # assign the model with full poligons to the nearest distance range
        lod2 = loader.loadModel("models/monkeylod/monkey03")
        lod2.reparentTo(lodNode)
        lodNode.node().addSwitch(10, 0)

        #sweep out the loading message
        splash.destroy()



    def ClearScene(self):
        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

