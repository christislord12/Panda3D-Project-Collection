
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
from direct.actor.Actor import Actor

####################################################################################################################
class Morph3Demo(demobase.DemoBase):
    """
    Morphing - Captain Blender
    Morph control in Panda with Captain Blender
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.4)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        #self.SetCameraPos(Vec3(0,-11,0), Vec3(0,0,0))

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-59,-59,-45],
                     [59,59,45],
                     [-90,90,0],
                     [-90,90,0], Vec3(0,-3,2.5))#, rate=0.02)

        self.att_cameracontrol.DefaultController(moveup=None,movedown=None,moveleft=None,moveright=None,fovup=None,fovdown=None)
        self.att_cameracontrol.LockAt(Point3(0,0,2.5))
        self.att_cameracontrol.Stop()

        self.morphTargets = []
        i = 0
        for name in [ "jawdown", "jawleft", "jawright", "lipoutlower", "lipstogether", "lipswide", "round", "lipoutupper",
                "smile", "frown", "eyesclose", "eyesclose-left", "eyesclose-right", "lipinlower",
                "browstogether", "browmidup", "browoutup", "squint", "nosecrinkle",
                "smile-left", "smile-right", "frown-left", "frown-right", "squint-left", "squint-right",
                "browmidup-right", "browmidup-left", "browoutup-right", "browoutup-left", "nosecrinkle-left",
                "nosecrinkle-right", "browdown", "browdown-left", "browdown-right"]:
            namer = name.replace("-", "_")
            morph = self.object.controlJoint(None, 'modelRoot', name)
            self.morphTargets.append(morph)
            expr = "v = self.att_M_%s = demobase.Att_FloatRange(False,'Joint:%s',-2.0, 2.0, 0.0)" % (namer, name)
            exec(expr)
            v.index = i
            i += 1
            v.setNotifier(self.setMorph)

    def setMorph(self, object):
        self.morphTargets[object.index].setX(object.v)

    def LoadLights(self):
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.5, .5, .5, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.7, .7, .7, 1 ),  Vec3( 1, 1, 0 ))
        self.att_directionalLight.setLight(render)
        #self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
        #        Vec4( 1, 1, 1, 1 ), Vec3(0,5,13), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        #self.att_pointLight.setLight(render)


    def LoadModels(self):
        splash=splashCard.splashCard('textures/loading.png')

        self.object = Actor("models/captain2.egg")
        self.object.reparentTo(render)

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

