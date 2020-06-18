from pandac.PandaModules import loadPrcFileData, TextureStage
from pandac.PandaModules import Texture, Vec3, Point3, Vec4
from direct.interval.IntervalGlobal import Sequence
import demobase

class SceneDemo(demobase.DemoBase):
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)
        #loadPrcFileData("", "prefer-parasite-buffer #f")


    def setAnimation(self, object):
        if self.att_animation.v:
            self.interval.loop()
            self.interval2.loop()
            self.sequence.loop()
        else:
            self.interval.pause()
            self.interval2.pause()
            self.sequence.pause()

    def InitScene(self):
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)

        self.att_animation = demobase.Att_Boolean(False, "Animation", True)
        self.att_animation.setNotifier(self.setAnimation)

        #self.att_lightpos = demobase.Att_Vecs(False, "Shadow:Light Position", 4, (0,20,15,0), -40, 40)
        #self.att_lightpos.setNotifier(self.changeLightPos)
        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 0.99, 0.96, 0.5, 1 ), Vec3(0,20,15),
                attenuation=Vec3( 0.1, 0.03, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=render,
                fBulb=True)
        self.att_pointLight.setLight(render)
        self.LoadModel()
        self.SetShader()
        taskMgr.add(self.cameraUpdated, "camupdate")

    def cameraUpdated(self, task):
        self.changeParams(None)

        return task.cont

    def LoadModel(self):
        self.table = loader.loadModel("demo_softshadow/models/tableplane.egg")
        tableTex = loader.loadTexture("demo_softshadow/models/tree-bark-89a.jpg")
        tableTex.setMinfilter(Texture.FTLinearMipmapLinear) # Enable texture mipmapping
        self.table.setTexture(tableTex)
        self.table.reparentTo(render)


        self.modelnode = render.attachNewNode("models")
        # Load the teapot
        self.teapot = loader.loadModel("models/teapotuv")
        #self.teapot.setTwoSided(True)
        self.teapot.setPos(0,0,0)
        self.teapot.setColor(1,1,0.5,1)
        self.teapot.reparentTo(self.modelnode)
        self.teapot.setScale(3)

        nops = loader.loadTexture("models/nops.png")
        nops.setWrapU(Texture.WMRepeat)
        nops.setWrapV(Texture.WMRepeat)
        self.teapot.setTexture(nops, 1)


        self.interval = self.teapot.hprInterval(5.0, Vec3.zero(), Vec3(360, 0, 0))
        self.interval.loop()
        #self.sequence = Sequence(self.teapot.posInterval(2.0, Point3.zero(), Point3(2, 0, 1)), self.teapot.posInterval(2.0, Point3(2, 0, 1), Point3.zero()))
        self.sequence = Sequence(self.teapot.posInterval(2.0, Point3(0,0,5), Point3(2, 0, 1)), self.teapot.posInterval(2.0, Point3(2, 0, 1), Point3(0,0,5)))
        self.sequence.loop()

        # Setup the camera
        base.disableMouse()
        camPivot = render.attachNewNode("cameraPivotPoint")
        base.camera.reparentTo(camPivot)
        base.camera.setPos(-10,-10,15)
        base.camera.lookAt(self.teapot)

        base.camLens.setNearFar(1,1000)
        base.camLens.setFov(75)

        # Setup an interval to rotate the camera around camPivot
        self.interval2 = camPivot.hprInterval(15.0, Vec3.zero(), Vec3(360, 0, 0))
        self.interval2.loop()

    def ClearScene(self):
        #base.camera.reparentTo(render)
        taskMgr.remove("camupdate")

        self.modelnode.clearShader()
        self.sequence.pause()
        self.interval.pause()
        self.interval2.pause()

        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)
