import demobase, camerabase
from pandac.PandaModules import NodePath,Vec3,Vec4,TextureStage,TexGenAttrib

class SkyDome1(demobase.Att_base):
    def __init__(self, scene, rate=(0.05,0.05),
            texturescale=(10,10),
            scale=(4000,4000,1000), texturefile=None):
        demobase.Att_base.__init__(self,False, "Sky Dome 1")
        self.skybox = loader.loadModel("models/dome1")
        self.skybox.setTwoSided(True)
        self.skybox.setScale(scale[0],scale[1],scale[2])
        self.skybox.setLightOff()
        if texturefile == None:
            texturefile = "textures/clouds.jpg"
        texture = loader.loadTexture(texturefile)
        self.textureStage0 = TextureStage("stage0")
        self.textureStage0.setMode(TextureStage.MReplace)
        self.skybox.setTexture(self.textureStage0,texture,1)
        self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

        self.skybox.reparentTo(scene)
        self.rate = rate
        self.textureScale = texturescale

        taskMgr.add(self.shiftTextureTask,"skycloudsshifttask" )

    def shiftTextureTask(self, task):
        offsetx = (task.time * self.rate[0]) % 1.0
        offsety = (task.time * self.rate[1]) % 1.0
        self.skybox.setTexOffset(self.textureStage0, offsetx, offsety)
        return task.cont

    def setRate(self, rate):
        self.rate = rate

    def setTextureScale(self, texturescale):
        self.skybox.setTexScale(self.textureStage0, texturescale[0], texturescale[1])

    def Destroy(self):
        self.skybox.removeNode()
        taskMgr.remove("skycloudsshifttask")

    def setPos(self, v):
        self.skybox.setPos(v)

    def show(self):
        self.skybox.show()

    def hide(self):
        self.skybox.hide()

    def setStandardControl(self):
        self.att_rate_x = demobase.Att_FloatRange(False, "Speed X", -1.0, 1.0, self.rate[0], 3)
        self.att_rate_y = demobase.Att_FloatRange(False, "Speed Y", -1.0, 1.0, self.rate[1], 3)
        self.att_scale_x = demobase.Att_FloatRange(False, "Tex-scale X", 0.01, 100.0, self.textureScale[0], 2)
        self.att_scale_y = demobase.Att_FloatRange(False, "Tex-scale Y", 0.01, 100.0, self.textureScale[1], 2)
        self.att_rate_x.setNotifier(self.skyboxratechange)
        self.att_rate_y.setNotifier(self.skyboxratechange)
        self.att_scale_x.setNotifier(self.skyboxscalechange)
        self.att_scale_y.setNotifier(self.skyboxscalechange)

    def skyboxratechange(self, object):
        self.setRate((self.att_rate_x.v, self.att_rate_y.v))

    def skyboxscalechange(self,object):
        self.setTextureScale((self.att_scale_x.v, self.att_scale_y.v))

