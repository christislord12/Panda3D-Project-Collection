
from random import randint, random
import math, sys
import demobase, camerabase, geomutil, grass1

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties, Plane, PlaneNode, TransparencyAttrib
from pandac.PandaModules import TextNode, CardMaker
from pandac.PandaModules import Vec3,Vec4,Point3,Point2
from pandac.PandaModules import Shader, Texture, TextureStage
from direct.interval.LerpInterval import LerpFunc


import skydome1
####################################################################################################################
class Grass1Demo(demobase.DemoBase):
    """
    Nature - Grass Demo 1
    Testing of creating Tree and grass dynamically
    Some code from: http://panda3d.org/phpbb2/viewtopic.php?t=2385
    Theory: http://developer.nvidia.com/object/nature_scene.html
    Resources: http://blender-archi.tuxfamily.org/
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        #self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.textnode = render2d.attachNewNode("textnode")
        self.grasstextnode = demobase.addInstructions(-1.0,-0.9, "", align=TextNode.ALeft, node=self.textnode)

        self.LoadModels()
        self.LoadLights()
        self.SetupCamera()


    def SetupCamera(self):
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-500,-500,0], [500,500,100],
                     [-45,0, -9.5], [0,0,-52],
                     Vec3(-130,-93,46),
                     rate=0.5, speed=60)
        self.att_cameracontrol.DefaultController()
        self.att_cameracontrol.ShowPosition(self.textnode)
        self.att_cameracontrol.LockAt((0,0,20))
        #self.att_cameracontrol.Stop()

    	#demobase.addInstructionList(-1,0.95,0.05, self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        taskMgr.add(self.cameraUpdated, "camupdate")
        #taskMgr.add(self.timer, 'mytimer')

    #def timer(self, task):
    #    render.setShaderInput('time', task.time)
    #    return task.cont

    def LoadLights(self):
        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambientLight.setLight(render)


    def LoadSkyBox(self):
        self.att_skydome = skydome1.SkyDome1(render)
        self.att_skydome.setStandardControl()
        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def LoadModels(self):
        self.LoadSkyBox()

        self.att_space = demobase.Att_FloatRange(False,"Grass Spacing",1.0 ,30.0, 5.0, 1);

        self.ground = geomutil.createPlane('myplane',100,100,1,1)
        self.ground.reparentTo(render)
        #self.ground.setShaderAuto()
        #self.ground.setLightOff()

        #groundtex = loader.loadTexture("textures/grass.png")
        groundtex = loader.loadTexture("textures/dirt.png")
        self.ground.setTexture(groundtex)
        #self.ground.setTexScale(TextureStage.getDefault(), 100,100)
        self.ground.setTexScale(TextureStage.getDefault(), 10,10)
        self.att_grass = grass1.GrassNode("Grass")

        model1 = grass1.LeafModel("Green leaf 1", 2, 12.0,16.0, 'shaders/grass1.sha', 'textures/grassPack.png', [ (Point2(0,0.1),Point2(0.25,1)), (Point2(0.5,0.1),Point2(0.75,1))])
        #model1_2 = grass1.LeafModel("Green leaf 2", 2, 12.0, 24.0, 'shaders/grass1.sha', 'textures/grassPack_2.png', [ (Point2(0,0.1),Point2(0.25,1)), (Point2(0.5,0.1),Point2(0.75,1))])
        model2 = grass1.LeafModel("Brown leaf 1", 2, 12.0, 16.0, 'shaders/grass1.sha', 'textures/grassPack.png', [ (Point2(0.25,0.1),Point2(0.5,1)), (Point2(0.75,0.1),Point2(1,1))])
        #model3 = grass1.LeafModel("Brighter leaf", 2, 6.0, 6.0, 'shaders/grass1.sha', 'textures/grassWalpha.png', None)
        modeldebug = grass1.LeafModel("White debug leaf", 2, 6.0, 10.0, 'shaders/grass1.sha', 'textures/white.png', None)
        #modeldebug = grass1.LeafModel("White debug leaf", 2, 6.0, 10.0, 'shaders/grass1.sha', 'demo_human/textures/hair1.png', None)
        self.modellist = [model1, model2, modeldebug]
        self.model = 0
        self.randompos=True
        self.randomsize=False
        self.setModel()


        self.att_tree = grass1.GrassNode("Tree", color=Vec4(.9,.9,.9,1))
        modeltree1 = grass1.LeafModel("Tree 1", 3, 80.0, 50.0, 'shaders/grass1color.sha', 'textures/Flamboyant.png', None)
        modeltree2 = grass1.LeafModel("Tree 3", 4, 70.0, 60.0, 'shaders/grass1color.sha', 'textures/Lime2.png', None)
        modeltree3 = grass1.LeafModel("Tree 2", 3, 50.0, 50.0, 'shaders/grass1color.sha', 'textures/Bleech.png', None)
        self.modeltreelist = [ (modeltree1,Vec4(.9,.9,.9,1)), (modeltree2,Vec4(.9,.9,.9,1)), (modeltree3,Vec4(.6,.6,.6,1))]
        self.modeltree = 0
        self.setModelTree()

    def setModel(self):
        self.att_grass.setModel(self.modellist[self.model])
        self.grasstextnode.setText(self.modellist[self.model].name)
        self.LoadEven()

    def setModelTree(self):
        model = self.modeltreelist[self.modeltree]
        self.att_tree.setModel(model[0])
        self.att_tree.reset()
        self.att_tree.setColor(model[1])
        np = self.att_tree.addGrassWithModel(Vec3(-10,20,0), 0)

    def LoadEven(self):
        self.att_grass.reset()
        space = self.att_space.v
        x = -50 + space
        #x = 25 + space
        while x < 50 - space/2:
            y = -50 + space
            #y = 25 + space
            while y < 50 - space/2:
                if self.randompos:
                    x1 = x + random() * space - space/2
                    y1 = y + random() * space - space/2
                else:
                    x1 = x
                    y1 = y
                h = random() * 90.0
                np = self.att_grass.addGrassWithModel(Vec3(x1,y1,0), h)
                if self.randomsize:
                    size = random() * 0.5+0.5
                    np.setScale(size)
                y += space
            x += space
        self.att_grass.flatten()

    def changelight(self, object):
        pass

    def Demo01(self):
        """Toggle grass model"""
        self.model = (self.model + 1) % len(self.modellist)
        #self.randompos = False
        #self.randomsize = False
        self.setModel()
        self.changelight(None)

    def Demo02(self):
        """Reload with a bit random"""
        self.randompos = True
        self.randomsize = False
        self.LoadEven()
        self.changelight(None)

    def Demo03(self):
        """Reload with random size/pos"""
        self.randompos = True
        self.randomsize = True
        self.LoadEven()
        self.changelight(None)

    def Demo04(self):
        """Reload in regular"""
        self.randompos = False
        self.randomsize = False
        self.LoadEven()
        self.changelight(None)

    def Demo05(self):
        """Toggle Tree Model"""
        self.modeltree = (self.modeltree + 1) % len(self.modeltreelist)
        self.setModelTree()


    def ClearScene(self):
        taskMgr.remove("camupdate")

        if hasattr(self, "att_skydome"):
            self.att_skydome.Destroy()

        if self.att_grass:
            self.att_grass.Destroy()

        if hasattr(self, "att_tree"):
            self.att_tree.Destroy()

        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

    def cameraUpdated(self, task):
        campos = base.camera.getPos()
        render.setShaderInput('time', task.time)

        self.att_grass.setTime(task.time)
        if hasattr(self, "att_tree"):
            self.att_tree.setTime(task.time)

        return task.cont



