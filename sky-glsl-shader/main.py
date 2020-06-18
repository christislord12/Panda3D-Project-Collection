from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)

        self.skydome = loader.loadModel('skydome2')
        self.skydome.reparentTo(render)
#self.skydome.setPos(256, 256, -200)
#  self.skydome.setScale(10)
        self.skydome.setShaderInput("sky", Vec4(0.4,0.6,1.0, 1.0))
        self.skydome.setShaderInput("fog", Vec4(0,0,0, 0))
        self.skydome.setShaderInput("cloudColor", Vec4(0.9,0.9,1.0, 0.8))
        self.skydome.setShaderInput("cloudTile",8.0)
        self.skydome.setShaderInput("cloudSpeed",0.08)
        self.skydome.setShaderInput("horizont",20.0)
        self.skydome.setShaderInput("sunColor",Vec4(0.25, 0.5, 1, 0))
        self.skydome.setShaderInput("skyColor",Vec4(1.0,1.0,1.0, 1.0))
        self.skydome.setShaderInput("sunpos",Vec4(1.0,1.0,1.0, 1.0))
        self.skydome.setBin('background', 1)
        self.skydome.setTwoSided(True)
        self.skydome.node().setBounds(OmniBoundingVolume())
        self.skydome.node().setFinal(1)
        self.skydome.setShader(Shader.load(Shader.SLGLSL, "cloud_v.glsl", "cloud_f.glsl"))
        #self.skydome.hide(MASK_SHADOW)
        self.skydome.setTransparency(TransparencyAttrib.MNone, 1)
app = MyApp()
app.run()