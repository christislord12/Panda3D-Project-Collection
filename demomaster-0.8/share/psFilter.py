from pandac.PandaModules import NodePath, WindowProperties, loadPrcFileData, ConfigVariableBool
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3, Plane, MouseButton, VBase4D
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, PNMImage, RenderState, GraphicsOutput,FrameBufferProperties

from pandac.PandaModules import CardMaker,OrthographicLens,Camera

class psFilter1():
    def __init__(self, SIZE):
        self.buffer = base.win.makeTextureBuffer( 'surface', SIZE, SIZE)
        self.buffer.setClearColor( Vec4( 0.5, 0.5, 0.5, 0 ) )
        self.buffer.setSort(-1)

        cm = CardMaker("filter-stage-quad")
        cm.setFrameFullscreenQuad()
        #cm.setFrame(0,1,0,1)
        quad = NodePath(cm.generate())
        quad.setDepthTest(0)
        quad.setDepthWrite(0)
        quad.setColor(Vec4(0.5,0.5,0.5,1))

        quadcamnode = Camera("filter-quad-cam")
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0,0)
        lens.setNearFar(-1000, 1000)
        quadcamnode.setLens(lens)
        quadcam = quad.attachNewNode(quadcamnode)

        self.buffer.getDisplayRegion(0).setCamera(quadcam)
        self.buffer.getDisplayRegion(0).setActive(1)

        self.quad = quad
        self.quadcam = quadcam

    def Destroy(self):
        self.quad.clearShader()
        self.quad.removeNode()
        self.quadcam.removeNode()
        base.graphicsEngine.removeWindow(self.buffer)



class psFilter2():
    def __init__(self, SIZE):
        tex128 = Texture()
        tex128.setFormat(Texture.FRgba32)

        fbprops = FrameBufferProperties()
        fbprops.setColorBits(96)
        fbprops.setAlphaBits(32)
        self.buffer = base.win.makeTextureBuffer('SURFACE', SIZE, SIZE, tex128, False, fbprops)

        self.buffer.setClearColor( Vec4( 0.5, 0.5, 0.5, 0 ) )
        self.buffer.setSort(-1)

        cm = CardMaker("filter-stage-quad")
        cm.setFrameFullscreenQuad()
        #cm.setFrame(0,1,0,1)
        quad = NodePath(cm.generate())
        quad.setDepthTest(0)
        quad.setDepthWrite(0)
        quad.setColor(Vec4(0.5,0.5,0.5,1))

        quadcamnode = Camera("filter-quad-cam")
        lens = OrthographicLens()
        lens.setFilmSize(2, 2)
        lens.setFilmOffset(0,0)
        lens.setNearFar(-1000, 1000)
        quadcamnode.setLens(lens)
        quadcam = quad.attachNewNode(quadcamnode)

        self.buffer.getDisplayRegion(0).setCamera(quadcam)
        self.buffer.getDisplayRegion(0).setActive(1)

        self.quad = quad
        self.quadcam = quadcam

    def Destroy(self):
        self.quad.clearShader()
        self.quad.removeNode()
        self.quadcam.removeNode()
        base.graphicsEngine.removeWindow(self.buffer)


