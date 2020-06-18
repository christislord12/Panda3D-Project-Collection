from panda3d.core import *
import direct.directbase.DirectStart
from direct.filter.FilterManager import FilterManager

loadPrcFileData("", "prefer-parasite-buffer #t")


def filter():
    base.setBackgroundColor(0,0,0)
    # ATI video cards (or drivers) are not too frendly with the input 
    # variables, so I had to transfer most of parameters to the shader
    # code.

    # Threshold (x,y,z) and brightness (w) settings
    threshold = Vec4(0.4, 0.4, 0.4, 1.0) # <----
    
    # FilterManager
    manager = FilterManager(base.win, base.cam)
    tex1 = Texture()
    tex2 = Texture()
    tex3 = Texture()
    finalquad = manager.renderSceneInto(colortex=tex1)
    # First step - threshold and radial blur
    interquad = manager.renderQuadInto(colortex=tex2)
    interquad.setShader(Shader.load("invert_threshold_r_blur.sha"))
    interquad.setShaderInput("tex1", tex1)
    interquad.setShaderInput("threshold", threshold)
    # Second step - hardcoded fast gaussian blur. 
    # Not very important. This step can be omitted to improve performance
    # with some minor changes in lens_flare.sha
    interquad2 = manager.renderQuadInto(colortex=tex3)
    interquad2.setShader(Shader.load("gaussian_blur.sha"))
    interquad2.setShaderInput("tex2", tex2)
    # Final - Make lens flare and blend it with the main scene picture
    finalquad.setShader(Shader.load("lens_flare.sha"))
    finalquad.setShaderInput("tex1", tex1)
    finalquad.setShaderInput("tex2", tex2)
    finalquad.setShaderInput("tex3", tex3)
    #lf_settings = Vec3(lf_samples, lf_halo_width, lf_flare_dispersal)
    #finalquad.setShaderInput("lf_settings", lf_settings)
    #finalquad.setShaderInput("lf_chroma_distort", lf_chroma_distort)

# Just made a scene. There have not any special settings.
from scene import make_scene
make_scene()

base.mouseInterfaceNode.setY(350)

filter()

#base.bufferViewer.toggleEnable()
run()

