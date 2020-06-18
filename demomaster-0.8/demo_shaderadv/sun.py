
import demobase, camerabase

from pandac.PandaModules import Filename
from pandac.PandaModules import NodePath, WindowProperties, ConfigVariableBool
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3

from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool, TexGenAttrib
from direct.filter.FilterManager import FilterManager
from direct.filter.CommonFilters import CommonFilters

####################################################################################################################
class SunShaderDemo(demobase.DemoBase):
    """
    Shaders - Sun
    Sun Shader - reference http://www.mathematik.uni-marburg.de/~menzel/index.php?seite=tutorials
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0, 0, 0)

        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()

        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-59,-59,-45], [59,59,45], [-45,45, 0], [0,0,0], Vec3(0,-15,0), rate=0.2)
        self.att_cameracontrol.DefaultController()
    	#demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)
        self.att_cameracontrol.Stop()

        taskMgr.add(self.timer, "timer")

    def LoadModels(self):
        self.sun2 = loader.loadModel("models/sphere")
        self.sun2.reparentTo(render)
        self.sun2.setScale(0.9)

        # Check video card capabilities.
        self.filters = None
        if ConfigVariableBool("basic-shaders-only").getValue():
             self.parent.MessageBox("Sun Shader Demo",
                    "This demonstration uses advance shader technique, which need to set the basic-shaders-only option to #f\nTo run this demo you need a powerful video card, and run demomaster by:\ndemomaster.py f\n"
             )
        elif (base.win.getGsg().getSupportsBasicShaders() == 0):
            self.addTitle("Filter: Video driver reports that shaders are not supported.")
        else:
            self.filters = CommonFilters(base.win, base.cam)
            #self.filters.setVolumetricLighting(self.sun2,32,0.5,1.0,0.05)
            self.filters.setVolumetricLighting(self.sun2,32,0.7,0.99,0.05)


        self.sun = loader.loadModel("models/sphere")
        self.sun.reparentTo(render)
        self.tex1 = [
            loader.loadTexture("textures/sunlayer1.png"),
            loader.loadTexture("textures/sunlayer1n.png"),
        ]
        self.tex2 = [
            loader.loadTexture("textures/sunlayer2.png"),
            loader.loadTexture("textures/sunlayer2n.png")
        ]
        self.index1 = 0
        self.index2 = 0

        tex3 = loader.loadTexture("textures/FireGradient.png")
        self.sun.setShaderInput("tex1", self.tex1[0])
        self.sun.setShaderInput("tex2", self.tex2[0])
        self.sun.setShaderInput("fire", tex3)
        shader = loader.loadShader("shaders/sun.sha")
        self.sun.setShader(shader)
        #self.setBloomShader()

##    def setBloomShader(self):
##        self.manager = FilterManager(base.win, base.cam)
##        self.quadlist = []
##        src1 = None
##        tex1 = Texture()
##        finalquad = self.manager.renderSceneInto(colortex=tex1)
##
##        tex2 = Texture()
##        interquad = self.manager.renderQuadInto(colortex=tex2)
##        interquad.setShaderInput("src", tex1)
##
##        sha = loader.loadShader("shaders/blur1.sha")
##        interquad.setShader(sha)
##        interquad.setShaderInput("src", tex1)
##        interquad.setShaderInput("param1", 0.015)
##
##        self.quadlist.append(interquad)
##        src1 = tex1
##        tex1 = tex2
##
##        sha = loader.loadShader("shaders/bloom2.sha")
##        finalquad.setShader(sha)
##        finalquad.setShaderInput("src", tex1)
##        finalquad.setShaderInput("src1", src1)
##        finalquad.setShaderInput("param1", Vec4(1.8,1,0,0))
##        self.quadlist.append(finalquad)

    def ClearScene(self):
        if self.filters:
            taskMgr.remove("common-filters-update")
            self.filters.cleanup()

##        if False:
##            self.manager.cleanup()
##            self.manager = None
##            for quad in self.quadlist:
##                quad.clearShader()

        self.sun.clearShader()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def timer(self, task):
        self.sun.setShaderInput("time", task.time)
        return task.cont

    def Demo01(self):
        """Toggle texture 1 noise"""
        self.index1 = (self.index1 + 1) % 2
        self.sun.setShaderInput("tex1", self.tex1[self.index1])

    def Demo02(self):
        """Toggle texture 2 noise"""
        self.index2 = (self.index2 + 1) % 2
        self.sun.setShaderInput("tex2", self.tex2[self.index2])
