from pandac.PandaModules import loadPrcFileData, TextNode
from pandac.PandaModules import Texture, Vec3, Point3, Vec4
from direct.interval.IntervalGlobal import Sequence
import demobase
from shadowManager2 import ShadowManager

class Shadow2Demo(demobase.DemoBase):
    """
    Shadow - Shadow Manager Test 2
    Soft Shadow from ..
    """
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

    def changeLightPos(self, object):
        if self.sMgr.IsOK():
            self.sMgr.changeLightPos(self.att_lightpos.getValue(), self.teapot.getPos())
        #v = self.att_lightpos.getValue()
        #self.sMgr.castercam.setPos(v[0],v[1],v[2])
        #self.sMgr.castercam.lookAt(self.teapot)

    def changeParams(self, object):
        if self.sMgr.IsOK():
            fov = self.att_fov.v
            #self.sMgr.castercam.node().getLens().setFov(fov)
            self.sMgr.setFov(fov)
            self.sMgr.setHardness(self.att_hardness.v)   # values so it was kinda unnecessary to

    def InitScene(self):
        self.textnode = render2d.attachNewNode("textnode")
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)

        self.att_animation = demobase.Att_Boolean(False, "Animation", True)
        self.att_animation.setNotifier(self.setAnimation)

        self.att_lightpos = demobase.Att_Vecs(False, "Shadow:Light Position", 3, (0,20,15), -20, 50)
        self.att_lightpos.setNotifier(self.changeLightPos)
        self.att_fov = demobase.Att_FloatRange(False, "Shadow:Fov", 10.0, 200.0, 40.0, 0)
        self.att_fov.setNotifier(self.changeParams)
        self.att_hardness = demobase.Att_FloatRange(False, "Shadow:Hardness", 0, 1, 0.2)
        self.att_hardness.setNotifier(self.changeParams)

        self.parent.Accept("v", base.bufferViewer.toggleEnable)
        self.LoadModel()

        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambinentLight.setLight(render)
        #self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.4, .4, .4, 1 ),  Vec3( 1, 1, -2 ))
        #self.att_directionalLight.setLight(render)
        pos = self.att_lightpos.getValue()
        lookat = self.teapot.getPos()
        fov = self.att_fov.v
        self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( 0.7, 0.7, 0.7, 1 ), 88, fov, pos, lookat, attenuation=Vec3( 0.4, 0.0, 0.0 ))
        self.att_spotLight.setLight(render)

        #return
        # Initiate the shadows
        self.sMgr = ShadowManager(render)
        if self.sMgr.IsOK():
            self.changeLightPos(None)
            self.changeParams(None)
            #self.sMgr.castercam.node().showFrustum() # Show the frustrum
            self.sMgr.showFrustum()
        else:
            demobase.addInstructions(0,-0.5, "Your hardware is not powerful enough to run this demo", align=TextNode.ACenter, node=self.textnode)

    def LoadModel(self):
        # Create the 'table'
        self.table = loader.loadModel("models/tableplane.egg")
        self.table.reparentTo(render)
        tableTex = loader.loadTexture("models/tree-bark-89a.jpg")
        tableTex.setMinfilter(Texture.FTLinearMipmapLinear) # Enable texture mipmapping
        self.table.setTexture(tableTex)
##        self.table = loader.loadModel("models/ebox.egg")
##        self.table.reparentTo(render)
##        self.table.setScale(20,20,1)

        # Load the teapot
        self.teapot = loader.loadModel("models/teapot")
        #self.teapot = loader.loadModel("models/ball")
        #self.teapot.setScale(3)
        self.teapot.setPos(0,0,0.5)
        self.teapot.setColor(1,1,0.5,1)
        self.teapot.setTwoSided(True)
        self.teapot.reparentTo(render)

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


    def ClearScene(self):
        base.bufferViewer.enable(False)

        self.sequence.pause()
        self.interval.pause()
        self.interval2.pause()

        self.textnode.removeNode()
        base.camera.detachNode()
        self.sMgr.Destroy()

        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)


