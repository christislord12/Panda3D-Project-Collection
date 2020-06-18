
from random import randint, random
import math, sys
from math import pi, sin
import demobase, camerabase
from skydome1 import *

from pandac.PandaModules import GeoMipTerrain, Filename
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
#from pandac.PandaModules import PStatClient
#from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib
from direct.task.Task import Task

####################################################################################################################
class TerrainDemo(demobase.DemoBase):
    """
    GeoMipTerrain - Yarr
    It is all from Yarr
    """
    def __init__(self, parent):
        demobase.DemoBase.__init__(self, parent)

    def InitScene(self):
        #self.SetCameraPosHpr(0, -8, 2.5, 0, -9, 0)
        #base.setBackgroundColor(.6, .6, 1) #Set the background color
        self.att_shaderoption = demobase.Att_AutoShaderOption(False, "Shader:AutoShader", False)

        self.att_ambientLight = demobase.Att_ambientLightNode(False, "Light:Ambient Light", Vec4(.4, .4, .35, 1 ))
        self.att_ambientLight.setLight(render)
        self.att_ambientLight.setNotifier(self.changelight)
        self.att_directionalLight = demobase.Att_directionalLightNode(False,"Light:Directional Light",Vec4( .9, .8, .9, 1 ) ,Vec3( 0, 8, -2.5 ) )
        self.att_directionalLight.setLight(render)
        self.att_directionalLight.setNotifier(self.changelight)

        #self.att_spotLight = demobase.Att_spotLightNode(False, "Light:Spotlight",  Vec4( .45, .45, .45, 1 ), 16, 60.0, Vec3(0,0,0), Point3(0,0,0), attenuation=Vec3( 1, 0.0, 0.0 ), node=camera)
        #self.att_spotLight.setLight(render)
##        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
##                     [-20,-20,30], [20,20,100], [-89,89, -23], [0,0,-40],
##                     Vec3(0,0,50),
##                     rate=1.5)
        self.att_cameracontrol = camerabase.Att_CameraControllerByMouse(self.parent, False, "Camera:Camera Control",
                     [-200,-200,10], [200,200,100], [-89,89, -15], [0,0,-107],
                     Vec3(-22,94,30),
                     rate=1.5)
        self.att_cameracontrol.DefaultController()

        self.att_fogcolor = demobase.Att_color(False,"Fog:Color", Vec4(0.4,0.4,0.4,1))
        self.att_fogcolor.setNotifier(self.fogChange)
        self.att_fogdensity = demobase.Att_FloatRange(False,"Fog:Density",0,0.2,0.01,3)
        self.att_fogdensity.setNotifier(self.fogChange)
        self.att_fogEnable = demobase.Att_Boolean(False,"Fog:Enable Fog",False)
        self.att_fogEnable.setNotifier(self.fogChange)


        self.textnode = render2d.attachNewNode("textnode")
    	demobase.addInstructionList(-1,0.95,0.05,self.att_cameracontrol.GetDefaultInstruction(),node=self.textnode)

        self.att_multitexture = demobase.Att_Boolean(False, "Terrain:Multi-texture", True)
        self.att_multitexture.setNotifier(self.setMultiTexture)
        self.terrain = None
        self.LoadSkyBox()
        self.LoadModels()
        self.changelight(None)
        #self.att_cameracontrol.setNotifier(self.cameraUpdated)
        # create a new task instead of using camera control for callback
        # because the camera control task will be removed if user press escape to stop control
        taskMgr.add(self.cameraUpdated, "camupdate")

        self._setup_camera()

    def changelight(self, object):
        root = self.terrain.getRoot()
        v = self.att_directionalLight.att_direction.vec
        root.setShaderInput('lightvec', Vec4(v[0].v,v[1].v,v[2].v,1))
        root.setShaderInput('lightcolor', self.att_directionalLight.att_lightcolor.color)
        root.setShaderInput('ambientlight', self.att_ambientLight.att_lightcolor.color)

    def cameraUpdated(self, task):
        campos = base.camera.getPos()
        self.att_skybox.setPos(campos)
        return Task.cont

    def LoadSkyBox(self):
        self.att_skybox = SkyDome1(render)
        self.att_skybox.setStandardControl()
        base.cam.node().getLens( ).setNear( 1 )
        base.cam.node().getLens( ).setFar( 5000 )

    def LoadModels(self):
        self.LoadTerrain()

    def LoadTerrain(self):
        if self.terrain != None:
            self.terrain.Destroy()

        self.terrain = myGeoMipTerrain("mySimpleTerrain")

        # Set terrain properties
        self.terrain.setBlockSize(32)
        self.terrain.setFactor(100)
        self.terrain.setFocalPoint(base.camera)

        root = self.terrain.getRoot()
        root.reparentTo(render)
        root.setSz(30)    # z (up) scale

        # Generate it.
        self.terrain.generate()

        # texture
        self.setMultiTexture(None)

    def setMultiTexture(self, object):
        #self.LoadModels()
        #self.changelight(None)

        if self.att_multitexture.v:
            self.terrain.setMultiTexture()
        else:
            self.terrain.setMonoTexture()
        self.setTag()

    def ClearScene(self):
        self.att_skybox.Destroy()

        self.textnode.removeNode()
        if self.terrain:
            self.terrain.Destroy()
        self.att_cameracontrol.Destroy()
        base.camera.detachNode()
        #render.clearShaderInput('light')
        self.DestroyAllLights()
        render.removeChildren()
        base.camera.reparentTo(render)
        taskMgr.remove("camupdate")

    def _setup_camera(self):

        cam = base.cam.node()
        cam.getLens().setNear(1)
        cam.getLens().setFar(5000)

        saF = ShaderAttrib.make( )
        saF = saF.setShader(loader.loadShader('shaders/splut3NormalFog.sha'))
        #cam.setTagStateKey('Fog')
        #cam.setTagState('True', RenderState.make(saF))

        sa = ShaderAttrib.make( )
        sa = sa.setShader(loader.loadShader('shaders/splut3Normal.sha'))
        cam.setTagStateKey('Normal')
        cam.setTagState('True', RenderState.make(sa))
        cam.setTagState('Fog', RenderState.make(saF))



    def setTag(self):
        root = self.terrain.getRoot()
        if self.att_multitexture.v:
            if self.att_fogEnable.v:
                root.setShaderInput('fogDensity', self.att_fogdensity.v, 0, 0, 0)
                root.setShaderInput('fogColor', self.att_fogcolor.getColor())
                root.setTag( 'Normal', 'Fog' )
            else:
                root.setTag( 'Normal', 'True' )
        else:
            root.clearTag('Normal')
            #root.clearTag('Clipped')
        root.setTag( 'Clipped', 'True' )

    def fogChange(self, object):
        self.setTag()



class myGeoMipTerrain(GeoMipTerrain):
    def __init__(self, name):
        GeoMipTerrain.__init__(self, name)
        self.setHeightfield(Filename('demo_terrain/models/land01-map.png'))
        taskMgr.add(self.update, "terrainupdate")
        self.fEnable = True
##
##        # Set terrain properties
##        self.setBlockSize(32)
##        self.setFactor(100)
##        self.setFocalPoint(base.camera)

    def Destroy(self):
        if not self.fEnable:
            return
        self.fEnable = False
        root = self.getRoot()
#        root.clearTag( 'Normal')
#        root.clearTag( 'Clipped')
        #self.getRoot().clearShaderInput('tscale')
##        self.getRoot().clearShaderInput('tscale')
##        self.getRoot().clearShaderInput('lightvec')
##        self.getRoot().clearShaderInput('lightcolor')
##        self.getRoot().clearShaderInput('ambientlight')
        #root.clearTexture()
        root.removeNode()
        taskMgr.remove("terrainupdate")


    def update(self, task):
        GeoMipTerrain.update(self)
        #return task.cont

    def setMonoTexture(self):
        root = self.getRoot()
        root.clearTexture()

        ts = TextureStage('ts')
        tex = loader.loadTexture('textures/land01_tx_512.png')
        root.setTexture(ts, tex)

    def setMultiTexture(self):
        root = self.getRoot()
        root.clearTexture()
        # root.setShader(loader.loadShader('shaders/splut3.sha'))
        root.setShaderInput('tscale', Vec4(16.0, 16.0, 16.0, 1.0))    # texture scaling

        tex1 = loader.loadTexture('textures/grass_ground2.jpg')
        #tex1.setMinfilter(Texture.FTLinearMipmapLinear)
        tex1.setMinfilter(Texture.FTNearestMipmapLinear)
        tex1.setMagfilter(Texture.FTLinear)
        tex2 = loader.loadTexture('textures/rock_02.jpg')
        tex2.setMinfilter(Texture.FTNearestMipmapLinear)
        tex2.setMagfilter(Texture.FTLinear)
        tex3 = loader.loadTexture('textures/sable_et_gravier.jpg')
        tex3.setMinfilter(Texture.FTNearestMipmapLinear)
        tex3.setMagfilter(Texture.FTLinear)

        alp1 = loader.loadTexture('textures/land01_Alpha_1.png')
        alp2 = loader.loadTexture('textures/land01_Alpha_2.png')
        alp3 = loader.loadTexture('textures/land01_Alpha_3.png')

        ts = TextureStage('tex1')    # stage 0
        root.setTexture(ts, tex1)
        ts = TextureStage('tex2')    # stage 1
        root.setTexture(ts, tex2)
        ts = TextureStage('tex3')    # stage 2
        root.setTexture(ts, tex3)

        ts = TextureStage('alp1')    # stage 3
        root.setTexture(ts, alp1)
        ts = TextureStage('alp2')    # stage 4
        root.setTexture(ts, alp2)
        ts = TextureStage('alp3')    # stage 5
        root.setTexture(ts, alp3)

        # enable use of the two separate tagged render states for our two cameras
        #root.setTag( 'Normal', 'True' )
        #self.att_fog = demobase.Att_exponentialFog(False, "Exponential Fog", Vec4(0,0,0,1), 0.08)
        #root.setShaderInput('fogDensity', 0.01, 0, 0, 0)
        #root.setShaderInput('fogColor', Vec4(0.4,0.4,0.4,1))
        #root.setShaderInput('alight0', self.att_ambientLight.light)
        #root.setTag( 'Fog', 'True' )
        #root.setTag( 'Normal', 'Fog' )

