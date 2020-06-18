
import math, sys
import demobase, camerabase

import splashCard
from pandac.PandaModules import Filename

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode, FadeLODNode
from pandac.PandaModules import Vec3,Vec4,Point3
from direct.actor.Actor import Actor

####################################################################################################################
class Morph2Demo(demobase.DemoBase):
    """
    Morphing - Block
    Morph control in Panda
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(1.0, 0.0, 1.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        #self.SetCameraPos(Vec3(0,-11,0), Vec3(0,0,0))

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-59,-59,-45],
                     [59,59,45],
                     [-90,90,-30],
                     [-90,90,45], Vec3(0,-4,0))#, rate=0.02)

        self.att_cameracontrol.DefaultController(moveup=None,movedown=None,moveleft=None,moveright=None,fovup=None,fovdown=None)
        self.att_cameracontrol.LockAt(Point3(0,0,0))
        self.att_cameracontrol.Stop()

        self.morphTargets = []
        i = 0
        for name in [ "Taper_1", "Wedge"]:
            morph = self.object.controlJoint(None, 'modelRoot', name)
            self.morphTargets.append(morph)
            expr = "v = self.att_M_%s = demobase.Att_FloatRange(False,'Joint:%s',-2.0, 2.0, 0.0)" % (name, name)
            exec(expr)
            v.index = i
            i += 1
            v.setNotifier(self.setMorph)

    def setMorph(self, object):
        self.morphTargets[object.index].setX(object.v)

    def LoadLights(self):
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.5, .5, .5, 1 ))
        self.att_ambientLight.setLight(render)
        #self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.7, .7, .7, 1 ),  Vec3( 1, 1, 0 ))
        #self.att_directionalLight.setLight(render)
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(0,0,3), attenuation=Vec3( 0.1, 0.04, 0.0 ), node=render, fBulb=True)
        self.att_pointLight.setLight(render)


    def LoadModels(self):
        splash=splashCard.splashCard('textures/loading.png')

        self.object = Actor("models/basic")
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

