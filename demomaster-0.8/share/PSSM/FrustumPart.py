###########################################################
# Estrada Real Digital
# DCC - UFMG
###########################################################

from pandac.PandaModules import *

import random
import math




class FrustumPart():

    def __init__(self, i, size):

        self.size = size
        self.splitMaxDepth = None
        self.splitMinDepth = None

        self.createBuffer()
        self.createDepthMap()
        self.cam = base.makeCamera(self.buffer)

        lens = OrthographicLens()
        lens.setFilmSize(1, 1)
        self.cam.node().setLens(lens)
        self.cam.node().getLens().setFar(1000)

        #self.cam.node().showFrustum()
        self.cam.setShaderOff(1)



    def createBuffer(self):
        # creating the offscreen buffer.
        winprops = WindowProperties.size(self.size, self.size)
        props = FrameBufferProperties()
#        props.setRgbColor(1)
#        props.setAlphaBits(1)
#        props.setDepthBits(1)
        self.buffer = base.graphicsEngine.makeOutput(
                 base.pipe, "offscreen buffer", -2,
                 props, winprops,
                 GraphicsPipe.BFRefuseWindow,
                 base.win.getGsg(), base.win)

    def createDepthMap(self):

        self.depthmap = Texture()
        self.buffer.addRenderTexture(self.depthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
        if (base.win.getGsg().getSupportsShadowFilter()):
            self.depthmap.setMinfilter(Texture.FTShadow)
            self.depthmap.setMagfilter(Texture.FTShadow)


        self.depthmap.setBorderColor(Vec4(1,1,1,1))
        self.depthmap.setWrapU(Texture.WMBorderColor)
        self.depthmap.setWrapV(Texture.WMBorderColor)

    def calculateDepth(self, position, numSplits, pssmBias):
        si = (float(position) / numSplits)

        camRatio = base.cam.node().getLens().getFar() / base.cam.node().getLens().getNear()
        log = (base.cam.node().getLens().getNear() * (math.pow(camRatio, si)))
        uniform = base.cam.node().getLens().getNear() + (base.cam.node().getLens().getFar() - base.cam.node().getLens().getNear()) * (si)
        splitDepth =  log * pssmBias + uniform * (1.0 - pssmBias)

        self.splitMinDepth = splitDepth

    def Destroy(self):
        self.cam.node().setInitialState(RenderState.makeEmpty())
        self.cam.removeNode()
        base.graphicsEngine.removeWindow(self.buffer)
