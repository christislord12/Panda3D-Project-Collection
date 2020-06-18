from random import randint, random
import math, sys, colorsys, threading
import demobase, camerabase
from pandac.PandaModules import Vec3,Vec4,Point3, TextNode, TextureStage, NodePath, VBase4
from direct.filter.CommonFilters import CommonFilters
from direct.interval.LerpInterval import LerpFunc
####################################################################################################################
class ShowShadersDemo(demobase.DemoBase):
    """
    Shaders - Show Models with various effects
    Shader effect by various models from http://panda3d.org/phpbb2/viewtopic.php?t=4006
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def SetupCamera(self):
        self.SetCameraPos(Vec3(0,-25,0), Vec3(0,0,0))

    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)

        self.textnode = render2d.attachNewNode("textnode")
        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()
        self.LoadFilter()
        #render.setShaderAuto()
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        #self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
        #             [-59,-59,5], [59,59,45], [-45,45, -17], [0,0,45], Vec3(8,-8,3), rate=0.2)
        #self.parent.Accept("escape", self.att_cameracontrol.Stop)
        #self.parent.Accept("enter", self.att_cameracontrol.Resume)
        #self.att_cameracontrol.Stop()
#        return

    def LoadLights(self):
        self.att_ambinentLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(0.2, 0.2, 0.2, 1 ))
        self.att_ambinentLight.setLight(render)
        self.att_directionalLight = demobase.Att_directionalLightNode(False, "Light:Directional Light", Vec4(.8, .8, .8, 1 ),  Vec3( 1, 1, 0 ))
        self.att_directionalLight.setLight(render)

    def LoadFilter(self):
        # Check video card capabilities.
        if (base.win.getGsg().getSupportsBasicShaders() == 0):
            self.addTitle("Glow Filter: Video driver reports that shaders are not supported.")
            return
        # Use class 'CommonFilters' to enable a bloom filter.
        # The brightness of a pixel is measured using a weighted average
        # of R,G,B,A.  We put all the weight on Alpha, meaning that for
        # us, the framebuffer's alpha channel alpha controls bloom.
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setBloom(blend=(0,0,0,1), desat=-0.5, intensity=3.0, size=1)

    def LoadModels(self):
        self.modellist = [
            "models/earthnobloom.egg","models/earthnormalnobloom.egg","models/earth.egg",
    		"models/earthnormal.egg","models/earthmod.egg","models/earthmod2.egg",
    		"models/earthmod3.egg","models/sunwhite.egg","models/sun.egg",
    		"models/earthgloss.egg","models/earthglossnormal.egg"]
        i = 0
        space = 4
        z = 2 * space
        self.intervals = []
        for m in self.modellist:
            if (i % 4) == 0:
                x = -1.5 * space
                z -= space
            else:
                x += space
            i+=1
            model = loader.loadModel(m)
            model.reparentTo(render)
            model.setPos(x,0,z)
            pos = Vec3(x,0,z)
            text = TextNode('node name')
            text.setTextColor(1, 1, 1, 1)
            text.setText(m[7:])
            tNode = render.attachNewNode(text)
            tNode.setPos( pos + Vec3(-1,0,-1.4) )
            tNode.setScale( 0.4 )
            #tNode.setHpr(0,-90,0)
            tNode.setShaderOff()
            tNode.setLightOff()

            iv = model.hprInterval(20,Point3(360,0,0))
            iv.loop()
            self.intervals.append(iv)
		#self.model.setShaderAuto()
		#self.model.setShaderInput("light", self.dlnp)


    def addTitle(self, title):
    	demobase.addInstructionList(0,-0.8,0.05,title,align=TextNode.ACenter,node=self.textnode)

    def ClearScene(self):
        self.filters.cleanup()
        for iv in self.intervals:
            iv.pause()

        self.textnode.removeNode()
        #self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)


    def animate(self, t):
        radius = 4.3
        angle = math.radians(t)
        c = (math.sin(angle) + 0.5)
        cr=VBase4( c, c, c, c)
        self.att_pointLight.setColor(None, cr)
        self.att_pointLight.att_bulb.setBulbColor(None, cr)

