import demobase

from pandac.PandaModules import Filename, CardMaker
from pandac.PandaModules import NodePath, WindowProperties,TextureStage, Texture
from pandac.PandaModules import Vec3,Vec4,Point3
from pandac.PandaModules import Plane
from pandac.PandaModules import PlaneNode
from pandac.PandaModules import PStatClient
from pandac.PandaModules import CullFaceAttrib
from pandac.PandaModules import RenderState
from pandac.PandaModules import ShaderAttrib, TransparencyAttrib


class WaterNode(demobase.Att_base):
    def __init__(self, x1, y1, x2, y2, z):
        demobase.Att_base.__init__(self, False, "Water1")
        # Water surface
        maker = CardMaker( 'water' )
        maker.setFrame( x1, x2, y1, y2 )

        self.waterNP = render.attachNewNode(maker.generate())
        self.waterNP.setHpr(0,-90,0)
        self.waterNP.setPos(0,0,z)
        self.waterNP.setTransparency(TransparencyAttrib.MAlpha )
        self.waterNP.setShader(loader.loadShader( 'shaders/water1.sha' ))
        # offset, strength, refraction factor (0=perfect mirror, 1=total refraction), refractivity
        #self.waterNP.setShaderInput('waterdistort', Vec4( 0.4, 4.0, 0.4, 0.45 ))

        #self.bottomNP = render.attachNewNode(maker.generate())
        #self.bottomNP.setHpr(0,-90,0)
        #self.bottomNP.setPos(0,0,z-0.01)
        #self.bottomNP.setColor(0,0,1,1)

        # Reflection plane
        self.waterPlane = Plane( Vec3( 0, 0, z+1 ), Point3( 0, 0, z ) )

        planeNode = PlaneNode( 'waterPlane' )
        planeNode.setPlane( self.waterPlane )

        # Buffer and reflection camera
        self.buffer = base.win.makeTextureBuffer( 'waterBuffer', 512, 512 )
        self.buffer.setClearColor( Vec4( 0, 0, 0, 1 ) )

        cfa = CullFaceAttrib.makeReverse( )
        rs = RenderState.make(cfa)

        self.watercamNP = base.makeCamera( self.buffer )
        self.watercamNP.reparentTo(render)

        sa = ShaderAttrib.make()
        sa = sa.setShader(loader.loadShader('shaders/splut3Clipped.sha') )

        self.cam = self.watercamNP.node()
        self.cam.getLens( ).setFov( base.camLens.getFov( ) )
        self.cam.getLens().setNear(1)
        self.cam.getLens().setFar(5000)
        self.cam.setInitialState( rs )
        self.cam.setTagStateKey('Clipped')
        self.cam.setTagState('True', RenderState.make(sa))


        # ---- water textures ---------------------------------------------

        # reflection texture, created in realtime by the 'water camera'
        tex0 = self.buffer.getTexture( )
        tex0.setWrapU(Texture.WMClamp)
        tex0.setWrapV(Texture.WMClamp)
        ts0 = TextureStage( 'reflection' )
        self.waterNP.setTexture( ts0, tex0 )

        # distortion texture
        tex1 = loader.loadTexture('textures/water.png')
        #tex1 = loader.loadTexture('textures/waves200.tga')
        ts1 = TextureStage('distortion')
        self.waterNP.setTexture(ts1, tex1)


    def Destroy(self):
        base.graphicsEngine.removeWindow(self.buffer)
        self.cam.setInitialState(RenderState.makeEmpty())
        self.watercamNP.removeNode()
        self.waterNP.clearShader()
        #self.bottomNP.removeNode()
        self.waterNP.removeNode()

    #def setColor(self, color):
    #    self.bottomNP.setColor(color)

    def setParams(self, offset, strength, refractionfactor, refractivity, vx, vy, scale):
        self.waterNP.setShaderInput('waterdistort', Vec4( offset, strength, refractionfactor, refractivity ))
        self.waterNP.setShaderInput('wateranim', Vec4( vx, vy, scale, 0 )) # vx, vy, scale, skip

    def changeCameraPos(self, pos, mc=None):
        if mc != None:
            # update matrix of the reflection camera
            mf = self.waterPlane.getReflectionMat( )
            self.watercamNP.setMat(mc * mf)

    def changeParams(self, object):
        self.setParams(self.att_offset.v,self.att_strength.v,self.att_refractionfactor.v,self.att_refractivity.v,
                self.att_vx.v, self.att_vy.v, self.att_scale.v)

    def setStandardControl(self):
        self.att_offset = demobase.Att_FloatRange(False, "Water:Offset", 0.0, 1.0, 0.4)
        self.att_strength = demobase.Att_FloatRange(False, "Water:Strength", 0.0, 100.0, 4)
        self.att_refractionfactor = demobase.Att_FloatRange(False, "Water:Refraction Factor", 0.0, 1.0, 0.2)
        self.att_refractivity = demobase.Att_FloatRange(False, "Water:Refractivity", 0.0, 1.0, 0.45)
        self.att_vx = demobase.Att_FloatRange(False, "Water:Speed X", -1.0, 1.0, 0.1)
        self.att_vy = demobase.Att_FloatRange(False, "Water:Speed Y", -1.0, 1.0, -0.1)
        self.att_scale = demobase.Att_FloatRange(False, "Water:Scale", 1.0, 200.0, 64.0,0)
        self.att_offset.setNotifier(self.changeParams)
        self.att_strength.setNotifier(self.changeParams)
        self.att_refractionfactor.setNotifier(self.changeParams)
        self.att_refractivity.setNotifier(self.changeParams)
        self.att_vx.setNotifier(self.changeParams)
        self.att_vy.setNotifier(self.changeParams)
        self.att_scale.setNotifier(self.changeParams)
        self.changeParams(None)


    def hide(self):
        self.waterNP.hide()

    def show(self):
        self.waterNP.show()

    def setFov(self, fov):
        # the reflection cam has to follow the base.cam fov
        self.cam.getLens().setFov(fov)

    def setCubeMap(self, cubemapfile):
        pass
