# -*- coding: utf_8 -*-
from panda3d.core import *
loadPrcFileData("", "show-frame-rate-meter #t")
import direct.directbase.DirectStart
from direct.particles.ParticleEffect import ParticleEffect
from direct.filter.FilterManager import FilterManager

loadPrcFileData("", "prefer-parasite-buffer #t")

# Test scene (some models + fire perticles)
# Nothing special
def make_test_scene():
    #base.setBackgroundColor(0,0,0)
    scene = loader.loadModel('test_scene')
    scene.reparentTo(render)
    scene.setScale(3)
    scene.setShaderAuto()

    sm = loader.loadModel('smiley')
    sm.reparentTo(render)
    sm.setScale(0.5)


    box = loader.loadModel('box')
    box.reparentTo(render)
    box.setPos(2, -2, 0)

    pv = ParticleEffect()
    pv.loadConfig('ptf/smoke.ptf')
    pv.start(render)
    pv.setPos(0, 0, 0)
    pv.setDepthWrite(False)
    pv.setBin("fixed", 0)
    ps = ParticleEffect()
    ps.loadConfig('ptf/spark.ptf')
    ps.start(render)
    ps.setPos(0, 0, 0)
    ps.setScale(3)
    ps.setLightOff()
    pf = ParticleEffect()
    pf.loadConfig('ptf/fire.ptf')
    pf.start(render)
    pf.setPos(0, 0, 0.5)
    pf.setLightOff()
    pf.setDepthWrite(False)
    pf.setBin("fixed", 0)
    pf.setScale(0.6)
    
def setup_lights(root):
    ambientLight = AmbientLight("ambientLight")
    ambientLight.setColor(Vec4(.6, .6, .5, 1))
    directionalLight = DirectionalLight("directionalLight")
    directionalLight.setDirection(Vec3( 0, 8, -2.5 ) )
    directionalLight.setColor(Vec4( 0.9, 0.8, 0.9, 1 ) )
    root.setLight(root.attachNewNode(directionalLight))
    root.setLight(root.attachNewNode(ambientLight))


# ------------------- Setup the Heat Haze effect -----------------------

# Setup camera and frame buffer for the heat particles
# root - NodePath for the camera and particles (usually not under render)
def setup_FBR(root):
    ldepthmap = Texture()
    ldepthmap.setFormat( Texture.FDepthComponent )
    #ldepthmap.setComponentType( Texture.TFloat ) 
    props = FrameBufferProperties()
    props.setRgbColor(1)
    props.setDepthBits(1)
    mybuffer = base.win.makeTextureBuffer("My Buffer", 
                                          base.win.getXSize(), 
                                          base.win.getYSize(), 
                                          to_ram = False, 
                                          tex = ldepthmap, 
                                          fbp = props)
    mybuffer.setClearColor(Vec4(0,0,0,1)) 
    mybuffer.setSort(-100)
    mycamera = base.makeCamera(mybuffer, scene = root)
    mycamera.reparentTo(camera)
    
    distortmap = Texture()
    mybuffer.addRenderTexture(distortmap,
       GraphicsOutput.RTMBindOrCopy,
       GraphicsOutput.RTPColor)
    
    return distortmap, ldepthmap

# Post-process filter for final image
# dist - distortion texture from heat particles camera
# depth - depth texture from heat particles camera
# mcolor - color texture from main camera
# mdepth - depth texture from main camera
def filter(dist, depth):
    manager = FilterManager(base.win, base.cam)
    mcolor = Texture()
    mdepth = Texture()
    finalquad = manager.renderSceneInto(colortex = mcolor, depthtex = mdepth)
    finalquad.setShader(Shader.load("heat_shader.sha"))
    finalquad.setShaderInput("color", mcolor)
    finalquad.setShaderInput("distort", dist)
    finalquad.setShaderInput("depth", depth)
    finalquad.setShaderInput("maindepth", mdepth)


base.enableParticles()
make_test_scene()

setup_lights(render)

# root for the heat particles and camera - not under base render
heat_root = NodePath('heat particles root')

filter(*setup_FBR(heat_root))

# add heat particles
p = ParticleEffect()
p.loadConfig('ptf/heat.ptf')
p.start(parent = heat_root, renderParent = heat_root)
p.setPos(0, 0, 0)


#base.bufferViewer.toggleEnable()
base.mouseInterfaceNode.setY(20)
run()
