# -*- coding: utf_8 -*-
from panda3d.core import *
loadPrcFileData("", "show-frame-rate-meter #t")
loadPrcFileData("", "prefer-parasite-buffer #t")
from direct.filter.FilterManager import FilterManager
from direct.particles.ParticleEffect import ParticleEffect
import direct.directbase.DirectStart
import random

MAIN_MASK = BitMask32.bit(1)
CLOUD_MASK = BitMask32.bit(17)

def setup_lights(root):
    l_root = NodePath('lights')
    l_root.reparentTo(root)
    ambientLight = AmbientLight("ambientLight")
    ambientLight.setColor(Vec4(.3, .3, .2, 1))
    plight = PointLight("PLight")
    plight_np = l_root.attachNewNode(plight)
    plight_np.setPos(-3, 3, 3)
    m = loader.loadModel('sphere')
    m.setLightOff()
    m.setScale(0.1)
    m.reparentTo(plight_np)
    m.hide(CLOUD_MASK)
    root.setLight(plight_np)
    root.setLight(l_root.attachNewNode(ambientLight))
    return l_root
    
def light_task(l_root, task):
    l_root.setHpr(l_root.getHpr() + Vec3(30, 10, 0) * globalClock.getDt())
    return task.cont
    
def setup_FBR(c_mask):
    winprops = WindowProperties()
    winprops.setSize(base.win.getXSize(), base.win.getYSize())
    props = FrameBufferProperties()
    props.setRgbColor(1)
    props.setDepthBits(24)
    props.setAlphaBits(1)
    #props.setAuxRgba(1)
    ldepthmap = Texture()
    ldepthmap.setFormat( Texture.FDepthComponent )
    #ldepthmap.setComponentType( Texture.TFloat )
    #mybuffer = base.win.makeTextureBuffer("My Buffer", 
    #                                      base.win.getXSize(), 
    #                                      base.win.getYSize(), 
    #                                      to_ram = False, 
    #                                      tex = ldepthmap, 
    #                                      fbp = props)
    mybuffer=base.graphicsEngine.makeOutput(
        base.win.getPipe(), "My Buffer", -1,
        props, winprops, GraphicsPipe.BFRefuseWindow | GraphicsPipe.BFResizeable,
        base.win.getGsg(), base.win)
    mybuffer.setClearColor(Vec4(1,1,1,0)) 
    mybuffer.setSort(-100)
    #mycamera = base.makeCamera(mybuffer, scene = root)
    mycamera = base.makeCamera(mybuffer)
    cs = NodePath('tmp')
    cs.setState(mycamera.node().getInitialState())
    cs.setAttrib(AuxBitplaneAttrib.make(AuxBitplaneAttrib.ABOAuxNormal))
    mycamera.node().setInitialState(cs.getState())    
    mycamera.node().setLens(base.cam.node().getLens())
    mycamera.reparentTo(camera)
    mycamera.node().setCameraMask(c_mask)
    mybuffer.addRenderTexture(ldepthmap,
                              GraphicsOutput.RTMBindOrCopy,
                              GraphicsOutput.RTPDepth)
    ccolormap = Texture()
    mybuffer.addRenderTexture(ccolormap,
                              GraphicsOutput.RTMBindOrCopy,
                              GraphicsOutput.RTPColor)
    #normalmap = Texture()
    #normalmap.setFormat( Texture.FRgb )
    #mybuffer.addRenderTexture(normalmap, 
    #                          GraphicsOutput.RTMBindOrCopy, 
    #                          GraphicsOutput.RTPAuxRgba0)
    return ccolormap, ldepthmap
    
def l_depth_calc_FBR(c_mask, sort = -200):
    props = FrameBufferProperties()
    props.setRgbColor(0)
    props.setDepthBits(24)
    props.setAlphaBits(0)
    #props.setAuxRgba(1)
    ldepthmap = Texture()
    ldepthmap.setFormat( Texture.FDepthComponent )
    #ldepthmap.setComponentType( Texture.TFloat )
    mybuffer = base.win.makeTextureBuffer("My Buffer", 
                                          base.win.getXSize(), 
                                          base.win.getYSize(), 
                                          to_ram = False, 
                                          tex = ldepthmap, 
                                          fbp = props)
    #mybuffer = base.win.makeTextureBuffer("My Buffer 2", 
    #                                       base.win.getXSize(), 
    #                                       base.win.getYSize())
    mybuffer.setClearColor(Vec4(1,1,1,1))
    mybuffer.setSort(sort)
    mycamera = base.makeCamera(mybuffer)
    tempnode = NodePath(PandaNode("temp node"))
    #tempnode.setShader(loader.loadShader("normals.sha"), 1)
    tempnode.setShader(loader.loadShader("linear_depth.sha"), 1)
    tempnode.setShaderInput('cam', mycamera)
    #tempnode.setShaderInput('light', light)
    mycamera.node().setInitialState(tempnode.getState())
    mycamera.node().setLens(base.cam.node().getLens())
    mycamera.reparentTo(camera)
    mycamera.node().setCameraMask(c_mask)
    return ldepthmap#mybuffer.getTexture()
    

class CloudFilter():
    def __init__(self):
        self.rot_np = NodePath('rotator')
        self.finalquad = None
        taskMgr.add(self.rotator, 'rotator task')
        
    def make_filter(self, ccolor, cdepth, distort):
        manager = FilterManager(base.win, base.cam)
        mcolor = Texture()
        mdepth = Texture()
        ssao = Texture()
        mdepth.setFormat( Texture.FDepthComponent24 )
        mdepth.setComponentType( Texture.TFloat )
        #blured_ccolor = Texture()
        finalquad = manager.renderSceneInto(colortex = mcolor, depthtex = mdepth)
        #finalquad = manager.renderSceneInto(colortex = mcolor)
        
        interquad = manager.renderQuadInto(colortex=ssao)
        interquad.setShader(Shader.load("ssao.sha"))
        interquad.setShaderInput("cdepth", cdepth)
        interquad.setShaderInput("maindepth", mdepth)
        interquad.setShaderInput("noise", loader.loadTexture('noise.png'))
        
        finalquad.setShader(Shader.load("cloud_shader.sha"))
        finalquad.setShaderInput("color", mcolor)
        finalquad.setShaderInput("ccolor", ccolor)
        finalquad.setShaderInput("cdepth", cdepth)
        finalquad.setShaderInput("maindepth", mdepth)
        finalquad.setShaderInput("ssao", ssao)
        finalquad.setShaderInput("distort", distort)
        finalquad.setShaderInput("rotation", self.rot_np.getMat())
        self.finalquad = finalquad

    def rotator(self, task):
        if self.finalquad:
            self.rot_np.setR(self.rot_np, 10 * globalClock.getDt())
            self.finalquad.setShaderInput("rotation", self.rot_np.getMat())
        return task.cont

# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
tempnode = NodePath(PandaNode("temp node"))
tempnode.setShaderAuto()
base.cam.node().setInitialState(tempnode.getState())
base.cam.node().setCameraMask(MAIN_MASK)
base.cam.node().getLens().setNearFar(1,100)
# We need two separate NodePath - for our scene and for the particles
# to render them at different cameras
particles_root = NodePath('particles')
particles_root.reparentTo(render)
scene_root = NodePath('scene')
scene_root.reparentTo(render)
particles_root.hide(MAIN_MASK)
particles_root.show(CLOUD_MASK)
scene_root.hide(CLOUD_MASK)

# Make geom particles to make volumetric smoke
base.enableParticles()
p = ParticleEffect()
p.loadConfig('geom2.ptf')
p.start(parent = particles_root, renderParent = particles_root)

# Make scene
#base.setBackgroundColor(100, 0, 0)
back = loader.loadModel('test_scene')
back.setScale(5)
back.reparentTo(scene_root)
for i in range(5):
    box = loader.loadModel('box')
    box.reparentTo(scene_root)
    box.setPos(random.randrange(-2,2), 
                random.randrange(-2,2), 
                random.randrange(0,2))
sm = loader.loadModel('teapot')
sm.reparentTo(scene_root)
sm.setPos(-2, 2, 0)
sm.setScale(0.5)

# Setup lights
l_root = setup_lights(render)
l_root.setZ(5)
#taskMgr.add(light_task, 'light rotation', extraArgs = [l_root,], appendTask=True)
#render.setShaderAuto()

# Make framebuffer and filter
ccolor, cdepth = setup_FBR(CLOUD_MASK)
#mdepth = l_depth_calc_FBR(MAIN_MASK)
#cdepth2 = l_depth_calc_FBR(CLOUD_MASK)
cf = CloudFilter()
cf.make_filter(ccolor, cdepth, loader.loadTexture('dist5.png'))

#print l_root.find('**/PLight')
base.bufferViewer.toggleEnable()
run()
