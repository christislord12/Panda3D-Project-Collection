import demobase, camerabase
from pandac.PandaModules import NodePath,Vec3,Vec4,TextureStage,TexGenAttrib

class SkyDome2(demobase.Att_base):
    def __init__(self, scene, rate=Vec4(0.004, 0.002, 0.008, 0.010),
                skycolor=Vec4(0.25, 0.5, 1, 0),
                texturescale=Vec4(1,1,1,1),
                scale=(4000,4000,1000),
                texturefile=None):
        demobase.Att_base.__init__(self,False, "Sky Dome 2")
        self.skybox = loader.loadModel("models/dome2")
        self.skybox.reparentTo(scene)
        self.skybox.setScale(scale[0],scale[1],scale[2])
        self.skybox.setLightOff()

        if texturefile == None:
            texturefile = "textures/clouds_bw.png"
        texture = loader.loadTexture(texturefile)
        self.textureStage0 = TextureStage("stage0")
        self.textureStage0.setMode(TextureStage.MReplace)
        self.skybox.setTexture(self.textureStage0,texture,1)
        #self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

        self.rate = rate
        self.textureScale = texturescale
        self.skycolor = skycolor
        self.skybox.setShader( loader.loadShader( 'shaders/skydome2.sha' ) )
        self.setShaderInput()

    def setRate(self, rate):
        self.rate = rate

    def setTextureScale(self, texturescale):
        self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

    def Destroy(self):
        self.skybox.clearShader()
        self.skybox.removeNode()

    def setPos(self, v):
        self.skybox.setPos(v)

    def show(self):
        self.skybox.show()

    def hide(self):
        self.skybox.hide()

    def setStandardControl(self):
        self.att_rate = demobase.Att_Vecs(False,"Cloud Speed",4,self.rate,-1,1,3)
        self.att_scale = demobase.Att_Vecs(False, "Tex-scale", 4, self.textureScale, 0.01, 100.0, 2)
        self.att_skycolor = demobase.Att_color(False, "Sky Color", self.skycolor)
        self.att_rate.setNotifier(self.changeParams)
        self.att_scale.setNotifier(self.changeParams)
        self.att_skycolor.setNotifier(self.changeParams)

    def changeParams(self, object):
        self.rate = self.att_rate.getValue()
        self.skycolor = self.att_skycolor.getColor()
        self.textureScale = self.att_scale.getValue()
        self.setShaderInput()

    #def skyboxscalechange(self,object):
    #    self.setTextureScale(self.att_scale.getValue())

    def setShaderInput(self):
        self.skybox.setShaderInput("sky", self.skycolor)
        self.skybox.setShaderInput("clouds", self.rate)
        self.skybox.setShaderInput("ts", self.textureScale)
