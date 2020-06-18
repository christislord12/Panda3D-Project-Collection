from pandac.PandaModules import loadPrcFileData, TextureStage
from pandac.PandaModules import Texture, Vec3, Point3, Vec4
from direct.interval.IntervalGlobal import Sequence
import demobase
from shadowManager import ShadowManager

class SoftShadowDemo(demobase.DemoBase):
    """
    Shadow - Shadow Manager from pro-rsoft
    Soft Shadow from pro-rsoft at http://panda3d.org/phpbb2/viewtopic.php?t=4337
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)
        #loadPrcFileData("", "prefer-parasite-buffer #f")


    def changeParams(self, object):
        self.sMgr.setAmbient(self.att_ambient.v)     # Most of these five are the default
        self.sMgr.setHardness(self.att_hardness.v)   # values so it was kinda unnecessary to
        self.sMgr.setFov(self.att_fov.v)            # set them explicitly but I wanted to
        if self.att_near.v < self.att_far.v:
            self.sMgr.setNearFar(self.att_near.v, self.att_far.v)               # show how to set them anyway.

    def setAnimation(self, object):
        if self.att_animation.v:
            self.interval.loop()
            self.interval2.loop()
            self.sequence.loop()
        else:
            self.interval.pause()
            self.interval2.pause()
            self.sequence.pause()

    def changeLightPos(self, object):
        v = self.att_lightpos.getValue()
        self.sMgr.light.setPos(v[0],v[1],v[2])
        self.sMgr.light.lookAt(self.teapot)
        #self.sMgr.light.lookAt(0,22,0)

    def InitScene(self):
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)

        self.att_animation = demobase.Att_Boolean(False, "Animation", True)
        self.att_animation.setNotifier(self.setAnimation)

        # control params for the shadow manager
        self.att_hardness = demobase.Att_IntRange(False, "Shadow:Hardness", 0, 100, 20)
        self.att_hardness.setNotifier(self.changeParams)
        self.att_ambient = demobase.Att_FloatRange(False, "Shadow:Ambient", 0.0, 1.0, 0.2)
        self.att_ambient.setNotifier(self.changeParams)
        self.att_fov = demobase.Att_FloatRange(False, "Shadow:Fov", 10.0, 200.0, 40.0, 0)
        self.att_fov.setNotifier(self.changeParams)
        self.att_near = demobase.Att_FloatRange(False, "Shadow:near", 5.0, 200.0, 10.0, 0)
        self.att_near.setNotifier(self.changeParams)
        self.att_far = demobase.Att_FloatRange(False, "Shadow:far", 5.0, 200.0, 100.0, 0)
        self.att_far.setNotifier(self.changeParams)
        self.att_lightpos = demobase.Att_Vecs(False, "Shadow:Light Position", 3, (0,20,15), -40, 40)
        self.att_lightpos.setNotifier(self.changeLightPos)

        # Initiate the shadows
        self.sMgr = ShadowManager(render)
        self.changeParams(None)

        self.parent.Accept("v", base.bufferViewer.toggleEnable)
        self.LoadModel()

    def LoadModel(self):
        # Create the 'table'
        #self.table = loader.loadModel("models/box.egg")
        #self.table.reparentTo(render)
        #self.table.setScale(20,20,1)
        #self.sMgr.flagUntexturedObject(self.table)
        self.table = loader.loadModel("models/tableplane.egg")
        tableTex = loader.loadTexture("models/tree-bark-89a.jpg")
        tableTex.setMinfilter(Texture.FTLinearMipmapLinear) # Enable texture mipmapping
        self.table.setTexture(tableTex)
        self.table.reparentTo(render)


        # Load the teapot
        self.teapot = loader.loadModel("models/teapot")
        self.teapot.setTwoSided(True)
        self.teapot.setPos(0,0,0.5)
        self.teapot.setColor(1,1,0.5,1)
        self.teapot.reparentTo(render)
        # The teapot has no texture, so you have to tell it to the ShadowManager
        # Otherwise the model will turn up black.
        self.sMgr.flagUntexturedObject(self.teapot)

        # Set intervals to move the teapot
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

        # Position the shadow camera
        #self.sMgr.light.setPos(0,20,15)
        self.changeLightPos(None)
        self.sMgr.light.node().showFrustum() # Show the frustrum


    def ClearScene(self):
        #base.camera.reparentTo(render)

        self.sequence.pause()
        self.interval.pause()
        self.interval2.pause()

        base.camera.detachNode()
        self.sMgr.Destroy()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)
