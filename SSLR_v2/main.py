# -*- coding: utf_8 -*-
from panda3d.core import *
from direct.filter.FilterManager import FilterManager

class SSR():
    
    def __init__(self, app):
        self.base = app
        # (!) Note: the same near and far plane also should be setted 
        # in the shader constants
        self.base.cam.node().getLens().setNearFar(1.0, 500.0)
        # First pass we render needed texture
        self.manager = FilterManager(self.base.win, self.base.cam)
        self.albedo = Texture()
        self.depth = Texture()
        self.normal = Texture()
        final_quad = self.manager.renderSceneInto(colortex = self.albedo, 
                                                 depthtex = self.depth, 
                                                 auxtex = self.normal,
                                                 auxbits = AuxBitplaneAttrib.ABOAuxNormal)
        # Second pass - work with previous rendered textures
        # also we pass base camera to the shader to get needed matrices 
        # becouse the filter buffer work with the 2d ortogonal camera
        ssr_filter, ssr_quad = self.make_filter_buffer(self.base.win, 
                                        'ssr_buffer', 1, 'ssr_zfar.sha',
                                        texture = None,
                                        inputs = [("albedo", self.albedo),
                                                  ("depth", self.depth),
                                                  ("normal", self.normal),
                                                  ("mcamera", self.base.cam)
                                                  ]
                                            )
        self.ssr_filter = ssr_filter
        self.ssr_quad = ssr_quad
        # Third pass - mix color and reflected texture
        # We can awoid this pass and do this in the second pass, but 
        # we can have other textures to mix, or do other 
        # postprocess operations
        final_quad.setShader(Shader.load("mix.sha"))
        final_quad.setShaderInput("albedo", self.albedo)
        final_quad.setShaderInput("reflection", ssr_filter.getTexture())
        self.final_quad = final_quad
    
    def make_filter_buffer(self, srcbuffer, name, sort, prog, texture = None, inputs = None):
        filterBuffer=base.win.makeTextureBuffer(name, 512, 512)
        filterBuffer.setSort(sort)
        filterBuffer.setClearColor(Vec4(1,0,0,1))
        blurCamera=base.makeCamera2d(filterBuffer)
        blurScene=NodePath("Filter scene %i" % sort)
        blurCamera.node().setScene(blurScene)
        shader = loader.loadShader(prog)
        card = srcbuffer.getTextureCard()
        if texture:
            card.setTexture(texture)
        card.reparentTo(blurScene)
        card.setShader(shader)
        if inputs:
            for name, val in inputs:
                card.setShaderInput(name, val)
        return filterBuffer, card
        
# Just a test scene
def test_scene(scene_root):
    back = loader.loadModel('test_scene')
    back.setScale(5)
    back.reparentTo(scene_root)
    box = loader.loadModel('box')
    box.reparentTo(scene_root)
    box.setScale(1,1,6)
    tp = loader.loadModel('teapot')
    tp.reparentTo(scene_root)
    tp.setPos(-2, 2, 0)
    tp.setScale(0.5)
    sm = loader.loadModel('smiley')
    sm.reparentTo(scene_root)
    sm.setPos(0, 4, 1)
    sm.setColor(Vec4(1, 0, 0, 1))

    dlight = DirectionalLight('dlight')
    dlight.setColor(VBase4(0.5, 0.5, 0.5, 1))
    dlnp = scene_root.attachNewNode(dlight)
    dlnp.setHpr(0, -60, 0)
    scene_root.setLight(dlnp)
    alight = AmbientLight('alight')
    alight.setColor(VBase4(0.5, 0.5, 0.5, 1))
    alnp = scene_root.attachNewNode(alight)
    scene_root.setLight(alnp)

if __name__ == '__main__':
    loadPrcFileData("", "prefer-parasite-buffer #f")
    #loadPrcFileData("", "show-buffers #t")
    loadPrcFileData("", "show-frame-rate-meter #t")
    loadPrcFileData("", "basic-shaders-only #f")
    #loadPrcFileData("", "dump-generated-shaders #t")
    #loadPrcFileData("", "notify-level-gobj debug")
    #loadPrcFileData("", "notify-level-glgsg debug")

    #nout = MultiplexStream()
    #Notify.ptr().setOstreamPtr(nout, 0)
    #nout.addFile(Filename("log.txt"))
    
    import direct.directbase.DirectStart
    from direct.gui.OnscreenText import OnscreenText
    import random
    test_scene(render)
    render.setShaderAuto()
    ssr = SSR(base)
    
    def bind_shader(name):
        ssr.ssr_quad.setShader(Shader.load(name))
    
    base.accept('1', bind_shader, extraArgs = ['ssr_zfar.sha',])
    base.accept('2', bind_shader, extraArgs = ['ssr_base.sha',])
    
    
    # Instruction
    OnscreenText(text = '[1], [2] to switch shader',
                pos = (-0.7, 0.9), scale = 0.07, fg = (1,1,1,1))
    
    run()
