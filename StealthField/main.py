# -*- coding: utf_8 -*-
from panda3d.core import *
loadPrcFileData("", "show-frame-rate-meter #t")
loadPrcFileData("", "prefer-parasite-buffer #t")
from direct.filter.FilterManager import FilterManager
from direct.interval.IntervalGlobal import *
from direct.showbase.DirectObject import DirectObject 
from direct.gui.OnscreenText import OnscreenText 

MAIN_MASK = BitMask32.bit(1)
STEALTH_MASK = BitMask32.bit(17)

class Filter(DirectObject):

    def __init__(self, showbase, main_mask, stealth_mask):
        self.app = app
        self.manager = None
        self.quad = None
        self.main_mask = main_mask
        app.cam.node().setCameraMask(self.main_mask)
        self.stealth_mask = stealth_mask
        self.buffers = {}
        self.cameras = {}
        self.textures = {}
        self.on_int = LerpFunc(self.blend,
                               fromData=0.0,
                               toData=1.0,
                               duration=1.0)
        self.off_int = LerpFunc(self.blend,
                               fromData=1.0,
                               toData=0.0,
                               duration=1.0)
        self.state = False
        self.accept('space', self.switch)
        self.make_depth_normal_FBR()
        self.make_color_FBR()
        self.make_filters()
        
    def set_main_scene(self, root):
        root.hide(self.stealth_mask)
        
    def set_model(self, root):
        root.hide(self.main_mask)

    def make_depth_normal_FBR(self):
        # Buffer for the depth and normal textures with our model, 
        # which should be stealthed. We apply shader on the buffer camera
        # to get model normals in camera space
        ldepthmap = Texture()
        ldepthmap.setFormat( Texture.FDepthComponent )
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setDepthBits(1)
        props.setAlphaBits(1)
        mybuffer = app.win.makeTextureBuffer("AUX D-N Buffer", 
                                              self.app.win.getXSize(), 
                                              self.app.win.getYSize(), 
                                              to_ram = False, 
                                              tex = ldepthmap, 
                                              fbp = props)
        mybuffer.setClearColor(Vec4(0,0,0,0)) 
        mybuffer.setSort(-100)
        mycamera = self.app.makeCamera(mybuffer)
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(loader.loadShader("normals.sha"), 1)
        mycamera.node().setInitialState(tempnode.getState())
        mycamera.node().setLens(self.app.cam.node().getLens())
        mycamera.reparentTo(self.app.camera)
        mycamera.node().setCameraMask(self.stealth_mask)
        
        distortmap = Texture()
        mybuffer.addRenderTexture(distortmap,
           GraphicsOutput.RTMBindOrCopy,
           GraphicsOutput.RTPColor)
        
        self.buffers['depth-normal'] = mybuffer
        self.cameras['depth-normal'] = mycamera
        self.textures['normals'] = distortmap
        self.textures['depth'] = ldepthmap
        
    def make_color_FBR(self):
        # Buffer for the color texture with stealthed model
        # We need another camera for this - without normals shader
        colormap = Texture()
        props = FrameBufferProperties()
        props.setRgbColor(1)
        props.setAlphaBits(1)
        mybuffer = app.win.makeTextureBuffer("AUX Color Buffer", 
                                              self.app.win.getXSize(), 
                                              self.app.win.getYSize(), 
                                              to_ram = False, 
                                              tex = colormap, 
                                              fbp = props)
        mybuffer.setClearColor(Vec4(0,0,0,0)) 
        mybuffer.setSort(-100)
        mycamera = app.makeCamera(mybuffer)
        mycamera.node().setLens(app.cam.node().getLens())
        mycamera.reparentTo(app.camera)
        mycamera.node().setCameraMask(self.stealth_mask)
        self.buffers['color'] = mybuffer
        self.cameras['color'] = mycamera
        self.textures['color'] = colormap


    def make_filters(self):
        # Filter to final blend previously prepared textures, 
        # also it makes color and depth textures from the main scene
        self.manager = FilterManager(app.win, app.cam)
        self.textures['main color'] = Texture()
        self.textures['main depth'] = Texture()
        self.quad = self.manager.renderSceneInto(
                        colortex = self.textures['main color'], 
                        depthtex = self.textures['main depth'])
        self.quad.setShader(Shader.load("stealth.sha"))
        self.quad.setShaderInput("maincolor", self.textures['main color'])
        self.quad.setShaderInput("distort", self.textures['normals'])
        self.quad.setShaderInput("depth", self.textures['depth'])
        self.quad.setShaderInput("maindepth", self.textures['main depth'])
        self.quad.setShaderInput("color", self.textures['color'])
        self.quad.setShaderInput("colormask", loader.loadTexture('hf.png'))
        self.quad.setShaderInput("blend", 0.0)
        
    def blend(self, val):
        self.quad.setShaderInput("blend", val)
        
    def switch(self):
        if not self.state:
            self.off_int.finish()
            self.on_int.start()
        else:
            self.on_int.finish()
            self.off_int.start()
        self.state = not self.state


if __name__ == '__main__':
    # I used a scene from the standart panda helloworld
    from helloworld import MyApp
    app = MyApp()
    OnscreenText(text="Press space to switch stels-field.",
                 fg=(1,1,1,1), bg = (0,0,0,0.5),
                 pos=(-0.6, 0.8),
                 parent = app.aspect2d)
    # App is an exemplar of ShowBase. Usually - base, if used directstart. 
    # Or something, inherited from ShowBase
    f = Filter(app, MAIN_MASK, STEALTH_MASK)
    f.set_main_scene(app.environ)
    f.set_model(app.pandaActor)

    app.bufferViewer.toggleEnable()

    app.run()
