
#from random import randint, random
import math, sys, thread
import demobase, camerabase, geomutil, skydome2

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib
from direct.interval.LerpInterval import LerpFunc
from direct.interval.IntervalGlobal import Sequence, Func, Wait
from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.actor.Actor import Actor
import scene1

####################################################################################################################
class ShaderFacingRatioDemo(scene1.SceneDemo):
    """
    Shaders - Facing Ratio
    ynjh_jo - http://www.panda3d.org/phpbb2/viewtopic.php?t=3571&highlight=facingratio
    """

    def SetShader(self):
        # shader information
        # default values
        self.att_facingRatioPower = demobase.Att_FloatRange(False, "Facing Ratio:Power", 0, 5, 1.2)
        #self.att_facingRatioPower.setNotifier(self.changeParams)
        self.att_envirLightColor = demobase.Att_color(False, "Facing Ratio:Environment", Vec4(1,1,1,1))
        #self.att_envirLightColor.setNotifier(self.changeParams)
        shader=loader.loadShader('shaders/facingRatio1.sha')
        self.modelnode.setShader(shader)

    def changeParams(self, object):
        self.modelnode.setShaderInput('cam',camera)
        self.modelnode.setShaderInput('light',self.att_pointLight.light)
        self.modelnode.setShaderInput('envirLightColor',self.att_envirLightColor.getColor()*self.att_facingRatioPower.v)

