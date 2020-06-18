# clcheung June 2009
from pandac.PandaModules import GraphicsOutput, Texture, NodePath, Vec3
from pandac.PandaModules import PandaNode, WindowProperties, GraphicsPipe
from pandac.PandaModules import ShaderGenerator, Shader, RenderState
from pandac.PandaModules import FrameBufferProperties, Vec4
from direct.filter.FilterManager import FilterManager
import demobase
from filtercommon import *

class DOFManager(demobase.Att_base):
    """This class help to create DOF view for a scene."""
    def IsOK(self):
        return self.ok

    def __init__(self, scene = base.render, SIZE=512, focus = 0.5, blur=0.04, maxblur=0.006):
        demobase.Att_base.__init__(self, False, "DOF Manager")
        #self.ok = self.shaderSupported()
        #if not self.ok:
        #    return

        self.scene = scene
        self.tex = Texture()
        self.depthmap = Texture()
        #self.depthmap.setMinfilter(Texture.FTShadow)
        #self.depthmap.setMagfilter(Texture.FTShadow)
        self.manager = FilterManager(base.win,base.cam)
        self.quad = self.manager.renderSceneInto(colortex=self.tex,depthtex=self.depthmap)
        self.quad.setShader(loader.loadShader("shaders/dof2.sha"))
        self.quad.setShaderInput("src",self.tex)
        self.quad.setShaderInput("dtex",self.depthmap)
        self.setFocus(focus)
        self.setBlurriness(blur)
        self.setMaxBlurriness(maxblur)
        self.setParam()

    def setFocus(self, focus):
        self.focus = focus

    def setBlurriness(self, blur):
        self.blur = blur

    def setMaxBlurriness(self, maxblur):
        self.maxblur = maxblur

    def setParam(self):
        self.quad.setShaderInput("param1", self.focus, self.blur, self.maxblur, 0)

    def Destroy(self):
        self.manager.cleanup()
        self.quad.clearShader()

    def setStandardControl(self):
        self.att_focus = demobase.Att_FloatRange(False, "Focus", 0.0, 1, self.focus)
        self.att_focus.setNotifier(self.changeParams)
        self.att_blur = demobase.Att_FloatRange(False, "Blurriness", 0.0, 0.1, self.blur, 3)
        self.att_blur.setNotifier(self.changeParams)
        self.att_maxblur = demobase.Att_FloatRange(False, "Max Blurriness", 0.0, 0.01, self.maxblur, 3)
        self.att_maxblur.setNotifier(self.changeParams)

    def changeParams(self, object):
        self.setFocus(self.att_focus.v)
        self.setBlurriness(self.att_blur.v)
        self.setMaxBlurriness(self.att_maxblur.v)
        self.setParam()
