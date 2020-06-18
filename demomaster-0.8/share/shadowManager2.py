# from rollingt70 http://panda3d.org/phpbb2/viewtopic.php?t=5442

from pandac.PandaModules import GraphicsOutput, Texture, NodePath, Vec3
from pandac.PandaModules import PandaNode, WindowProperties, GraphicsPipe
from pandac.PandaModules import ShaderGenerator, Shader, RenderState
from pandac.PandaModules import FrameBufferProperties, Vec4
from direct.filter.FilterManager import FilterManager
import demobase

class ShadowManager(demobase.Att_base):
    """This class manages shadows for a scene."""
    def shaderSupported(self):
        return base.win.getGsg().getSupportsBasicShaders() and \
               base.win.getGsg().getSupportsDepthTexture()

        #return base.win.getGsg().getSupportsBasicShaders() and \
        #       base.win.getGsg().getSupportsDepthTexture() and \
        #       base.win.getGsg().getSupportsShadowFilter()

    def IsOK(self):
        return self.ok

    def __init__(self, scene = base.render, fov = 40, near = 10, far = 100, hardness=0.2):
        demobase.Att_base.__init__(self, False, "Shadow Manager")
        self.ok = self.shaderSupported()
        if not self.ok:
            return

        self.scene = scene

        # Create the depth buffer plus a texture to store the output in
        self.hardness = hardness
        self.depthbuffer = self.createOffscreenBuffer(-3)
        self.depthmap = Texture()
        self.depthbuffer.addRenderTexture(self.depthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
        #self.depthbuffer.addRenderTexture(self.depthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
        #if (base.win.getGsg().getSupportsShadowFilter()):
        #        self.depthmap.setMinfilter(Texture.FTShadow)
        #        self.depthmap.setMagfilter(Texture.FTShadow)

        # Create the shadow buffer plus a texture to store the output in
        self.shadowbuffer = self.createOffscreenBuffer(-2)
        self.shadowmap = Texture()
        self.shadowbuffer.addRenderTexture(self.shadowmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)

        self.manager = FilterManager(base.win, base.cam)
        self.blur = False
##        if self.blur:
##            # First filter stage just blurs the shadow map
##            # Just blurring in x-direction for now
##            self.blurbuffer = self.createOffscreenBuffer(-1)
##            self.blurtex = Texture()
##            self.blurbuffer.addRenderTexture(self.blurtex, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPColor)
##            blurquad = self.manager.renderQuadInto(colortex=self.blurtex)
##            blurquad.setShader(loader.loadShader("shaders/blurx.sha"))
##            blurquad.setShaderInput("tex", self.shadowmap)


        # blend shadow map with render output
        self.rendertex = Texture()
        renderquad = self.manager.renderSceneInto(colortex=self.rendertex)

        renderquad.setShader(loader.loadShader("shaders/shadowcombiner.sha"), 1)
        renderquad.setShaderInput("render", self.rendertex)
        if self.blur:
            renderquad.setShaderInput("shadow", self.blurtex)
        else:
            renderquad.setShaderInput("shadow", self.shadowmap)

        renderquad.setShaderInput("light", 1,1,1,1)
        renderquad.setShaderInput("props", self.hardness,0,0,0)
        self.renderquad = renderquad

        # Make the shadow caster camera
        self.castercam = base.makeCamera(self.depthbuffer)
        self.castercam.reparentTo(self.scene)
        self.castercam.node().setScene(self.scene)
        self.castercam.node().getLens().setFov(fov)
        self.castercam.node().getLens().setNearFar(near, far)

        # Put a shader on the shadow caster camera.
        lci = NodePath(PandaNode("lightCameraInitializer"))
        ####lci.setShaderOff()
        lci.setShader(loader.loadShader("shaders/caster.sha"), 1)
        ####self.castercam.node().setInitialState(RenderState.makeEmpty())
        ####print lci.getState()
        self.castercam.node().setInitialState(lci.getState())
        #####self.castercam.setShaderOff()

        # Make the shadow camera
        self.shadowcam = base.makeCamera(self.shadowbuffer, lens=base.cam.node().getLens())
        self.shadowcam.reparentTo(self.scene)


        # Put a shader on the shadow camera.
        lci = NodePath(PandaNode("lightCameraInitializer"))
        lci.setShader(loader.loadShader("shaders/shadowonly2.sha"), 1)
        self.shadowcam.node().setInitialState(lci.getState())
        self.shadowcam.reparentTo(base.cam)
        #TEMP
        #self.shadowcam.clearShader()

        # Set the shader inputs
        self.scene.setShaderInput("light", self.castercam)
        self.scene.setShaderInput("depthmap", self.depthmap)

    def Destroy(self):
        if self.ok:
            self.shadowcam.node().setInitialState(RenderState.makeEmpty())
            self.shadowcam.removeNode()
            self.castercam.node().setInitialState(RenderState.makeEmpty())
            self.castercam.removeNode()
            base.graphicsEngine.removeWindow(self.shadowbuffer)
            base.graphicsEngine.removeWindow(self.depthbuffer)
            self.manager.cleanup()

        base.bufferViewer.enable(False)

    # These are two functions which help creating two different kind of offscreen buffers.
    def createOffscreenBuffer(self, sort):
        winprops = WindowProperties.size(512,512)
        #winprops = WindowProperties.size(1024,1024)
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        props.setDepthBits(1)
        return base.graphicsEngine.makeOutput(
            base.pipe, "offscreenBuffer",
            sort, props, winprops,
            GraphicsPipe.BFRefuseWindow,
            base.win.getGsg(), base.win)

##    def makeFilterBuffer(scene, srcbuffer, name, sort, shader):
##        blurBuffer = base.win.makeTextureBuffer(name, 512, 512)
##        blurBuffer.setSort(sort)
##        blurBuffer.setClearColor(Vec4(1, 0, 0, 1))
##        blurCamera = base.makeCamera2d(blurBuffer)
##        blurCamera.reparentTo(scene)
##        blurScene = NodePath("blurScene")
##        blurCamera.node().setScene(blurScene)
##        card = srcbuffer.getTextureCard()
##        card.reparentTo(blurScene)
##        card.setShader(shader)
##        return blurBuffer, blurCamera

    def setFov(self, fov):
        if self.ok:
            self.castercam.node().getLens().setFov(fov)

    def setHardness(self, hardness):
        if self.ok:
            self.hardness = hardness
            self.renderquad.setShaderInput("props", self.hardness,0,0,0)

    def changeLightPos(self, pos, lookAt):
        if self.IsOK():
            self.castercam.setPos(pos[0],pos[1],pos[2])
            self.castercam.lookAt(lookAt[0],lookAt[1],lookAt[2])
            self.lookat = lookAt

    def showFrustum(self):
        if self.IsOK():
            self.castercam.node().showFrustum() # Show the frustrum

    def setStandardControl(self):
        fov = self.castercam.node().getLens().getFov()
        self.att_fov = demobase.Att_FloatRange(False, "Fov", 10.0, 200.0, fov[0], 0)
        self.att_fov.setNotifier(self.changeParams)
        self.att_hardness = demobase.Att_FloatRange(False, "Hardness", 0, 5., self.hardness)
        self.att_hardness.setNotifier(self.changeParams)

        pos = self.castercam.getPos()
        self.att_lightpos = demobase.Att_Vecs(False, "Light Pos", 3, pos, -40, 40)
        self.att_lightpos.setNotifier(self.changeLight)
        self.att_lightat = demobase.Att_Vecs(False, "LookAt", 3, self.lookat, -30, 30)
        self.att_lightat.setNotifier(self.changeLight)

    def changeLight(self, object):
        if self.IsOK():
            print self.att_lightpos.getValue(), self.att_lightat.getValue()
            self.changeLightPos(self.att_lightpos.getValue(), self.att_lightat.getValue())

    def changeParams(self, object):
        if self.IsOK():
            fov = self.att_fov.v
            self.setFov(fov)
            self.setHardness(self.att_hardness.v)
