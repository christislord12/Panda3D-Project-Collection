
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
class Morph1Demo(demobase.DemoBase):
    """
    Morphing - Ripple
    Morph control in Panda
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        #self.SetCameraPos(Vec3(0,-11,0), Vec3(0,0,0))

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-59,-59,-45],
                     [59,59,45],
                     [-90,90, 45],
                     [-90,90,-45], Vec3(0,-1,0))#, rate=0.02)

        self.att_cameracontrol.DefaultController(moveup=None,movedown=None,moveleft=None,moveright=None,fovup=None,fovdown=None)
        self.att_cameracontrol.LockAt(Point3(0,0,0))
        self.att_cameracontrol.Stop()

        self.morphTargets = []
        for i in range(7):
            name = "%d" % (i+1)
            morph = self.ripple.controlJoint(None, 'modelRoot', name)
            self.morphTargets.append(morph)

            #v = vars()["self.att_M_%s" % name] = demobase.Att_FloatRange(False,'Target:%s' % name,-2.0, 2.0, 0.0)
            expr = "v = self.att_M_%s = demobase.Att_FloatRange(False,'Joint:%s',-2.0, 2.0, 0.0)" % (name, name)
            exec(expr)
            v.index = i
            v.setNotifier(self.setMorph)

    def setMorph(self, object):
        self.morphTargets[object.index].setX(object.v)

    def LoadLights(self):
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.7, .7, .7, 1 ),  Vec3( 1, 1, 0 ))
        self.att_directionalLight.setLight(render)

    def LoadModels(self):
        splash=splashCard.splashCard('textures/loading.png')

        self.ripple = Actor("ripple")
        self.ripple.setTwoSided(True)
        self.ripple.reparentTo(render)

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

    def Demo01(self):
        """Play Ripple Animation"""
        for i in range(7):
            name = "%d" % (i+1)
            morph = self.ripple.releaseJoint('modelRoot', name)
        self.ripple.play("ripple")

    def Demo02(self):
        """Stop Ripple Animation"""
        self.ripple.stop("ripple")
        self.morphTargets = []
        for i in range(7):
            name = "%d" % (i+1)
            morph = self.ripple.controlJoint(None, 'modelRoot', name)
            self.morphTargets.append(morph)
