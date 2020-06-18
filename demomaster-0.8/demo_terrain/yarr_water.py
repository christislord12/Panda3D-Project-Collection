
from random import randint, random
import math, sys, colorsys, threading
from math import pi, sin
import demobase, camerabase, yarr, waterplane1

from pandac.PandaModules import GeoMipTerrain, Filename
from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
#from pandac.PandaModules import Plane, CardMaker
#from pandac.PandaModules import PlaneNode
#from pandac.PandaModules import PStatClient
#from pandac.PandaModules import CullFaceAttrib
#from pandac.PandaModules import RenderState
#from pandac.PandaModules import ShaderAttrib, TransparencyAttrib

####################################################################################################################
class TerrainWaterDemo(yarr.TerrainDemo):
    """
    GeoMipTerrain - Yarr with water
    It is all from Yarr
    """
    def __init__(self, parent):
        yarr.TerrainDemo.__init__(self, parent)

        self._water_level = Vec4(0.0, 0.0, 12.0, 1.0)

    def LoadModels(self):
        yarr.TerrainDemo.LoadModels(self)
        self.att_water = waterplane1.WaterNode(-128,-128,128,128, self._water_level.getZ())
        self.att_water.setStandardControl()
        self.att_water.changeParams(None)

        wl=self._water_level
        wl.setZ(wl.getZ()-0.05)    # add some leeway (gets rid of some mirroring artifacts)
        root = self.terrain.getRoot()
        root.setShaderInput('waterlevel', self._water_level)

        render.setShaderInput('time', 0)

        self.att_cameracontrol.setNotifier(self.camchanged)

    def cameraUpdated(self, task):
        pos = base.camera.getPos()
        render.setShaderInput('time', task.time)
        # update matrix of the reflection camera
        mc = base.camera.getMat( )
        self.att_water.changeCameraPos(pos,mc)

        return yarr.TerrainDemo.cameraUpdated(self, task)
        #return task.cont

    def camchanged(self, object):
        self.att_water.setFov(self.att_cameracontrol.att_fov.v)

    def ClearScene(self):
        self.att_water.Destroy()
        yarr.TerrainDemo.ClearScene(self)

##
##class WaterNode():
##    def __init__(self, x1, y1, x2, y2, z):
##        # Water surface
##        maker = CardMaker( 'water' )
##        maker.setFrame( x1, x2, y1, y2 )
##
##        self.waterNP = render.attachNewNode(maker.generate())
##        self.waterNP.setHpr(0,-90,0)
##        self.waterNP.setPos(0,0,z)
##        self.waterNP.setTransparency(TransparencyAttrib.MAlpha )
##        self.waterNP.setShader(loader.loadShader( 'shaders/water.sha' ))
##        self.waterNP.setShaderInput('wateranim', Vec4( 0.03, -0.015, 64.0, 0 )) # vx, vy, scale, skip
##        # offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
##        self.waterNP.setShaderInput('waterdistort', Vec4( 0.4, 4.0, 0.4, 0.45 ))
##
##        # Reflection plane
##        self.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )
##
##        planeNode = PlaneNode( 'waterPlane' )
##        planeNode.setPlane( self.waterPlane )
##
##        # Buffer and reflection camera
##        self.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
##        self.buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )
##
##        cfa = CullFaceAttrib.makeReverse( )
##        rs = RenderState.make(cfa)
##
##        self.watercamNP = base.makeCamera( self.buffer )
##        self.watercamNP.reparentTo(render)
##
##        sa = ShaderAttrib.make()
##        sa = sa.setShader(loader.loadShader('shaders/splut3Clipped.sha') )
##
##        self.cam = self.watercamNP.node()
##        self.cam.getLens( ).setFov( base.camLens.getFov( ) )
##        self.cam.getLens().setNear(1)
##        self.cam.getLens().setFar(5000)
##        self.cam.setInitialState( rs )
##        self.cam.setTagStateKey('Clipped')
##        self.cam.setTagState('True', RenderState.make(sa))
##
##
##        # ---- water textures ---------------------------------------------
##
##        # reflection texture, created in realtime by the 'water camera'
##        tex0 = self.buffer.getTexture( )
##        tex0.setWrapU(Texture.WMClamp)
##        tex0.setWrapV(Texture.WMClamp)
##        ts0 = TextureStage( 'reflection' )
##        self.waterNP.setTexture( ts0, tex0 )
##
##        # distortion texture
##        tex1 = loader.loadTexture('textures/water.png')
##        ts1 = TextureStage('distortion')
##        self.waterNP.setTexture(ts1, tex1)
##
##
##    def Destroy(self):
##        self.cam.setInitialState(RenderState.makeEmpty())
##        self.watercamNP.removeNode()
##        #self.waterNP.clearTexture()
##        self.waterNP.removeNode()
##
