import demobase
from pandac.PandaModules import NodePath,Vec3,Vec4,TextureStage

class WaterfallDemo(demobase.DemoBase):
    """
    Nature - Waterfall effect
    From ThomasEgi http://panda3d.org/phpbb2/viewtopic.php?t=4722
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        base.setBackgroundColor(0.3, 0.3, 0.3)
        self.LoadModels()
        taskMgr.add(self.shiftTextureTask,"shifttask" )
        self.SetCameraPos(Vec3(5,3,5), Vec3(0,0,0))

    def LoadModels(self):
        self.waterfall = loader.loadModelCopy("models/box")
        self.waterfall.reparentTo(render)

        texture = loader.loadTexture("textures/waterfall.png")
        self.textureStage0 = TextureStage("stage0")
        self.textureStage0.setMode(TextureStage.MReplace)
        self.waterfall.setTexture(self.textureStage0,texture,1)
        self.waterfall.setTexScale(self.textureStage0, 2, 2)

        texture2 = loader.loadTexture("textures/waterfall.png")
        self.textureStage1 = TextureStage("stage1")
        self.textureStage1.setMode(TextureStage.MModulate)
        self.waterfall.setTexture(self.textureStage1,texture2,1)
        self.waterfall.setTexScale(self.textureStage1, 1, 1)

    def shiftTextureTask(self, task):
        self.waterfall.setTexOffset(self.textureStage0, 0, (task.time) % 1.0 )
        self.waterfall.setTexOffset(self.textureStage1, 0, (task.time*1.15) % 1.0 )
        return task.cont


    def ClearScene(self):
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

        taskMgr.remove("shifttask")