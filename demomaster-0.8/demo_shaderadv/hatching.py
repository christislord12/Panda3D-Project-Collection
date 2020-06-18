
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
from scene1 import SceneDemo

####################################################################################################################
class ShaderHatching1Demo(SceneDemo):
    """
    Shaders - Hatching 1
    SHADERS for Game Programmers and Artists
    """

    def SetShader(self):
        # shader information
        # default values
        self.att_ambient = demobase.Att_FloatRange(False, "Ambient", 0, 1, 0.2)
        #self.att_envirLightColor.setNotifier(self.changeParams)
        shader=loader.loadShader('shaders/hatching.sha')
        self.modelnode.setShader(shader)
        for i in range(6):
            hatch = loader.loadTexture("textures/Hatch%d.dds" % i)
            self.modelnode.setShaderInput('hatch%d' % i, hatch)

    def changeParams(self, object):
        self.modelnode.setShaderInput('cam',camera)
        self.modelnode.setShaderInput('light',self.att_pointLight.light)

        self.modelnode.setShaderInput('ambient',self.att_ambient.v)


    def Demo01(self):
        """Clear Shader"""
        self.modelnode.clearShader()

    def Demo02(self):
        """Default Shader"""
        shader=loader.loadShader('shaders/hatching.sha')
        self.modelnode.setShader(shader)

    def Demo03(self):
        """Shader 1"""
        shader=loader.loadShader('shaders/hatching1.sha')
        self.modelnode.setShader(shader)

    def Demo04(self):
        """Shader 2"""
        shader=loader.loadShader('shaders/hatching2.sha')
        self.modelnode.setShader(shader)

