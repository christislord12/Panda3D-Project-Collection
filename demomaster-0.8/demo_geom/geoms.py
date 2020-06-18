
#from random import randint, random
import math, sys
import demobase, camerabase, geomutil, sheet

from pandac.PandaModules import Filename
from direct.gui.OnscreenText import OnscreenText

from pandac.PandaModules import NodePath, WindowProperties
from pandac.PandaModules import TextNode
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Shader, Texture, TextureStage, ShaderPool
from direct.interval.LerpInterval import LerpFunc



####################################################################################################################
class ShaderShapeDemo(demobase.DemoBase):
    """
    Geometry - Create various geometries
    Testing of creating geometries dynamically
    Code from: http://panda3d.org/phpbb2/viewtopic.php?t=5558
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)


    def InitScene(self):
        base.setBackgroundColor(0.0, 0.0, 0.0)
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", True)
        self.textnode = render2d.attachNewNode("textnode")

        self.LoadModels()
        self.LoadLights()
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control", \
                     [-100,-100,-100], [100,100,100], [-45,45, -17], [0,0,45],
                     Vec3(48,-48,21),
                     rate=0.2)
        self.parent.Accept("escape", self.att_cameracontrol.Stop)
        self.parent.Accept("enter", self.att_cameracontrol.Resume)
        self.att_cameracontrol.Stop()

    	demobase.addInstructionList(-1,0.95,0.05,
"""Press ESC to release mouse, Enter to resume mouse control
Move mouse to rotate camera
Left mouse button: Move forwards
Right mouse button: Move backwards""",node=self.textnode)

        #taskMgr.add(self.timer, 'mytimer')

    #def timer(self, task):
    #    render.setShaderInput('time', task.time)
    #    return task.cont

    def LoadLights(self):
        self.lightpivot = render.attachNewNode("lightpivot")
        self.lightpivot.setPos(0,0,10)
        self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()

        self.att_pointLight = demobase.Att_pointLightNode(False, "Light:Point Light",  \
                Vec4( 1, 1, 1, 1 ), Vec3(10,0,0),
                attenuation=Vec3( 0.1, 0.05, 0.0 ), ##attenuation=Vec3( 0.1, 0.04, 0.0 ),
                node=self.lightpivot, fBulb=True)
        self.att_pointLight.setLight(render)
        #self.att_pointLight.setLightOn(None, True)
        #self.att_pointLight.setPosition(None, Vec3(0,0,10))

        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.2, .2, .2, 1 ))
        self.att_ambientLight.setLight(render)

    def LoadModels(self):
        self.surface = None

    def Reset(self):
        if self.surface != None:
            self.surface.removeNode()
            self.surface = None

    def Demo01(self):
        """Create flat plane of 15x15 grids"""
        self.Reset()
        self.surface = geomutil.createPlane('myplane',20,40,15,15)
        self.surface.reparentTo(render)
        wood = loader.loadTexture("models/wood.png")
        wood.setWrapU(Texture.WMClamp)
        wood.setWrapV(Texture.WMClamp)
        self.surface.setTexture(wood)


    def Demo02(self):
        """Create curve surface from NurbsSurfaceEvaluator"""
        self.Reset()
        vKnot = uKnot = [0,0,0,0,1,1,1,1]
        #vKnot = uKnot = None
        surface = sheet.Sheet("curve")
        verts = [
                 {'node':None, 'point': (-7.5, -8., 0.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (-5., -8.3,- 3.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (5., -8.3,- 3.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (7.5, -8, 0.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (-9.8, -2.7, 3.), 'color' : (0,0.5,0,0)} ,
                 {'node':None, 'point': (-5.3, -7.2, -3.), 'color' : (0,0.5,0,0)} ,
                 {'node':None, 'point': (5.3, -7.2, -3.), 'color' : (0,1,0,0)} ,
                 {'node':None, 'point': (9.8, -2.7, 3.), 'color' : (0,1,0,0)} ,
                 {'node':None, 'point': (-11., 4.0, 3.), 'color' : (0,1,0,0)} ,
                 {'node':None, 'point': (-6., -1.8, 3.), 'color' : (0,1,0,0)} ,
                 {'node':None, 'point': (6., -1.8, 3.), 'color' : (0,0.5,0,0)} ,
                 {'node':None, 'point': (11, 4.0, 3.), 'color' : (0,0.5,0,0)} ,
                 {'node':None, 'point': (-9.5, 9.5, -3.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (-7., 7.8, 3.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (7., 7.8, 3.), 'color' : (0,0,0,0)} ,
                 {'node':None, 'point': (9.5, 9.5, -3.), 'color' : (0,0,0,0)} ,
                 ]
        surface.setup(4,4,4, verts, uKnot, vKnot)
        surface.sheetNode.setNumUSubdiv(16)
        surface.sheetNode.setNumVSubdiv(16)
        surface.flattenStrong()
        surface.setScale(1.3)
        surface.reparentTo(render)
        self.surface = surface

    def Demo03(self):
        """Create Colored Cube"""
        self.Reset()
        self.surface = geomutil.createCube()
        self.surface.setScale(4)
        self.surface.reparentTo(render)


    def Demo04(self):
        """Create Wedge from Egg interface"""
        self.Reset()
        wedge = geomutil.makeEggWedge(270,30)
        wedge.reparentTo(render)
        wedge.setScale(10)
        #wedge.setTwoSided(True)
        self.surface = wedge

    def Demo05(self):
        """Create Grid plane from Egg interface"""
        self.Reset()
        plane = geomutil.makeEggPlane(20, 40, 15, 15)
        plane.reparentTo(render)
        #plane.setTwoSided(True)
        self.surface = plane
        wood = loader.loadTexture("models/wood.png")
        wood.setWrapU(Texture.WMClamp)
        wood.setWrapV(Texture.WMClamp)
        self.surface.setTexture(wood)
#        render.analyze()

    def Demo06(self):
        """Draw Arc"""
        self.Reset()
        arc = geomutil.makeArc(270, 30)
        arc.reparentTo(render)
        arc.setScale(20,20,1)
        self.surface = arc
        self.surface.setLightOff()

    def ClearScene(self):
        if hasattr(self, "interval"):
            self.interval.pause()
        self.textnode.removeNode()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)

